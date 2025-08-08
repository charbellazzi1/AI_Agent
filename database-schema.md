# Database Schema Documentation

## Overview
This is a comprehensive Supabase/PostgreSQL schema for a restaurant reservation system with dual AI agents. The schema supports customer bookings, restaurant management, staff operations, social features, and loyalty programs.

## Core Entity Relationships

### Users & Authentication
- **`profiles`** - Extended user profiles (links to `auth.users`)
- **`friends`** - User friendships
- **`friend_requests`** - Friendship management

### Restaurant Management
- **`restaurants`** - Core restaurant data with location, cuisine, hours
- **`restaurant_staff`** - Staff roles and permissions
- **`restaurant_hours`** - Regular operating hours by day
- **`restaurant_special_hours`** - Holiday/exception hours
- **`restaurant_closures`** - Planned closures

### Table Management
- **`restaurant_tables`** - Physical table definitions with positioning
- **`table_combinations`** - Rules for combining tables for larger parties
- **`floor_plans`** - SVG layouts for restaurant floors

### Booking System
- **`bookings`** - Core reservation data with status tracking
- **`booking_tables`** - Many-to-many: bookings to tables
- **`booking_status_history`** - Audit trail for status changes
- **`booking_archive`** - Completed/old bookings
- **`booking_attendees`** - Group booking participants
- **`booking_invites`** - Invitation system for group bookings

### Customer Relationship Management
- **`restaurant_customers`** - Customer profiles per restaurant
- **`customer_notes`** - Staff notes about customers
- **`customer_preferences`** - Seating, timing, service preferences
- **`customer_tags`** - Categorization system
- **`customer_tag_assignments`** - Tag relationships
- **`customer_relationships`** - Family/friend connections

### Menu & Pricing
- **`menu_categories`** - Menu sections
- **`menu_items`** - Individual dishes with dietary info

### Reviews & Social
- **`reviews`** - Customer feedback with detailed ratings
- **`review_replies`** - Restaurant responses
- **`posts`** - Social media style sharing
- **`post_comments`, `post_likes`, `post_tags`, `post_images`** - Social interactions

### Loyalty & Rewards
- **`loyalty_activities`** - Point-earning actions
- **`loyalty_rewards`** - Available rewards catalog
- **`loyalty_redemptions`** - Used rewards tracking
- **`restaurant_loyalty_rules`** - Custom point rules per restaurant
- **`restaurant_loyalty_balance`** - Restaurant point inventory
- **`restaurant_loyalty_transactions`** - Point transaction log
- **`tier_benefits`** - Membership tier perks

### Offers & Promotions
- **`special_offers`** - Promotional campaigns
- **`user_offers`** - Claimed offers by users

### Operational Features
- **`restaurant_playlists`** - User-curated restaurant lists
- **`playlist_items`, `playlist_collaborators`** - Playlist management
- **`favorites`** - Simple restaurant bookmarking
- **`waitlist`** - Waiting list for full restaurants
- **`notifications`** - In-app messaging system

## Key Data Types & Constraints

### Booking Status Flow
```
pending → confirmed → [arrived → seated → completed] | [cancelled_by_user | cancelled_by_restaurant | no_show]
```

### Table Types
- `booth`, `window`, `patio`, `standard`, `bar`, `private`

### User Tiers
- `bronze`, `silver`, `gold`, `platinum`

### Critical Columns for AI Agents

#### For Staff Agent Queries
- `restaurant_id` - Always filter by this for staff operations
- `booking_time` - Use date ranges for daily/weekly stats
- `party_size` - Essential for table matching
- `status` - Filter confirmed/active bookings
- `table_type`, `capacity`, `min_capacity`, `max_capacity` - Table assignment logic

#### For Customer Agent Queries
- `ai_featured` - Prioritize these restaurants in recommendations
- `cuisine_type` - Primary search filter
- `price_range` - 1-4 scale
- `average_rating` - Quality indicator
- `dietary_options`, `ambiance_tags` - Feature matching

## Database Query Patterns

### Performance Guidelines
```sql
-- Always select specific columns, never SELECT *
SELECT id, name, cuisine_type FROM restaurants;

-- Use restaurant_id filtering for staff queries
WHERE restaurant_id = 'uuid' AND booking_time >= 'date'

-- Case-insensitive search with ilike
WHERE cuisine_type ILIKE '%italian%'

-- Date range queries for operational stats
WHERE booking_time BETWEEN start_date AND end_date
```

### Common Joins for AI Tools
```sql
-- Bookings with customer info
SELECT b.*, p.full_name, p.allergies 
FROM bookings b 
JOIN profiles p ON b.user_id = p.id

-- Tables with current bookings
SELECT t.*, bt.booking_id 
FROM restaurant_tables t 
LEFT JOIN booking_tables bt ON t.id = bt.table_id

-- Customer history with preferences
SELECT rc.*, p.dietary_restrictions, cn.note
FROM restaurant_customers rc
JOIN profiles p ON rc.user_id = p.id
LEFT JOIN customer_notes cn ON rc.id = cn.customer_id
```

## Schema Update Protocol

When database schema changes occur:

1. **Update this file** with new tables, columns, or relationships
2. **Update AI agent tools** that query affected tables
3. **Update column selection strings** in agent code
4. **Test tool outputs** to ensure JSON serialization works
5. **Update system prompts** if new capabilities are added

## Common Gotchas

- **NULL handling**: Many foreign keys are optional (guest bookings)
- **Array columns**: Use PostgreSQL array functions for filtering
- **JSONB columns**: Extract with `->` or `->>` operators
- **Timezone aware**: All timestamps are `timestamptz`
- **Soft deletes**: Use `is_active` flags, rarely hard delete
- **Guest vs User bookings**: Check both `user_id` and `guest_*` fields

## AI Agent Column Sets

### Customer Agent Essentials
```sql
"id, name, description, address, cuisine_type, price_range, average_rating, dietary_options, ambiance_tags, outdoor_seating, ai_featured"
```

### Staff Agent Essentials
```sql
-- Bookings
"id, booking_time, party_size, status, guest_name, guest_email, special_requests, dietary_notes"

-- Tables
"id, table_number, table_type, capacity, min_capacity, max_capacity, features, is_active"

-- Customers
"id, guest_name, guest_email, total_bookings, vip_status, last_visit, preferred_table_types"
```
