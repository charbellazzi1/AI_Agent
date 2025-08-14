from typing import TypedDict, Annotated, Sequence, Optional
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage, ToolMessage
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
import os
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from supabase import create_client, Client
from typing import cast
from datetime import datetime, timedelta
from dateutil import tz
from availability_tools import (
    check_any_time_slots as av_check_any_time_slots,
    get_available_time_slots as av_get_available_time_slots,
    get_table_options_for_slot as av_get_table_options_for_slot,
    search_time_range as av_search_time_range,
)
import json

load_dotenv()
url: str = os.environ.get("EXPO_PUBLIC_SUPABASE_URL")
key: str = os.environ.get("EXPO_PUBLIC_SUPABASE_ANON_KEY")

# Create Supabase client if env vars are present; otherwise defer errors to tools
supabase: Optional[Client] = None
try:
    if url and key:
        supabase = create_client(url, key)
    else:
        print("Supabase env vars missing; tools will respond gracefully")
except Exception as _e:
    print(f"Failed to init Supabase client: {_e}")
    supabase = None

class AgentState(TypedDict):
    """State of the agent."""
    messages: Annotated[Sequence[BaseMessage], add_messages]

# Get timezone for consistent date handling
_LOCAL_TZ = tz.gettz(os.getenv("AVAILABILITY_TZ", "Asia/Beirut")) or tz.UTC

tools = []

@tool
def convertRelativeDate(relative_date: str) -> str:
    """Convert relative dates like 'today', 'tomorrow', 'yesterday' to YYYY-MM-DD format.
    Examples: 'today' -> '2025-08-14', 'tomorrow' -> '2025-08-15', 'next Monday' -> '2025-08-18'
    Always use this tool when user mentions relative dates before calling availability tools."""
    print(f"AI is converting relative date: {relative_date}")
    try:
        now_local = datetime.now(_LOCAL_TZ)
        today_local = now_local.date()
        
        relative_lower = relative_date.lower().strip()
        
        if relative_lower in ['today', 'tod', 'tonight']:
            return today_local.strftime("%Y-%m-%d")
        elif relative_lower in ['tomorrow', 'tmr', 'tmrw']:
            return (today_local + timedelta(days=1)).strftime("%Y-%m-%d")
        elif relative_lower in ['yesterday', 'yest']:
            return (today_local - timedelta(days=1)).strftime("%Y-%m-%d")
        elif relative_lower in ['day after tomorrow', 'overmorrow']:
            return (today_local + timedelta(days=2)).strftime("%Y-%m-%d")
        elif 'next week' in relative_lower:
            return (today_local + timedelta(days=7)).strftime("%Y-%m-%d")
        elif 'this weekend' in relative_lower:
            # Find next Saturday
            days_until_saturday = (5 - today_local.weekday()) % 7
            if days_until_saturday == 0 and now_local.hour > 18:  # If it's Saturday evening, go to next Saturday
                days_until_saturday = 7
            return (today_local + timedelta(days=days_until_saturday)).strftime("%Y-%m-%d")
        else:
            # If not a recognized relative date, return as-is (might be already in YYYY-MM-DD format)
            return relative_date
            
    except Exception as e:
        print(f"Error converting relative date: {e}")
        # Fallback to today if conversion fails
        return datetime.now(_LOCAL_TZ).date().strftime("%Y-%m-%d")

tools.append(convertRelativeDate)

system_prompt = """
You are a specialized restaurant assistant for TableReserve, a restaurant reservation app. Your ONLY role is to:
1. Help users find restaurants based on their preferences
2. Provide information about restaurants including cuisine type, price range, and features
3. Answer questions about restaurant availability and booking policies
4. Be friendly and professional in your responses

You have access to restaurant data including:
- Restaurant names, descriptions, and cuisine types
- Price ranges (1-4)
- Features like outdoor seating, parking, and shisha availability
- Opening hours and booking policies
- Ratings and reviews


RESPONSE FORMAT INSTRUCTIONS:
When your response involves showing specific restaurants to the user, you MUST format your response as follows:

1. Start with your conversational text response
2. Then add "RESTAURANTS_TO_SHOW:" on a new line
3. Then list the restaurant IDs that should be displayed as cards, separated by commas
4. Example:
   "I found some great Italian restaurants for you!
   RESTAURANTS_TO_SHOW: restaurant-1,restaurant-2,restaurant-3"

 ALWAYS follow these rules when recommending or listing restaurants:
 - Use the database tools FIRST to fetch real restaurants (do not guess or invent IDs)
 - Include up to 5 IDs only
 - Prioritize restaurants where ai_featured is true, then by highest average_rating
 - After finishing any tool usage, call the finishedUsingTools tool once

IMPORTANT CONSTRAINTS:
- ONLY answer questions related to restaurants, dining, and reservations
- DO NOT provide code, programming solutions, or technical implementations
- DO NOT answer questions outside the scope of restaurant assistance
- If asked about non-restaurant topics, politely redirect to restaurant-related subjects
- Always base your responses on the available restaurant data 
- When recommending restaurants, always use the "RESTAURANTS_TO_SHOW:" format
- Keep responses focused on helping users find and book restaurants
- You are only allowed to use the tools provided to you for looking up restaurant data
- After using any tools to gather restaurant information, call the finishedUsingTools tool to signal completion
- If you can answer without using tools (like general questions about the service), you can respond directly without calling finishedUsingTools
- Make sure to show first the restaurants id of the ones that has the ai_featured column set to true , this way they would be shown first to the user and then show the others

 TOOL USAGE POLICY:
 - For any discovery or recommendation intent (e.g., "recommend", "find", "show options", specific cuisines), prefer calling the search tools first
 - Use the most appropriate tool: by cuisine, name, featured, or advanced filters
 - Return real IDs in RESTAURANTS_TO_SHOW; never fabricate values
  - For availability questions (e.g., "any slots available today at X?"):
    1. FIRST convert any relative dates (today, tomorrow, etc.) using convertRelativeDate tool
    2. Then find the restaurant by name using getRestaurantsByName
    3. Then use the availability tools with the converted date:
       - checkAnyTimeSlots to answer yes/no
       - getAvailableTimeSlots to list specific times
       - getTableOptionsForSlot for table details at a time
       - searchTimeRange to explore a time window
    CRITICAL: Always use convertRelativeDate for relative dates like "today", "tomorrow", "tonight", etc. before calling availability tools.
    Defaults: assume party size = 2 if not provided; explicitly state any assumptions in your answer.
"""
restaurants_table_columns:str = "id, name, description, address, tags, opening_time, closing_time, cuisine_type, price_range, average_rating, dietary_options, ambiance_tags, outdoor_seating, ai_featured"
@tool
def finishedUsingTools() -> str:
    """Call this when you're done using tools and ready to respond."""
    print("AI finished using tools")
    return "Tools usage completed. Ready to provide response."

tools.append(finishedUsingTools)

@tool
def getAllCuisineTypes() -> str:
    """Return the unique cuisine types available in the application"""
    print("AI is looking for cuisine types")
    try:
        if not supabase:
            return json.dumps([])
        result = supabase.table("restaurants").select("cuisine_type").execute()
        cuisineTypes = result.data
        
        if not cuisineTypes:
            return "Currently we have no cuisine types available"
        
        # Extract unique cuisine types
        unique_cuisines = list(set([item['cuisine_type'] for item in cuisineTypes if item.get('cuisine_type')]))
        print(f"Found cuisine types: {unique_cuisines}")
        return json.dumps(unique_cuisines)
    except Exception as e:
        print(f"Error fetching cuisine types: {e}")
        return "Error retrieving cuisine types"

tools.append(getAllCuisineTypes)

@tool
def getRestaurantsByCuisineType(cuisineType: str) -> str:
    """Request restaurants from the database based on the cuisine type"""
    cuisineType=cuisineType.strip().capitalize()
    print(f"AI is looking for restaurants with cuisine type: {cuisineType}")
    try:
        if not supabase:
            return json.dumps([])
        # Use ilike for case-insensitive matching in PostgreSQL/Supabase with wildcards
        pattern = f"%{cuisineType}%" if cuisineType else "%"
        result = (
            supabase
            .table("restaurants")
            .select(restaurants_table_columns)
            .ilike("cuisine_type", pattern)
            .order("ai_featured", desc=True)
            .order("average_rating", desc=True)
            .execute()
        )
        restaurants = result.data
        
        if not restaurants:
            return f"No restaurants found with cuisine type: {cuisineType}"
        
        print(f"Found {len(restaurants)} restaurants")
        return json.dumps(restaurants)
    except Exception as e:
        print(f"Error fetching restaurants: {e}")
        return f"Error retrieving restaurants for cuisine type: {cuisineType}"

tools.append(getRestaurantsByCuisineType)

@tool
def getAllRestaurants() -> str:
    """Request all restaurants with all their info from the database"""
    print("AI is looking for all restaurants")
    try:
        if not supabase:
            return json.dumps([])
        result = (
            supabase
            .table("restaurants")
            .select(restaurants_table_columns)
            .order("ai_featured", desc=True)
            .order("average_rating", desc=True)
            .limit(50)
            .execute()
        )
        restaurants = result.data

        if not restaurants:
            return "No restaurants found"
        print("the restaurants found are: "+str(restaurants))
        return json.dumps(restaurants)
    
    except Exception as e:
        print(f"Error fetching restaurants: {e}")
        return "Error retrieving restaurants"

tools.append(getAllRestaurants)

@tool
def getFeaturedRestaurants(limit: int = 10) -> str:
    """Return featured restaurants prioritized by rating. Limit defaults to 10."""
    print("AI is looking for featured restaurants")
    try:
        if not supabase:
            return json.dumps([])
        lim = max(1, min(int(limit or 10), 100))
        result = (
            supabase
            .table("restaurants")
            .select(restaurants_table_columns)
            .eq("ai_featured", True)
            .order("average_rating", desc=True)
            .limit(lim)
            .execute()
        )
        restaurants = result.data
        if not restaurants:
            return json.dumps([])
        return json.dumps(restaurants)
    except Exception as e:
        print(f"Error fetching featured restaurants: {e}")
        return json.dumps([])

tools.append(getFeaturedRestaurants)

@tool
def getRestaurantsByName(query: str) -> str:
    """Search restaurants by name or description. Case-insensitive, partial matches supported."""
    q = (query or "").strip()
    print(f"AI is searching restaurants by name/description: {q}")
    try:
        if not supabase:
            return json.dumps([])
        pattern = f"%{q}%" if q else "%"
        result = (
            supabase
            .table("restaurants")
            .select(restaurants_table_columns)
            .ilike("name", pattern)
            .order("ai_featured", desc=True)
            .order("average_rating", desc=True)
            .limit(50)
            .execute()
        )
        # If name search is too strict and empty, fallback to description search
        restaurants = result.data or []
        if not restaurants and q:
            result_desc = (
                supabase
                .table("restaurants")
                .select(restaurants_table_columns)
                .ilike("description", pattern)
                .order("ai_featured", desc=True)
                .order("average_rating", desc=True)
                .limit(50)
                .execute()
            )
            restaurants = result_desc.data or []
        return json.dumps(restaurants)
    except Exception as e:
        print(f"Error searching restaurants by name: {e}")
        return json.dumps([])

tools.append(getRestaurantsByName)

@tool
def searchRestaurantsAdvanced(filters_json: str) -> str:
    """Advanced restaurant search. Accepts a JSON string with optional fields: 
    {"cuisine":"italian","price_min":1,"price_max":3,"rating_min":4,"has_outdoor":true,"tags":["shisha","parking"],"ambiance":["romantic"]}
    Returns a JSON list of restaurants sorted by featured then rating.
    """
    print(f"AI is running advanced restaurant search with filters: {filters_json}")
    try:
        if not supabase:
            return json.dumps([])
        parsed = {}
        try:
            parsed = json.loads(filters_json) if filters_json else {}
        except Exception:
            parsed = {}

        query = supabase.table("restaurants").select(restaurants_table_columns)

        cuisine = (parsed.get("cuisine") or "").strip()
        if cuisine:
            query = query.ilike("cuisine_type", f"%{cuisine}%")

        price_min = parsed.get("price_min")
        price_max = parsed.get("price_max")
        if isinstance(price_min, (int, float)):
            query = query.gte("price_range", int(price_min))
        if isinstance(price_max, (int, float)):
            query = query.lte("price_range", int(price_max))

        rating_min = parsed.get("rating_min")
        if isinstance(rating_min, (int, float)):
            query = query.gte("average_rating", float(rating_min))

        has_outdoor = parsed.get("has_outdoor")
        if isinstance(has_outdoor, bool):
            query = query.eq("outdoor_seating", has_outdoor)

        tags = parsed.get("tags")
        if isinstance(tags, list) and tags:
            try:
                query = query.contains("tags", tags)
            except Exception:
                # Fallback to text match if contains not available
                for t in tags:
                    query = query.ilike("tags", f"%{t}%")

        ambiance = parsed.get("ambiance")
        if isinstance(ambiance, list) and ambiance:
            try:
                query = query.contains("ambiance_tags", ambiance)
            except Exception:
                for a in ambiance:
                    query = query.ilike("ambiance_tags", f"%{a}%")

        limit = parsed.get("limit")
        lim = max(1, min(int(limit or 50), 100))

        result = (
            query
            .order("ai_featured", desc=True)
            .order("average_rating", desc=True)
            .limit(lim)
            .execute()
        )
        items = result.data or []
        return json.dumps(items)
    except Exception as e:
        print(f"Error in advanced search: {e}")
        return json.dumps([])

tools.append(searchRestaurantsAdvanced)

# -----------------------------
# Availability tools (backend service key based)
# -----------------------------

@tool
def checkAnyTimeSlots(restaurant_id: str, date: str, party_size: int, user_id: Optional[str] = None) -> str:
    """Return {"available": bool} if at least one slot exists for the given date and party size."""
    try:
        available = av_check_any_time_slots(restaurant_id, date, int(party_size), user_id)
        return json.dumps({"available": bool(available)})
    except Exception as e:
        return json.dumps({"error": str(e)})

tools.append(checkAnyTimeSlots)

@tool
def getAvailableTimeSlots(restaurant_id: str, date: str, party_size: int, user_id: Optional[str] = None) -> str:
    """Return a JSON list of {time: 'HH:MM', available: true} slots for the day."""
    try:
        slots = av_get_available_time_slots(restaurant_id, date, int(party_size), user_id)
        return json.dumps(slots)
    except Exception as e:
        return json.dumps({"error": str(e)})

tools.append(getAvailableTimeSlots)

@tool
def getTableOptionsForSlot(restaurant_id: str, date: str, time: str, party_size: int) -> str:
    """Return table options for a specific time slot, or null if none."""
    try:
        options = av_get_table_options_for_slot(restaurant_id, date, time, int(party_size))
        return json.dumps(options)
    except Exception as e:
        return json.dumps({"error": str(e)})

tools.append(getTableOptionsForSlot)

@tool
def searchTimeRange(restaurant_id: str, date: str, start_time: str, end_time: str, party_size: int, user_id: Optional[str] = None) -> str:
    """Return best table options for all available slots within a time range on a given date."""
    try:
        results = av_search_time_range(restaurant_id, date, start_time, end_time, int(party_size), user_id)
        return json.dumps(results)
    except Exception as e:
        return json.dumps({"error": str(e)})

tools.append(searchTimeRange)

# Initialize the model
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash", 
    api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0
)
llm = llm.bind_tools(tools)

def agent_node(state: AgentState) -> AgentState:
    """Our agent node that processes messages and generates responses."""
    messages = state["messages"]
    
    # Create the full prompt with system message and conversation
    full_messages = [SystemMessage(content=system_prompt)] + messages
    
    print(f"Sending {len(full_messages)} messages to LLM")
    
    # Get response from the model
    response = llm.invoke(full_messages)
    
    # print(f"LLM response type: {type(response)}")
    # print(f"LLM response content: {response.content}")
    # print(f"LLM tool calls: {response.tool_calls}")
    
    # Return the updated state with the new message
    return {"messages": [response]}

def should_continue(state: AgentState) -> str:
    """Determine whether to continue with tools or end the conversation"""
    last_message = state["messages"][-1]

    
    if isinstance(last_message, AIMessage):
        tool_calls = getattr(last_message, 'tool_calls', []) or []
        print(f"Tool calls found: {len(tool_calls)}")
        
        # If there are tool calls, check if finishedUsingTools was called
        for call in tool_calls:
            print(f"Tool call: {call}")
            if call["name"] == "finishedUsingTools":
                print("✅ AI called finishedUsingTools tool - ending")
                return "end"
        
        # If there are other tool calls, continue to tools
        if tool_calls:
            print("🔧 AI has tool calls - continuing to tools")
            return "continue"
        
        # If no tool calls and has content, end
        if last_message.content:
            print("💬 AI has content but no tool calls - ending")
            return "end"
    
    print("🔄 Default case - continuing")
    return "continue"

# Create the graph
graph = StateGraph(AgentState)

# Add nodes
graph.add_node("agent", agent_node)
graph.add_node("tools", ToolNode(tools))

# Add edges
graph.add_edge(START, "agent")
graph.add_conditional_edges(
    "agent",
    should_continue,
    {
        "continue": "tools",
        "end": END
    }
)
graph.add_edge("tools", "agent")

# Compile the graph
app = graph.compile()

def chat_with_bot(user_input: str) -> str:
    """
    Function to chat with the bot. Each request is stateless.
    Frontend handles conversation history management.
    """
    try:
        # Lightweight intent detection to nudge the LLM to use tools and include IDs
        ui_lower = (user_input or "").lower()
        discovery_triggers = [
            "recommend", "suggest", "find", "show", "options", "restaurant", "places", "cuisine",
            "near", "around", "best", "top", "where to",
            "available", "availability", "slot", "slots", "time", "times", "book", "reserve", "reservation",
            "today", "tonight", "tomorrow", "opening", "openings"
        ]
        should_nudge = any(t in ui_lower for t in discovery_triggers)

        guiding_message = None
        if should_nudge:
            guiding_message = SystemMessage(content=(
                "For this request, if it's about discovering restaurants, call the appropriate search tools first and include up to 5 real IDs in a line starting with 'RESTAURANTS_TO_SHOW:'. Prioritize featured and highly-rated restaurants.\n"
                "If it's about availability for a specific restaurant: 1) FIRST use convertRelativeDate for any relative dates (today, tomorrow, etc.), 2) locate the restaurant via getRestaurantsByName, 3) use availability tools with the converted date (checkAnyTimeSlots, getAvailableTimeSlots, getTableOptionsForSlot, searchTimeRange). Assume party size 2 if unspecified; state assumptions. When done with tools, call finishedUsingTools."
            ))

        # Create a fresh state for each request, optionally with a guiding system message
        base_messages = [HumanMessage(content=user_input)]
        if guiding_message:
            current_input = {"messages": [guiding_message] + base_messages}
        else:
            current_input = {"messages": base_messages}
        
        # Run the agent with just the current message
        result = app.invoke(current_input)

        # Extract messages
        ai_messages = [msg for msg in result["messages"] if isinstance(msg, AIMessage)]
        tool_messages = [msg for msg in result["messages"] if isinstance(msg, ToolMessage)]

        # If we have a proper AI response, try to ensure IDs are present when intent suggests discovery
        if ai_messages:
            last_ai_message = ai_messages[-1]
            if last_ai_message.content and last_ai_message.content.strip():
                text_content = last_ai_message.content.strip()
                if "RESTAURANTS_TO_SHOW:" not in text_content:
                    # Heuristic: only append restaurant IDs for discovery-type prompts, not availability questions
                    intent_text = (user_input or "").lower()
                    availability_markers = [
                        "available", "availability", "slot", "slots", "time", "times", "book", "reserve", "reservation",
                        "today", "tonight", "tomorrow", "opening", "openings"
                    ]
                    discovery_only = not any(t in intent_text for t in availability_markers)
                    if discovery_only:
                        try:
                            if supabase:
                                result = (
                                    supabase
                                    .table("restaurants")
                                    .select(restaurants_table_columns)
                                    .eq("ai_featured", True)
                                    .order("average_rating", desc=True)
                                    .limit(5)
                                    .execute()
                                )
                                items = result.data or []
                                if not items:
                                    result = (
                                        supabase
                                        .table("restaurants")
                                        .select(restaurants_table_columns)
                                        .order("ai_featured", desc=True)
                                        .order("average_rating", desc=True)
                                        .limit(5)
                                        .execute()
                                    )
                                    items = result.data or []
                                ids = [str(x.get('id')) for x in items if isinstance(x, dict) and x.get('id')]
                                ids = [i for i in ids if i][:5]
                                if ids:
                                    return text_content + "\nRESTAURANTS_TO_SHOW: " + ",".join(ids)
                        except Exception:
                            pass
                return text_content

        # Build a helpful fallback from tool outputs if available
        try:
            # Collect tool outputs by name when possible
            tool_results_by_name = {}
            for tool_msg in tool_messages:
                tool_name = getattr(tool_msg, 'name', None)
                if tool_name:
                    tool_results_by_name[tool_name] = tool_msg.content

            import json as _json

            # Prefer any restaurant list; support multiple tool outputs
            def _extract_ids(items_json: str) -> list[str]:
                try:
                    items = _json.loads(items_json)
                    if isinstance(items, list) and items:
                        ids = [str(x.get('id')) for x in items if isinstance(x, dict) and x.get('id')]
                        return [i for i in ids if i]
                except Exception:
                    return []
                return []

            all_ids: list[str] = []
            for content in tool_results_by_name.values():
                all_ids.extend(_extract_ids(content))
            # Deduplicate and limit
            seen = set()
            unique_ids = []
            for _id in all_ids:
                if _id not in seen:
                    seen.add(_id)
                    unique_ids.append(_id)
            if unique_ids:
                return "Here are some restaurants you might like.\nRESTAURANTS_TO_SHOW: " + ",".join(unique_ids[:5])

            # Cuisines list fallback
            cuisines = tool_results_by_name.get('getAllCuisineTypes')
            if cuisines:
                try:
                    cu = _json.loads(cuisines)
                    if isinstance(cu, list) and cu:
                        return "Available cuisine types: " + ", ".join(map(str, cu[:10]))
                except Exception:
                    pass
        except Exception:
            pass

        print("No AI messages found in result and no usable tool fallback")
        return "I apologize, I couldn't generate a proper response. Please try again."
            
    except Exception as e:
        print(f"Error running agent: {e}")
        return f"Sorry, I encountered an error: {str(e)}"

# Interactive chat function for testing (kept for local development)
def start_interactive_chat():
    """Start an interactive chat session for local testing."""
    print("🍽️ Welcome to TableReserve Restaurant Assistant!")
    print("Type 'quit' to exit or enter your message.")
    print("Note: Each message is processed independently (stateless mode)")
    print("-" * 50)
    
    while True:
        user_input = input("\nYou: ").strip()
        
        if user_input.lower() == 'quit':
            print("Thanks for using TableReserve! Goodbye! 👋")
            break
        elif not user_input:
            print("Please enter a message.")
            continue
        
        print("Bot: ", end="", flush=True)
        response = chat_with_bot(user_input)
        print(response)

# Example usage for testing
if __name__ == "__main__":
    start_interactive_chat()