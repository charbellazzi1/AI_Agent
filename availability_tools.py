# availability_tools.py
# pip install supabase>=2.4.0 python-dateutil
# Env:
#   SUPABASE_URL / SUPABASE_SERVICE_KEY  (optional, preferred on backend)
#   EXPO_PUBLIC_SUPABASE_URL / EXPO_PUBLIC_SUPABASE_ANON_KEY (fallback)
#   AVAILABILITY_TZ=Asia/Beirut (default)

import os
import sys
import traceback
from dataclasses import dataclass
from datetime import datetime, date as date_cls, timedelta
from typing import Any, Dict, List, Optional

from dateutil import tz
from supabase import create_client, Client

# Timezone handling
_LOCAL_TZ = tz.gettz(os.getenv("AVAILABILITY_TZ", "Asia/Beirut")) or tz.UTC

@dataclass
class Table:
	id: str
	table_number: str
	capacity: int
	min_capacity: int
	max_capacity: int
	table_type: str
	is_combinable: bool
	priority_score: int

_SUPABASE: Optional[Client] = None

def _get_supabase() -> Client:
	global _SUPABASE
	if _SUPABASE is not None:
		return _SUPABASE
	url = os.environ.get("SUPABASE_URL") or os.environ.get("EXPO_PUBLIC_SUPABASE_URL") or os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
	key = os.environ.get("SUPABASE_SERVICE_KEY") or os.environ.get("EXPO_PUBLIC_SUPABASE_ANON_KEY") or os.environ.get("NEXT_PUBLIC_SUPABASE_ANON_KEY")
	if not (url and key):
		raise RuntimeError("Supabase credentials missing")
	_SUPABASE = create_client(url, key)
	return _SUPABASE

def _parse_date(d: Any) -> date_cls:
	if isinstance(d, date_cls) and not isinstance(d, datetime):
		return d
	if isinstance(d, str):
		return datetime.strptime(d, "%Y-%m-%d").date()
	if isinstance(d, datetime):
		return d.date()
	raise ValueError("date must be a datetime.date or 'YYYY-MM-DD' string")

def _normalize_time_str(t: str) -> str:
	parts = t.split(":")
	if len(parts) >= 2:
		return f"{parts[0].zfill(2)}:{parts[1].zfill(2)}"
	raise ValueError("time must be 'HH:MM' or 'HH:MM:SS'")

def _combine_local(dt_date: date_cls, hhmm: str) -> datetime:
	h, m = [int(x) for x in _normalize_time_str(hhmm).split(":")]
	# Local-aware datetime (restaurant hours are local)
	return datetime(dt_date.year, dt_date.month, dt_date.day, h, m, 0, tzinfo=_LOCAL_TZ)

def _to_utc_iso(dt_local: datetime) -> str:
	return dt_local.astimezone(tz.UTC).isoformat()

def _day_of_week_str(d: date_cls) -> str:
	return d.strftime("%A").lower()

def _default_turn_time(party_size: int) -> int:
	if party_size <= 2:
		return 90
	if party_size <= 4:
		return 120
	if party_size <= 6:
		return 150
	if party_size <= 8:
		return 180
	if party_size <= 10:
		return 210
	return 240

def _log_exception(context: str) -> None:
	print(f"[availability_tools] ERROR in {context}:", file=sys.stderr)
	traceback.print_exc()

def _get_restaurant_config(sb: Client, restaurant_id: str) -> Dict[str, Any]:
	try:
		cfg: Dict[str, Any] = {"booking_window_days": 30, "regularHours": [], "specialHours": [], "closures": []}

		r1 = (
			sb.table("restaurants")
			.select("booking_window_days")
			.eq("id", restaurant_id)
			.single()
			.execute()
		)
		if r1 and getattr(r1, "data", None):
			bwd = r1.data.get("booking_window_days")
			if isinstance(bwd, int):
				cfg["booking_window_days"] = bwd

		hours = (
			sb.table("restaurant_hours")
			.select("*")
			.eq("restaurant_id", restaurant_id)
			.order("day_of_week")
			.execute()
		)
		if hours and isinstance(hours.data, list):
			cfg["regularHours"] = hours.data

		special = (
			sb.table("restaurant_special_hours")
			.select("*")
			.eq("restaurant_id", restaurant_id)
			.order("date")
			.execute()
		)
		if special and isinstance(special.data, list):
			cfg["specialHours"] = special.data

		closures = (
			sb.table("restaurant_closures")
			.select("*")
			.eq("restaurant_id", restaurant_id)
			.order("start_date")
			.execute()
		)
		if closures and isinstance(closures.data, list):
			cfg["closures"] = closures.data

		return cfg
	except Exception:
		_log_exception("_get_restaurant_config")
		return {"booking_window_days": 30, "regularHours": [], "specialHours": [], "closures": []}

def _get_operating_hours_for_date(cfg: Dict[str, Any], d: date_cls) -> Dict[str, Any]:
	date_str = d.strftime("%Y-%m-%d")
	day = _day_of_week_str(d)

	for c in cfg.get("closures", []) or []:
		if c.get("start_date") <= date_str <= c.get("end_date"):
			return {"shifts": [], "isClosed": True}

	for s in cfg.get("specialHours", []) or []:
		if s.get("date") == date_str:
			if s.get("is_closed"):
				return {"shifts": [], "isClosed": True}
			return {"shifts": [{"openTime": s.get("open_time") or "11:00", "closeTime": s.get("close_time") or "22:00"}], "isClosed": False}

	reg = [h for h in (cfg.get("regularHours") or []) if h.get("day_of_week") == day and h.get("is_open")]
	shifts = []
	for h in reg:
		if h.get("open_time") and h.get("close_time"):
			shifts.append({"openTime": h["open_time"], "closeTime": h["close_time"]})
	shifts.sort(key=lambda s: s["openTime"])
	return {"shifts": shifts, "isClosed": len(shifts) == 0}

def _get_turn_time_for_party(sb: Client, restaurant_id: str, party_size: int, booking_dt_local: datetime) -> int:
	try:
		res = sb.rpc(
			"get_turn_time",
			{"p_restaurant_id": restaurant_id, "p_party_size": int(party_size), "p_booking_time": _to_utc_iso(booking_dt_local)},
		).execute()
		if res and res.data is not None:
			return int(res.data)
		return _default_turn_time(int(party_size))
	except Exception:
		_log_exception("_get_turn_time_for_party")
		return _default_turn_time(int(party_size))

def _generate_15_minute_slots(sb: Client, restaurant_id: str, d: date_cls, open_time: str, close_time: str, party_size: int) -> List[str]:
	slots: List[str] = []
	try:
		open_h, open_m = [int(x) for x in _normalize_time_str(open_time).split(":")]
		close_h, close_m = [int(x) for x in _normalize_time_str(close_time).split(":")]

		probe_dt_local = datetime(d.year, d.month, d.day, open_h, open_m, tzinfo=_LOCAL_TZ)
		buffer_minutes = _get_turn_time_for_party(sb, restaurant_id, int(party_size), probe_dt_local)

		open_total = open_h * 60 + open_m
		close_total = close_h * 60 + close_m

		if open_m % 15 != 0:
			open_total = open_h * 60 + ((open_m + 14) // 15) * 15

		minutes = open_total
		while minutes <= close_total - buffer_minutes:
			h, m = divmod(minutes, 60)
			slots.append(f"{str(h).zfill(2)}:{str(m).zfill(2)}")
			minutes += 15
	except Exception:
		_log_exception("_generate_15_minute_slots")
	return slots

def _quick_combination_check(sb: Client, restaurant_id: str, start_dt_local: datetime, end_dt_local: datetime, party_size: int) -> bool:
	try:
		res = (
			sb.table("restaurant_tables")
			.select("id,capacity")
			.eq("restaurant_id", restaurant_id)
			.eq("is_active", True)
			.eq("is_combinable", True)
			.order("capacity", desc=True)
			.execute()
		)
		tables = res.data or []
		if len(tables) < 2:
			return False

		selected: List[Dict[str, Any]] = []
		running = 0
		for t in tables:
			if running >= int(party_size):
				break
			selected.append(t)
			running += int(t["capacity"])

		if running < int(party_size):
			return False

		table_ids = [t["id"] for t in selected]
		overlap = sb.rpc(
			"check_booking_overlap",
			{"p_table_ids": table_ids, "p_start_time": _to_utc_iso(start_dt_local), "p_end_time": _to_utc_iso(end_dt_local)},
		).execute()
		return overlap.data in (None, "")
	except Exception:
		_log_exception("_quick_combination_check")
		return False

def _quick_availability_check(sb: Client, restaurant_id: str, start_dt_local: datetime, end_dt_local: datetime, party_size: int) -> bool:
	try:
		if int(party_size) > 6 and _quick_combination_check(sb, restaurant_id, start_dt_local, end_dt_local, int(party_size)):
			return True

		res = sb.rpc(
			"quick_availability_check",
			{"p_restaurant_id": restaurant_id, "p_start_time": _to_utc_iso(start_dt_local), "p_end_time": _to_utc_iso(end_dt_local), "p_party_size": int(party_size)},
		).execute()
		if isinstance(getattr(res, "data", None), bool) and res.data:
			return True

		res2 = sb.rpc(
			"get_available_tables",
			{"p_restaurant_id": restaurant_id, "p_start_time": _to_utc_iso(start_dt_local), "p_end_time": _to_utc_iso(end_dt_local), "p_party_size": int(party_size)},
		).execute()
		data = getattr(res2, "data", None) or []
		if isinstance(data, list) and len(data) > 0:
			return True

		if int(party_size) > 2 and _quick_combination_check(sb, restaurant_id, start_dt_local, end_dt_local, int(party_size)):
			return True

		return False
	except Exception:
		_log_exception("_quick_availability_check")
		return False

def get_available_time_slots(restaurant_id: str, date: Any, party_size: int, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
	try:
		sb = _get_supabase()
		d = _parse_date(date)
		party_size = int(party_size)

		cfg = _get_restaurant_config(sb, restaurant_id)

		today_local = datetime.now(_LOCAL_TZ).date()
		days_diff = (d - today_local).days
		max_days = int(cfg.get("booking_window_days") or 30)

		if user_id:
			try:
				vip = (
					sb.table("restaurant_vip_users")
					.select("extended_booking_days")
					.eq("restaurant_id", restaurant_id)
					.eq("user_id", user_id)
					.gte("valid_until", datetime.utcnow().isoformat())
					.single()
					.execute()
				)
				if vip and getattr(vip, "data", None) and vip.data.get("extended_booking_days"):
					max_days = int(vip.data["extended_booking_days"])
			except Exception:
				_log_exception("VIP lookup")

		if days_diff > max_days:
			return []

		oh = _get_operating_hours_for_date(cfg, d)
		if oh["isClosed"] or len(oh["shifts"]) == 0:
			return []

		base: List[str] = []
		for shift in oh["shifts"]:
			base.extend(_generate_15_minute_slots(sb, restaurant_id, d, shift["openTime"], shift["closeTime"], party_size))
		unique_slots = sorted(list({t for t in base}))

		results: List[Dict[str, Any]] = []
		turn_time_for_slot: Optional[int] = None
		now_local = datetime.now(_LOCAL_TZ)

		for hhmm in unique_slots:
			start_dt_local = _combine_local(d, hhmm)
			if start_dt_local < now_local:
				continue
			if turn_time_for_slot is None:
				turn_time_for_slot = _get_turn_time_for_party(sb, restaurant_id, party_size, start_dt_local)
			end_dt_local = start_dt_local + timedelta(minutes=turn_time_for_slot)

			if _quick_availability_check(sb, restaurant_id, start_dt_local, end_dt_local, party_size):
				results.append({"time": hhmm, "available": True})

		return results
	except Exception:
		_log_exception("get_available_time_slots")
		return []

def get_table_options_for_slot(restaurant_id: str, date: Any, time_hhmm: str, party_size: int) -> Optional[Dict[str, Any]]:
	try:
		sb = _get_supabase()
		d = _parse_date(date)
		party_size = int(party_size)

		start_dt_local = _combine_local(d, time_hhmm)
		turn_time = _get_turn_time_for_party(sb, restaurant_id, party_size, start_dt_local)
		end_dt_local = start_dt_local + timedelta(minutes=turn_time)

		res = sb.rpc(
			"get_available_tables",
			{"p_restaurant_id": restaurant_id, "p_start_time": _to_utc_iso(start_dt_local), "p_end_time": _to_utc_iso(end_dt_local), "p_party_size": party_size},
		).execute()

		rows = [r for r in (getattr(res, "data", None) or []) if r.get("table_id") and r.get("table_number") and r.get("capacity")]
		tables: List[Table] = [
			Table(
				id=row["table_id"],
				table_number=row["table_number"],
				capacity=int(row["capacity"]),
				min_capacity=int(row.get("min_capacity") or 0),
				max_capacity=int(row.get("max_capacity") or row["capacity"]),
				table_type=row.get("table_type") or "standard",
				is_combinable=bool(row.get("is_combinable")),
				priority_score=int(row.get("priority_score") or 0),
			)
			for row in rows
		]

		if len(tables) == 0 and party_size > 2:
			if _quick_combination_check(sb, restaurant_id, start_dt_local, end_dt_local, party_size):
				comb = (
					sb.table("restaurant_tables")
					.select("id,table_number,capacity,min_capacity,max_capacity,table_type,is_combinable,priority_score")
					.eq("restaurant_id", restaurant_id)
					.eq("is_active", True)
					.eq("is_combinable", True)
					.order("capacity", desc=True)
					.execute()
				)
				picked: List[Table] = []
				cap = 0
				for t in (comb.data or []):
					if cap >= party_size:
						break
					picked.append(
						Table(
							id=t["id"],
							table_number=t.get("table_number", ""),
							capacity=int(t["capacity"]),
							min_capacity=int(t.get("min_capacity") or 0),
							max_capacity=int(t.get("max_capacity") or t["capacity"]),
							table_type=t.get("table_type") or "standard",
							is_combinable=bool(t.get("is_combinable")),
							priority_score=int(t.get("priority_score") or 0),
						)
					)
					cap += int(t["capacity"])

				if picked:
					total_capacity = sum(t.capacity for t in picked)
					option = {
						"tables": [t.__dict__ for t in picked],
						"requiresCombination": True,
						"totalCapacity": total_capacity,
						"tableTypes": list({t.table_type for t in picked}),
						"experienceTitle": "Group Arrangement" if len(picked) > 2 else "Private Group Arrangement",
						"experienceDescription": f"{len(picked)} tables arranged together for {party_size}",
						"isPerfectFit": total_capacity >= party_size and total_capacity <= party_size + 2,
					}
					return {"time": _normalize_time_str(time_hhmm), "options": [option], "primaryOption": option}
			return None

		if len(tables) == 0:
			return None

		tables_sorted = sorted(tables, key=lambda t: (abs(t.capacity - party_size), -t.priority_score))
		options: List[Dict[str, Any]] = []
		for t in tables_sorted:
			if t.capacity >= party_size:
				options.append(
					{
						"tables": [t.__dict__],
						"requiresCombination": False,
						"totalCapacity": t.capacity,
						"tableTypes": [t.table_type],
						"experienceTitle": "Classic Dining",
						"experienceDescription": "Prime dining room seating",
						"isPerfectFit": t.capacity == party_size,
					}
				)

		if not options:
			return None

		primary = options[0]
		return {"time": _normalize_time_str(time_hhmm), "options": options, "primaryOption": primary}
	except Exception:
		_log_exception("get_table_options_for_slot")
		return None

def check_any_time_slots(restaurant_id: str, date: Any, party_size: int, user_id: Optional[str] = None) -> bool:
	try:
		return len(get_available_time_slots(restaurant_id, date, int(party_size), user_id)) > 0
	except Exception:
		_log_exception("check_any_time_slots")
		return False

def search_time_range(restaurant_id: str, date: Any, start_time: str, end_time: str, party_size: int, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
	try:
		all_slots = get_available_time_slots(restaurant_id, date, int(party_size), user_id)
		s_norm = _normalize_time_str(start_time)
		e_norm = _normalize_time_str(end_time)
		in_range = [s for s in all_slots if s["available"] and s_norm <= s["time"] <= e_norm]

		d = _parse_date(date)
		results: List[Dict[str, Any]] = []
		for s in in_range:
			opts = get_table_options_for_slot(restaurant_id, d, s["time"], int(party_size))
			if not opts:
				continue
			primary = opts["primaryOption"]
			results.append(
				{
					"timeSlot": s["time"],
					"tables": primary.get("tables", []),
					"tableOptions": opts.get("options", []),
					"matchingTypes": primary.get("tableTypes", []),
					"totalCapacity": primary.get("totalCapacity", 0),
					"requiresCombination": primary.get("requiresCombination", False),
				}
			)

		results.sort(key=lambda r: r["timeSlot"])
		return results
	except Exception:
		_log_exception("search_time_range")
		return []

# CamelCase aliases for your agent’s tool names
checkAnyTimeSlots = check_any_time_slots
getAvailableTimeSlots = get_available_time_slots
getTableOptionsForSlot = get_table_options_for_slot
searchTimeRange = search_time_range