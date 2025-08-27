# RMS Database Documentation

## Project Overview
- **Project ID**: xsovqvbigdettnpeisjs
- **Database**: PostgreSQL 17.4.1.074
- **Status**: ACTIVE_HEALTHY
- **Created**: 2025-06-16

## Core Database Architecture

### User Management & Authentication

#### `profiles` (Main User Table)
Core user information table for all app users.
```sql
Key Fields:
- id (uuid, PK): User identifier
- email (text): User email address
- full_name (text): User's display name
- phone_number (text): Contact number
- avatar_url (text): Profile picture URL
- birth_date (date): Date of birth
- gender (text): User gender
- bio (text): User biography
- loyalty_tier (text): Loyalty status (bronze/silver/gold/platinum)
- loyalty_points (integer): Current loyalty points
- total_spent (numeric): Lifetime spending
- rating (numeric): User rating (1-5)
- is_verified (boolean): Email verification status
- location_coordinates (point): User location
- last_seen (timestamptz): Last activity
```

#### User Management Related Tables
- **`user_devices`**: Device registration for push notifications
- **`user_privacy_settings`**: Privacy and notification preferences
- **`notification_preferences`**: Granular notification controls
- **`friends`**: User friendship connections
- **`friend_requests`**: Pending friend requests

### Restaurant Management System

#### `restaurants` (Core Restaurant Data)
Main restaurant information and settings.
```sql
Key Fields:
- id (uuid, PK): Restaurant identifier
- name (text): Restaurant name
- description (text): Restaurant description
- cuisine_type (text): Type of cuisine
- address (text): Physical address
- phone_number (text): Contact phone
- email (text): Contact email
- website (text): Restaurant website
- coordinates (point): Geographic location
- price_range (text): Price category (budget/mid/upscale/fine-dining)
- rating (numeric): Overall rating
- total_reviews (integer): Review count
- is_featured (boolean): Featured restaurant status
- status (text): Operating status (active/inactive)
- booking_policy (text): Booking acceptance policy
- max_advance_booking_days (integer): Booking window
- ai_featured (boolean): AI recommendation priority
- cover_image_url (text): Main restaurant image
- logo_url (text): Restaurant logo
- social_media_links (jsonb): Social media handles
- features (text[]): Restaurant amenities
- opening_hours (jsonb): Operating hours
- special_hours (jsonb): Holiday/special hours
- minimum_party_size (integer): Minimum booking size
- maximum_party_size (integer): Maximum booking size
- auto_accept_bookings (boolean): Instant booking setting
- requires_approval (boolean): Manual approval requirement
- cancellation_policy (text): Cancellation terms
- reservation_deposit (numeric): Required deposit
- loyalty_program_enabled (boolean): Loyalty system active
```

#### `restaurant_staff` (Staff Management)
Restaurant employee information and access control.
```sql
Key Fields:
- id (uuid, PK): Staff member identifier
- user_id (uuid, FK → profiles): Link to user account
- restaurant_id (uuid, FK → restaurants): Restaurant association
- role (text): Staff role/position
- hire_date (date): Employment start date
- hourly_rate (numeric): Base pay rate
- is_active (boolean): Employment status
- permissions (text[]): System permissions
- department (text): Work department
- emergency_contact (jsonb): Emergency contact info
- work_schedule (jsonb): Regular schedule
- notes (text): Management notes
```

### Table Management & Seating

#### `restaurant_tables` (Core Table Configuration)
Physical table definitions and properties.
```sql
Key Fields:
- id (uuid, PK): Table identifier
- restaurant_id (uuid, FK → restaurants): Restaurant association
- table_number (text): Display number/name
- section_id (uuid, FK → restaurant_sections): Table section
- capacity (integer): Standard seating capacity
- min_capacity (integer): Minimum party size
- max_capacity (integer): Maximum party size
- table_type (text): Table category (indoor/outdoor/bar/private)
- shape (text): Table shape (round/square/rectangular)
- is_active (boolean): Table availability
- is_combinable (boolean): Can be combined with others
- combinable_with (uuid[]): Specific combination partners
- priority_score (integer): Booking priority (lower = higher priority)
- x_position (integer): Floor plan X coordinate
- y_position (integer): Floor plan Y coordinate
- width (integer): Table width
- height (integer): Table height
- amenities (text[]): Table-specific features
- accessibility_features (text[]): Accessibility options
- description (text): Table description
- service_fee (numeric): Additional charges
- booking_notes (text): Special booking instructions
```

#### `restaurant_sections` (Table Organization)
Logical grouping of tables within restaurants.
```sql
Key Fields:
- id (uuid, PK): Section identifier
- restaurant_id (uuid, FK → restaurants): Restaurant association
- name (text): Section name
- description (text): Section description
- display_order (integer): Sort order
- is_active (boolean): Section status
- color (text): UI color coding
- icon (text): Display icon
```

#### `table_combinations` (Multi-Table Bookings)
Predefined table combination rules for larger parties.
```sql
Key Fields:
- id (uuid, PK): Combination identifier
- restaurant_id (uuid, FK → restaurants): Restaurant association
- primary_table_id (uuid, FK → restaurant_tables): Main table
- secondary_table_id (uuid, FK → restaurant_tables): Additional table
- combined_capacity (integer): Total capacity
- is_active (boolean): Combination availability
```

### Booking System

#### `bookings` (Core Reservation Data)
Main booking records with comprehensive tracking.
```sql
Key Fields:
- id (uuid, PK): Booking identifier
- user_id (uuid, FK → profiles): Customer reference
- restaurant_id (uuid, FK → restaurants): Restaurant reference
- booking_time (timestamptz): Reservation datetime
- party_size (integer): Number of guests
- status (text): Booking status (pending/confirmed/cancelled/completed/etc.)
- special_requests (text): Customer requests
- occasion (text): Special occasion
- dietary_notes (text[]): Dietary requirements
- confirmation_code (text): Unique booking code
- table_preferences (text[]): Seating preferences
- reminder_sent (boolean): Reminder notification status
- checked_in_at (timestamptz): Arrival timestamp
- loyalty_points_earned (integer): Points awarded
- turn_time_minutes (integer): Expected duration (default: 120)
- guest_name (text): Name for booking
- guest_email (text): Contact email
- guest_phone (text): Contact phone
- is_group_booking (boolean): Group reservation flag
- organizer_id (uuid, FK → profiles): Group organizer
- attendees (integer): Confirmed attendees
- applied_offer_id (uuid, FK → special_offers): Applied promotion
- applied_loyalty_rule_id (uuid, FK → restaurant_loyalty_rules): Loyalty bonus
- actual_end_time (timestamptz): Actual departure time
- seated_at (timestamptz): Seating timestamp
- meal_progress (jsonb): Dining stage tracking
- source (text): Booking origin (app/web/phone)
```

#### `booking_tables` (Table Assignments)
Links bookings to specific tables.
```sql
Key Fields:
- id (uuid, PK): Assignment identifier
- booking_id (uuid, FK → bookings): Booking reference
- table_id (uuid, FK → restaurant_tables): Table reference
- created_at (timestamptz): Assignment timestamp
```

#### `booking_status_history` (Status Tracking)
Audit trail for booking status changes.
```sql
Key Fields:
- id (uuid, PK): History record identifier
- booking_id (uuid, FK → bookings): Booking reference
- old_status (text): Previous status
- new_status (text): New status
- changed_by (uuid, FK → profiles): User who made change
- changed_at (timestamptz): Change timestamp
- reason (text): Change reason
- metadata (jsonb): Additional change data
```

### Advanced Table Recommendation System

#### Core Functions

##### `suggest_optimal_tables()`
**Purpose**: Intelligent table selection algorithm
**Parameters**:
- `p_restaurant_id (uuid)`: Restaurant identifier
- `p_party_size (integer)`: Number of guests
- `p_start_time (timestamptz)`: Booking start time
- `p_end_time (timestamptz)`: Booking end time

**Returns**: TABLE(table_ids uuid[], total_capacity integer, requires_combination boolean)

**Algorithm**:
1. **Single Table Search**: Finds best-fitting individual table
   - Filters by capacity >= party_size
   - Checks availability during time slot
   - Orders by capacity closeness and priority score
2. **Combination Search**: If no single table available
   - Finds combinable table pairs
   - Validates both tables are available
   - Optimizes for total capacity match

##### `validate_table_combination()`
**Purpose**: Validates table combination business rules
**Parameters**: `p_table_ids (uuid[])`: Array of table IDs
**Returns**: TABLE(is_valid boolean, total_capacity integer, message text)

##### `get_available_tables()`
**Purpose**: Gets all available tables for time slot
**Parameters**:
- `p_restaurant_id (uuid)`: Restaurant ID
- `p_start_time (timestamptz)`: Start time
- `p_end_time (timestamptz)`: End time  
- `p_party_size (integer)`: Party size

**Returns**: Available tables with capacity matching

### Waitlist System

#### `waitlist` (Reservation Queue)
Manages waiting list for unavailable time slots.
```sql
Key Fields:
- id (uuid, PK): Waitlist entry identifier
- user_id (uuid, FK → profiles): Customer reference
- restaurant_id (uuid, FK → restaurants): Restaurant reference
- desired_date (date): Preferred date
- desired_time_range (text): Preferred time window
- party_size (integer): Number of guests
- table_type (table_type enum): Seating preference
- status (waiting_status enum): Entry status
- guest_name (text): Contact name
- guest_email (text): Contact email
- guest_phone (text): Contact phone
- special_requests (text): Additional requests
- notified_at (timestamptz): Notification sent time
- notification_expires_at (timestamptz): Notification expiry
- expires_at (timestamptz): Entry expiry
- converted_booking_id (uuid, FK → bookings): Resulting booking
```

**Enums**:
- `table_type`: any, indoor, outdoor, bar, private
- `waiting_status`: active, notified, booked, expired, cancelled

### Customer Relationship Management

#### `restaurant_customers` (Customer Profiles)
Restaurant-specific customer information.
```sql
Key Fields:
- id (uuid, PK): Customer record identifier
- restaurant_id (uuid, FK → restaurants): Restaurant association
- user_id (uuid, FK → profiles): User account link
- customer_tier (text): VIP status
- lifetime_spend (numeric): Total spending
- visit_count (integer): Number of visits
- last_visit (timestamptz): Most recent visit
- average_party_size (numeric): Typical group size
- preferred_times (text[]): Preferred booking times
- favorite_tables (uuid[]): Preferred seating
- notes (text): Staff notes
- tags (text[]): Customer categorization
```

#### `customer_notes` (Staff Notes)
Detailed notes about customers.
```sql
Key Fields:
- id (uuid, PK): Note identifier
- customer_id (uuid, FK → restaurant_customers): Customer reference
- note (text): Note content
- category (text): Note type (dietary/preference/behavior/special_occasion/general)
- is_important (boolean): High priority flag
- created_by (uuid, FK → profiles): Staff member
```

#### `customer_preferences` (Preference Tracking)
Structured customer preference data.
```sql
Key Fields:
- id (uuid, PK): Preference identifier
- customer_id (uuid, FK → restaurant_customers): Customer reference
- preference_type (text): Category (seating/ambiance/service/menu/timing)
- preference_value (jsonb): Structured preference data
```

### Loyalty & Rewards System

#### `restaurant_loyalty_rules` (Loyalty Configuration)
Restaurant-specific loyalty program rules.
```sql
Key Fields:
- id (uuid, PK): Rule identifier
- restaurant_id (uuid, FK → restaurants): Restaurant association
- rule_type (text): Rule category
- trigger_condition (jsonb): Activation conditions
- reward_type (text): Reward category
- reward_value (numeric): Reward amount
- points_required (integer): Points cost
- max_uses_per_user (integer): Usage limit
- is_active (boolean): Rule status
```

#### `loyalty_activities` (Points Transactions)
Detailed loyalty point transaction log.
```sql
Key Fields:
- id (uuid, PK): Activity identifier
- user_id (uuid, FK → profiles): User reference
- restaurant_id (uuid, FK → restaurants): Restaurant reference
- activity_type (text): Transaction type
- points_earned (integer): Points gained
- points_spent (integer): Points used
- related_booking_id (uuid, FK → bookings): Associated booking
- related_review_id (uuid, FK → reviews): Associated review
- description (text): Activity description
```

#### `tier_benefits` (Loyalty Tier Perks)
System-wide loyalty tier benefits.
```sql
Key Fields:
- id (uuid, PK): Benefit identifier
- tier (text): Loyalty tier (bronze/silver/gold/platinum)
- benefit_type (text): Benefit category
- benefit_value (text): Benefit details
- description (text): Benefit description
- is_active (boolean): Benefit status
```

### Review & Rating System

#### `reviews` (Customer Feedback)
Customer reviews and ratings.
```sql
Key Fields:
- id (uuid, PK): Review identifier
- user_id (uuid, FK → profiles): Reviewer
- restaurant_id (uuid, FK → restaurants): Restaurant reviewed
- booking_id (uuid, FK → bookings): Related booking
- overall_rating (integer): Overall score (1-5)
- food_rating (integer): Food quality score
- service_rating (integer): Service score
- ambiance_rating (integer): Ambiance score
- value_rating (integer): Value score
- review_text (text): Written review
- recommend_to_friend (boolean): Recommendation flag
- visit_again (boolean): Return intent
- tags (text[]): Review tags
- photos (text[]): Review photos
- is_verified (boolean): Verified purchase
- helpful_count (integer): Helpful votes
```

### Menu & Ordering System

#### `menus` (Menu Management)
Restaurant menu structure.
```sql
Key Fields:
- id (uuid, PK): Menu identifier
- restaurant_id (uuid, FK → restaurants): Restaurant association
- name (text): Menu name
- description (text): Menu description
- menu_type (text): Menu category
- is_active (boolean): Menu availability
- display_order (integer): Sort order
- availability_schedule (jsonb): Time-based availability
```

#### `menu_sections` (Menu Organization)
Menu section organization.
```sql
Key Fields:
- id (uuid, PK): Section identifier
- menu_id (uuid, FK → menus): Menu association
- name (text): Section name
- description (text): Section description
- display_order (integer): Sort order
- is_active (boolean): Section availability
```

#### `menu_items` (Menu Items)
Individual menu items.
```sql
Key Fields:
- id (uuid, PK): Item identifier
- menu_section_id (uuid, FK → menu_sections): Section association
- name (text): Item name
- description (text): Item description
- price (numeric): Item price
- dietary_info (text[]): Dietary information
- allergens (text[]): Allergen information
- preparation_time (integer): Prep time in minutes
- is_available (boolean): Current availability
- image_url (text): Item image
```

### Staff Scheduling System

#### `staff_schedules` (Schedule Templates)
Staff scheduling framework.
```sql
Key Fields:
- id (uuid, PK): Schedule identifier
- restaurant_id (uuid, FK → restaurants): Restaurant association
- staff_id (uuid, FK → restaurant_staff): Staff member
- name (text): Schedule name
- description (text): Schedule description
- schedule_type (text): Type (weekly/monthly/one_time)
- start_date (date): Schedule start
- end_date (date): Schedule end
- is_active (boolean): Schedule status
- created_by (uuid, FK → profiles): Creator
```

#### `staff_shifts` (Individual Shifts)
Specific shift assignments.
```sql
Key Fields:
- id (uuid, PK): Shift identifier
- restaurant_id (uuid, FK → restaurants): Restaurant association
- staff_id (uuid, FK → restaurant_staff): Staff member
- schedule_id (uuid, FK → staff_schedules): Schedule reference
- shift_date (date): Shift date
- start_time (time): Shift start
- end_time (time): Shift end
- break_duration_minutes (integer): Break time
- role (text): Shift role
- station (text): Work station
- notes (text): Shift notes
- status (text): Shift status
- hourly_rate (numeric): Shift pay rate
```

#### `time_clock_entries` (Time Tracking)
Staff time clock system.
```sql
Key Fields:
- id (uuid, PK): Entry identifier
- restaurant_id (uuid, FK → restaurants): Restaurant association
- staff_id (uuid, FK → restaurant_staff): Staff member
- shift_id (uuid, FK → staff_shifts): Related shift
- clock_in_time (timestamptz): Clock in time
- clock_out_time (timestamptz): Clock out time
- break_start_time (timestamptz): Break start
- break_end_time (timestamptz): Break end
- total_hours (numeric): Calculated hours
- total_break_minutes (integer): Break duration
- overtime_hours (numeric): Overtime hours
- gross_pay (numeric): Calculated pay
- location_clock_in (jsonb): Clock in location
- location_clock_out (jsonb): Clock out location
- status (text): Entry status
```

### Kitchen Operations

#### `kitchen_stations` (Kitchen Organization)
Kitchen work station definitions.
```sql
Key Fields:
- id (uuid, PK): Station identifier
- restaurant_id (uuid, FK → restaurants): Restaurant association
- name (text): Station name
- description (text): Station description
- station_type (text): Station category
- is_active (boolean): Station status
- equipment (text[]): Station equipment
- specialties (text[]): Station specialties
```

#### `orders` (Order Management)
Customer order tracking.
```sql
Key Fields:
- id (uuid, PK): Order identifier
- booking_id (uuid, FK → bookings): Related booking
- restaurant_id (uuid, FK → restaurants): Restaurant association
- order_number (text): Display order number
- status (text): Order status
- subtotal (numeric): Pre-tax total
- tax_amount (numeric): Tax calculation
- service_charge (numeric): Service fees
- discount_amount (numeric): Applied discounts
- total_amount (numeric): Final total
- payment_status (text): Payment status
- special_instructions (text): Order notes
```

### Social Features

#### `posts` (Social Posts)
User-generated content and social sharing.
```sql
Key Fields:
- id (uuid, PK): Post identifier
- user_id (uuid, FK → profiles): Post author
- restaurant_id (uuid, FK → restaurants): Featured restaurant
- booking_id (uuid, FK → bookings): Related booking
- content (text): Post content
- media_urls (text[]): Attached media
- post_type (text): Content type
- is_public (boolean): Visibility setting
- like_count (integer): Engagement metric
- comment_count (integer): Comment count
```

### Database Functions & Procedures

#### Availability Functions
- **`check_table_availability()`**: Basic availability check
- **`get_available_tables()`**: Comprehensive table search
- **`get_booked_tables_for_slot()`**: Conflict detection
- **`verify_table_availability()`**: Detailed availability verification

#### Booking Functions
- **`create_booking_with_tables()`**: Full booking creation with validation
- **`create_booking_with_tables_debug()`**: Debug version with detailed logging
- **`fix_booking_without_tables()`**: Auto-assign tables to bookings

#### Optimization Functions
- **`suggest_optimal_tables()`**: AI-powered table recommendations
- **`validate_table_combination()`**: Combination validation
- **`cleanup_orphaned_booking_tables()`**: Data integrity maintenance

#### Reporting Functions
- **`get_table_availability_by_hour()`**: Hourly availability reports
- **`get_table_utilization_report()`**: Utilization analytics

### Security & Permissions

#### Row Level Security (RLS)
Most tables implement RLS policies to ensure data isolation between restaurants and proper user access control.

#### Staff Permission System
- **`staff_permission_templates`**: Permission templates
- Staff roles with granular permissions
- Restaurant-specific access control

### Key Business Rules

#### Table Assignment Priority
1. **Single Table Preference**: Always try single table first
2. **Capacity Optimization**: Prefer tables closest to party size
3. **Priority Scoring**: Use priority_score for tiebreaking
4. **Combination Logic**: Only combine when single table unavailable

#### Booking Validation
1. **Time Conflicts**: Check overlapping bookings
2. **Capacity Limits**: Validate party size against table capacity
3. **Advance Booking**: Respect booking window limits
4. **VIP Treatment**: Extended booking windows for VIP customers

#### Waitlist Management
1. **Automatic Conversion**: Convert waitlist to bookings when available
2. **Notification Windows**: Time-limited response windows
3. **Priority Queuing**: VIP and loyalty tier prioritization

### Database Performance Optimizations

#### Indexes
- Composite indexes on booking_time + restaurant_id
- Spatial indexes for location-based queries
- Full-text search indexes for restaurant discovery

#### Materialized Views
- `mv_table_availability`: Cached availability calculations
- Refresh strategies for real-time updates

#### Advanced Features

#### Extensions Installed
- **PostGIS**: Geospatial operations
- **pg_cron**: Scheduled tasks
- **uuid-ossp**: UUID generation
- **pgcrypto**: Cryptographic functions
- **pg_stat_statements**: Performance monitoring

#### Integration Points
- **Expo Push Notifications**: Mobile notifications
- **Payment Processing**: Transaction handling
- **Social Media**: Content sharing
- **Analytics**: Business intelligence

### Maintenance & Operations

#### Data Cleanup Functions
- Orphaned record cleanup
- Archive old bookings
- Manage waitlist expiration

#### Monitoring & Alerts
- Table utilization tracking
- Booking conversion rates
- Customer satisfaction metrics
- Staff performance analytics

---

## Summary

This RMS database provides a comprehensive restaurant management solution with:

1. **Intelligent Table Management**: AI-powered table recommendations
2. **Advanced Booking System**: Full lifecycle booking management
3. **Customer Relationship Management**: Detailed customer profiles and preferences
4. **Staff Operations**: Complete workforce management
5. **Loyalty & Rewards**: Flexible loyalty program framework
6. **Social Integration**: User-generated content and social features
7. **Analytics & Reporting**: Comprehensive business intelligence

The system is designed for scalability, performance, and flexibility to accommodate various restaurant types and operational models.
