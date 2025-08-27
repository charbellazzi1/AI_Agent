# RMS Database Context Summary

## Quick Reference Guide for AI Restaurant Agent Development

### Core Database Context for AI Agent Integration

This document provides essential context for the AI restaurant agent system that interfaces with the RMS (Restaurant Management System) database.

#### Project Configuration
- **Database**: PostgreSQL 17.4.1.074 (Supabase)
- **Project ID**: xsovqvbigdettnpeisjs
- **Primary Schema**: public
- **Key Extensions**: PostGIS, uuid-ossp, pgcrypto, pg_cron

### Essential Tables for AI Agent Operations

#### 1. Table Management & Availability
```sql
-- Core table for seating management
restaurant_tables (id, restaurant_id, table_number, capacity, min_capacity, max_capacity, 
                  table_type, is_active, is_combinable, priority_score, section_id)

-- Table assignments to bookings  
booking_tables (booking_id, table_id)

-- Table grouping and organization
restaurant_sections (id, restaurant_id, name, description, display_order)

-- Predefined table combinations
table_combinations (id, restaurant_id, primary_table_id, secondary_table_id, combined_capacity)
```

#### 2. Booking System
```sql
-- Main reservation records
bookings (id, user_id, restaurant_id, booking_time, party_size, status, 
          confirmation_code, turn_time_minutes, special_requests, table_preferences)

-- Booking status change tracking
booking_status_history (booking_id, old_status, new_status, changed_by, changed_at, reason)

-- Group booking invitations
booking_invites (booking_id, from_user_id, to_user_id, status, message)
```

#### 3. Customer Management
```sql
-- User profiles and information
profiles (id, email, full_name, phone_number, loyalty_tier, loyalty_points, rating)

-- Restaurant-specific customer data
restaurant_customers (id, restaurant_id, user_id, customer_tier, lifetime_spend, 
                     visit_count, last_visit, preferred_times, favorite_tables)

-- Staff notes about customers
customer_notes (customer_id, note, category, is_important, created_by)

-- Customer preferences tracking
customer_preferences (customer_id, preference_type, preference_value)
```

#### 4. Waitlist Management
```sql
-- Waiting list for unavailable slots
waitlist (id, user_id, restaurant_id, desired_date, desired_time_range, party_size, 
          table_type, status, guest_name, guest_email, notification_expires_at)
```

### Critical Database Functions for AI Agent

#### Advanced Table Recommendation Function
```sql
-- Primary function for intelligent table selection
suggest_optimal_tables(
    p_restaurant_id uuid,
    p_party_size integer, 
    p_start_time timestamptz,
    p_end_time timestamptz
) RETURNS TABLE(table_ids uuid[], total_capacity integer, requires_combination boolean)
```

**Algorithm Logic**:
1. **Phase 1**: Search for optimal single table
   - Filter by capacity >= party_size
   - Check real-time availability  
   - Order by capacity closeness + priority score
2. **Phase 2**: If no single table, find table combinations
   - Search combinable table pairs
   - Validate combined capacity
   - Ensure both tables available

#### Table Availability Functions
```sql
-- Get all available tables for time slot
get_available_tables(p_restaurant_id, p_start_time, p_end_time, p_party_size)

-- Validate table combination business rules  
validate_table_combination(p_table_ids uuid[])

-- Check specific table availability
verify_table_availability(p_restaurant_id, p_booking_time, p_table_ids[], p_turn_time)
```

#### Booking Management Functions
```sql
-- Complete booking creation with table assignment
create_booking_with_tables(p_user_id, p_restaurant_id, p_booking_time, p_party_size, 
                          p_table_ids[], p_turn_time, p_special_requests, ...)

-- Fix bookings missing table assignments
fix_booking_without_tables(p_booking_id)

-- Data cleanup and maintenance
cleanup_orphaned_booking_tables()
```

### AI Agent Integration Patterns

#### 1. Customer-Facing Agent (`AI_Agent.py`)
**Primary Tables Used**:
- `restaurants` (discovery, info)
- `profiles` (user data)
- `bookings` (reservation history)
- `reviews` (ratings, feedback)
- `special_offers` (promotions)

**Key Functions**:
- Restaurant discovery and filtering
- Basic availability checking
- Booking conversion assistance
- Recommendation personalization

#### 2. Staff-Facing Agent (`AI_Agent_Restaurant.py`)
**Primary Tables Used**:
- `bookings` (reservation management)
- `restaurant_tables` (table operations)
- `booking_tables` (table assignments)
- `restaurant_customers` (customer profiles)
- `customer_notes` (service notes)
- `waitlist` (queue management)

**Key Functions**:
- **Advanced Table Recommendations**: Uses `suggest_optimal_tables()`
- **Real-time Availability**: Uses `get_available_tables()`
- **Table Combination Validation**: Uses `validate_table_combination()`
- **Immediate Seating**: Time-aware table suggestions
- **Customer Service**: Historical data and preferences

### Database Performance Considerations

#### Critical Indexes
```sql
-- Booking availability queries (most frequent)
idx_bookings_restaurant_time_status ON bookings(restaurant_id, booking_time, status)

-- Table assignment lookups
idx_booking_tables_table_booking ON booking_tables(table_id, booking_id) 

-- Restaurant discovery
idx_restaurants_location ON restaurants USING GIST(coordinates)

-- Customer history queries
idx_bookings_user_status_time ON bookings(user_id, status, booking_time DESC)
```

#### Query Optimization Tips
1. **Always filter by restaurant_id first** in table queries
2. **Use time range filters** for booking availability 
3. **Leverage composite indexes** for complex availability queries
4. **Consider materialized views** for frequently accessed aggregations

### AI Agent Tool Implementation Patterns

#### Tool Response Format
All database tools should return JSON strings for LangChain compatibility:
```python
@tool
def getOptimalTableRecommendations(restaurant_id: str, party_size: int, 
                                 booking_time: str, turn_time: int = 120) -> str:
    """Get AI-powered table recommendations using database algorithms."""
    try:
        # Call suggest_optimal_tables function
        result = supabase.rpc('suggest_optimal_tables', {
            'p_restaurant_id': restaurant_id,
            'p_party_size': party_size, 
            'p_start_time': booking_time,
            'p_end_time': end_time
        }).execute()
        return json.dumps(result.data)
    except Exception as e:
        return f"Error getting table recommendations: {str(e)}"
```

#### Error Handling Patterns
```python
# Standard error handling for all tools
try:
    result = supabase.table("table_name").select().execute()
    return json.dumps(result.data)
except Exception as e:
    return f"Error description: {str(e)}"
```

### Business Logic Constants

#### Booking Status Values
```python
BOOKING_STATUSES = [
    'pending', 'confirmed', 'cancelled_by_user', 'declined_by_restaurant',
    'auto_declined', 'completed', 'no_show', 'arrived', 'seated', 
    'ordered', 'appetizers', 'main_course', 'dessert', 'payment',
    'cancelled_by_restaurant'
]
```

#### Table Types
```python
TABLE_TYPES = ['indoor', 'outdoor', 'bar', 'private', 'any']
```

#### Customer Tiers
```python
CUSTOMER_TIERS = ['regular', 'preferred', 'vip', 'platinum']
LOYALTY_TIERS = ['bronze', 'silver', 'gold', 'platinum']
```

### Common Query Patterns

#### Get Today's Bookings
```python
today_bookings = supabase.table("bookings")\
    .select("*, profiles(full_name, phone_number)")\
    .eq("restaurant_id", restaurant_id)\
    .gte("booking_time", datetime.now().strftime('%Y-%m-%d'))\
    .lt("booking_time", (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'))\
    .in_("status", ["confirmed", "pending", "seated", "arrived"])\
    .order("booking_time")\
    .execute()
```

#### Get Customer History
```python
customer_data = supabase.table("restaurant_customers")\
    .select("*, customer_notes(*), bookings(count)")\
    .eq("restaurant_id", restaurant_id)\
    .or_(f"user_id.eq.{user_id},guest_email.eq.{email}")\
    .execute()
```

#### Check Table Availability
```python
availability = supabase.rpc('get_available_tables', {
    'p_restaurant_id': restaurant_id,
    'p_start_time': start_time,
    'p_end_time': end_time, 
    'p_party_size': party_size
}).execute()
```

### Integration with AI Agent Architecture

#### Memory & Context Management
- **Conversation History**: Frontend manages 20-message sliding window
- **Session State**: 8-hour staff sessions with context preservation
- **User Preferences**: Stored in `customer_preferences` table

#### Tool Execution Flow
1. **Data Gathering Phase**: Use multiple tools to collect context
2. **Processing Phase**: Apply business logic and database functions
3. **Response Phase**: Call `finishedUsingTools()` before responding
4. **Format Response**: Structure output for UI consumption

#### Error Recovery Strategies
- **Graceful Degradation**: Fallback to simpler queries if complex ones fail
- **Partial Results**: Return available data even if some queries fail
- **User Feedback**: Clear error messages for booking conflicts

### Security & Access Control

#### Row Level Security (RLS)
- Most tables implement RLS policies
- Restaurant data isolated by `restaurant_id`
- User data protected by `auth.uid()`

#### Staff Permissions
- Granular permission system via `restaurant_staff.permissions`
- Role-based access to different functionalities
- Audit trail for sensitive operations

This context provides the essential information needed for AI agents to effectively interact with the RMS database while maintaining performance, security, and data integrity.
