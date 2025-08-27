# RMS Database Schema Relationships

## Database Entity Relationship Diagram (ERD) Key Relationships

### Core Entity Relationships

#### User Management Flow
```
profiles (users) 
    ↓ 1:N
user_devices (push notifications)
    ↓ 1:1
user_privacy_settings (privacy controls)
    ↓ 1:1
notification_preferences (notification settings)
```

#### Restaurant Hierarchy
```
restaurants (main restaurant)
    ↓ 1:N
restaurant_staff (employees)
    ↓ 1:N  
restaurant_tables (seating)
    ↓ N:1
restaurant_sections (table grouping)
    ↓ 1:N
floor_plans (layout visualization)
```

#### Booking Flow
```
profiles (customer)
    ↓ 1:N
bookings (reservations)
    ↓ N:N (via booking_tables)
restaurant_tables (assigned seating)
    ↓ 1:N
booking_status_history (audit trail)
```

#### Table Management System
```
restaurant_tables (individual tables)
    ↓ N:N (via table_combinations)
table_combinations (multi-table setups)
    ↓ Primary/Secondary FK relationships
restaurant_tables (combinable tables)
```

### Detailed Foreign Key Relationships

#### Booking System Relationships
```sql
-- Core booking relationships
bookings.user_id → profiles.id
bookings.restaurant_id → restaurants.id
bookings.organizer_id → profiles.id (group bookings)
bookings.applied_offer_id → special_offers.id
bookings.applied_loyalty_rule_id → restaurant_loyalty_rules.id

-- Table assignment relationships
booking_tables.booking_id → bookings.id
booking_tables.table_id → restaurant_tables.id

-- Status tracking relationships
booking_status_history.booking_id → bookings.id
booking_status_history.changed_by → profiles.id

-- Invitation relationships
booking_invites.booking_id → bookings.id
booking_invites.from_user_id → profiles.id
booking_invites.to_user_id → profiles.id
```

#### Restaurant Management Relationships
```sql
-- Restaurant configuration
restaurants.id → (many child tables)

-- Staff management
restaurant_staff.user_id → profiles.id
restaurant_staff.restaurant_id → restaurants.id

-- Table configuration
restaurant_tables.restaurant_id → restaurants.id
restaurant_tables.section_id → restaurant_sections.id

-- Section organization
restaurant_sections.restaurant_id → restaurants.id

-- Table combinations
table_combinations.restaurant_id → restaurants.id
table_combinations.primary_table_id → restaurant_tables.id
table_combinations.secondary_table_id → restaurant_tables.id
```

#### Customer Relationship Management
```sql
-- Customer profiles
restaurant_customers.restaurant_id → restaurants.id
restaurant_customers.user_id → profiles.id

-- Customer notes and preferences
customer_notes.customer_id → restaurant_customers.id
customer_notes.created_by → profiles.id

customer_preferences.customer_id → restaurant_customers.id

-- Customer relationships
customer_relationships.customer_id → restaurant_customers.id
customer_relationships.related_customer_id → restaurant_customers.id
customer_relationships.created_by → profiles.id

-- Customer tagging
customer_tags.restaurant_id → restaurants.id
customer_tag_assignments.customer_id → restaurant_customers.id
customer_tag_assignments.tag_id → customer_tags.id
customer_tag_assignments.assigned_by → profiles.id
```

#### Loyalty System Relationships
```sql
-- Loyalty rules
restaurant_loyalty_rules.restaurant_id → restaurants.id

-- Loyalty transactions
loyalty_activities.user_id → profiles.id
loyalty_activities.restaurant_id → restaurants.id
loyalty_activities.related_booking_id → bookings.id
loyalty_activities.related_review_id → reviews.id

-- Loyalty redemptions
loyalty_redemptions.user_id → profiles.id
loyalty_redemptions.restaurant_id → restaurants.id
loyalty_redemptions.booking_id → bookings.id
loyalty_redemptions.offer_id → special_offers.id

-- Usage tracking
user_loyalty_rule_usage.user_id → profiles.id
user_loyalty_rule_usage.rule_id → restaurant_loyalty_rules.id
user_loyalty_rule_usage.booking_id → bookings.id
```

#### Menu & Ordering System
```sql
-- Menu hierarchy
menus.restaurant_id → restaurants.id
menu_sections.menu_id → menus.id
menu_items.menu_section_id → menu_sections.id

-- Order management
orders.booking_id → bookings.id
orders.restaurant_id → restaurants.id
order_items.order_id → orders.id
order_items.menu_item_id → menu_items.id

-- Kitchen operations
kitchen_stations.restaurant_id → restaurants.id
kitchen_assignments.order_item_id → order_items.id
kitchen_assignments.station_id → kitchen_stations.id
kitchen_assignments.assigned_to → profiles.id
```

#### Staff Scheduling System
```sql
-- Schedule management
staff_schedules.restaurant_id → restaurants.id
staff_schedules.staff_id → restaurant_staff.id
staff_schedules.created_by → profiles.id

-- Shift assignments
staff_shifts.restaurant_id → restaurants.id
staff_shifts.staff_id → restaurant_staff.id
staff_shifts.schedule_id → staff_schedules.id
staff_shifts.created_by → profiles.id

-- Time tracking
time_clock_entries.restaurant_id → restaurants.id
time_clock_entries.staff_id → restaurant_staff.id
time_clock_entries.shift_id → staff_shifts.id
time_clock_entries.approved_by → profiles.id

-- Staff availability
staff_availability.restaurant_id → restaurants.id
staff_availability.staff_id → restaurant_staff.id

-- Time off requests
time_off_requests.restaurant_id → restaurants.id
time_off_requests.staff_id → restaurant_staff.id
time_off_requests.approved_by → profiles.id

-- Position management
staff_positions.restaurant_id → restaurants.id
staff_position_assignments.staff_id → restaurant_staff.id
staff_position_assignments.position_id → staff_positions.id
```

#### Waitlist System
```sql
-- Waitlist entries
waitlist.user_id → profiles.id
waitlist.restaurant_id → restaurants.id
waitlist.converted_booking_id → bookings.id
```

#### Review & Social System
```sql
-- Reviews
reviews.user_id → profiles.id
reviews.restaurant_id → restaurants.id
reviews.booking_id → bookings.id

-- Review replies
review_replies.review_id → reviews.id
review_replies.user_id → profiles.id

-- Social posts
posts.user_id → profiles.id
posts.restaurant_id → restaurants.id
posts.booking_id → bookings.id

-- User favorites
favorites.user_id → profiles.id
favorites.restaurant_id → restaurants.id

-- Friend system
friends.user_id → profiles.id
friends.friend_id → profiles.id

friend_requests.from_user_id → profiles.id
friend_requests.to_user_id → profiles.id
```

### Database Constraints & Business Rules

#### Data Integrity Constraints

##### Check Constraints
```sql
-- Booking constraints
bookings.party_size > 0
bookings.status IN ('pending', 'confirmed', 'cancelled_by_user', ...)

-- Table constraints  
restaurant_tables.capacity > 0
restaurant_tables.min_capacity <= restaurant_tables.max_capacity

-- Rating constraints
reviews.overall_rating >= 1 AND overall_rating <= 5
reviews.food_rating >= 1 AND food_rating <= 5
profiles.rating >= 1 AND rating <= 5

-- Waitlist constraints
waitlist.party_size > 0 AND party_size <= 20

-- Staff constraints
staff_availability.day_of_week >= 0 AND day_of_week <= 6
```

##### Unique Constraints
```sql
-- Booking system
bookings.confirmation_code (unique booking codes)
restaurant_tables(restaurant_id, table_number) (unique table numbers per restaurant)

-- User system
profiles.email (unique user emails)
user_devices(user_id, device_id) (unique device registrations)

-- Staff system
restaurant_staff(restaurant_id, user_id) (unique staff assignments)
```

##### Temporal Constraints
```sql
-- Time-based validations
bookings.booking_time > CURRENT_TIMESTAMP (future bookings only)
special_offers.valid_from < special_offers.valid_until
time_off_requests.start_date <= time_off_requests.end_date
staff_shifts.start_time < staff_shifts.end_time
```

#### Business Logic Constraints

##### Table Assignment Rules
1. **Single Table Priority**: Prefer single tables over combinations
2. **Capacity Matching**: Table capacity must accommodate party size
3. **Availability Checking**: No double-booking of tables
4. **Combination Rules**: Only combinable tables can be grouped

##### Booking Workflow Rules
1. **Status Progression**: Defined state transitions (pending → confirmed → seated → completed)
2. **Time Windows**: Respect advance booking limits
3. **VIP Treatment**: Extended booking windows for VIP customers
4. **Conflict Prevention**: No overlapping user bookings

##### Staff Scheduling Rules
1. **Shift Conflicts**: No overlapping shifts for same staff member
2. **Availability Matching**: Shifts must match staff availability
3. **Role Requirements**: Minimum staffing levels per shift
4. **Overtime Calculation**: Automatic overtime tracking

### Performance Optimization Indexes

#### Primary Query Patterns
```sql
-- Booking availability queries
CREATE INDEX idx_bookings_restaurant_time_status 
ON bookings(restaurant_id, booking_time, status);

-- Table availability queries  
CREATE INDEX idx_booking_tables_table_booking 
ON booking_tables(table_id, booking_id);

-- Restaurant discovery
CREATE INDEX idx_restaurants_location 
ON restaurants USING GIST(coordinates);

-- User booking history
CREATE INDEX idx_bookings_user_status_time 
ON bookings(user_id, status, booking_time DESC);

-- Staff scheduling
CREATE INDEX idx_staff_shifts_restaurant_date 
ON staff_shifts(restaurant_id, shift_date);

-- Loyalty activities
CREATE INDEX idx_loyalty_activities_user_restaurant 
ON loyalty_activities(user_id, restaurant_id, created_at DESC);
```

#### Composite Indexes for Complex Queries
```sql
-- Table availability with time overlap
CREATE INDEX idx_table_availability 
ON bookings(restaurant_id, booking_time, turn_time_minutes, status)
INCLUDE (id);

-- Customer relationship queries
CREATE INDEX idx_customer_restaurant_tier 
ON restaurant_customers(restaurant_id, customer_tier, last_visit DESC);

-- Review aggregation
CREATE INDEX idx_reviews_restaurant_verified 
ON reviews(restaurant_id, is_verified, overall_rating, created_at DESC);
```

### Data Consistency Patterns

#### Soft Delete Strategy
Many tables use status fields instead of hard deletes:
- `bookings.status` includes 'cancelled_by_user', 'cancelled_by_restaurant'
- `restaurant_tables.is_active` for table management
- `staff_shifts.status` for schedule management

#### Audit Trail Implementation
Key tables maintain change history:
- `booking_status_history` tracks all booking changes
- `user_rating_history` tracks rating changes
- Timestamp fields (`created_at`, `updated_at`) on most tables

#### Referential Integrity
- Foreign keys enforce relationships
- Cascade delete rules where appropriate
- Orphan cleanup functions for data maintenance

### Advanced Database Features

#### Stored Procedures & Functions
- Table recommendation algorithms
- Availability calculation functions
- Booking validation procedures
- Cleanup and maintenance routines

#### Triggers & Automation
- Automatic timestamp updates
- Status change notifications
- Data validation triggers
- Aggregation maintenance

#### Materialized Views
- Pre-calculated availability data
- Restaurant analytics aggregations
- Performance optimization for common queries

This schema design ensures data integrity, performance, and scalability while supporting complex restaurant management workflows and customer relationship management.
