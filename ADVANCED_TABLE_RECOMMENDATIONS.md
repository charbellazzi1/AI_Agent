# Advanced Table Recommendation System

## Overview

The staff AI agent now includes an advanced table recommendation system that leverages your RMS database's `suggest_optimal_tables` PostgreSQL function. This provides sophisticated, database-level algorithms for intelligent table selection.

## Key Features

### 1. Database-Level Intelligence
- Uses the `suggest_optimal_tables` stored procedure from your RMS database
- Implements sophisticated two-phase algorithm:
  - **Phase 1**: Single table search with capacity optimization
  - **Phase 2**: Table combination logic for larger parties
- Real-time availability checking against current bookings

### 2. Advanced Capabilities
- **Capacity Optimization**: Finds tables with closest capacity match using `ABS(capacity - party_size)` scoring
- **Priority Scoring**: Considers table priority scores and features
- **Combination Intelligence**: Automatically suggests table combinations when needed
- **Validation System**: Validates table combinations using database business rules
- **Hourly Reporting**: Generates detailed availability reports for operational planning

## New Tools Added

### `getOptimalTableRecommendations`
**Primary tool for table recommendations** - Use this instead of the legacy `getTableSuggestions`.

```python
# Usage example
getOptimalTableRecommendations(
    restaurant_id="your-restaurant-id",
    party_size=4,
    booking_time="2024-08-27T19:00:00Z",
    turn_time_minutes=120  # Optional, defaults to 120
)
```

**Response Format:**
```json
{
    "status": "success",
    "party_size": 4,
    "requested_time": "2024-08-27T19:00:00Z",
    "total_capacity": 4,
    "requires_combination": false,
    "recommended_tables": [
        {
            "id": "table-uuid",
            "table_number": "5",
            "table_type": "standard",
            "capacity": 4,
            "features": ["window"],
            "priority_score": 10
        }
    ],
    "table_count": 1,
    "algorithm_notes": {
        "selection_method": "single_table",
        "optimization": "closest_capacity_match_with_priority_scoring"
    }
}
```

### `validateTableCombination`
Validates if specific tables can be combined for a party.

```python
validateTableCombination(
    restaurant_id="your-restaurant-id",
    table_ids="table-1-uuid,table-2-uuid",  # Comma-separated string
    party_size=8
)
```

### `getTableAvailabilityReport`
Generates hourly availability reports for operational planning.

```python
getTableAvailabilityReport(
    restaurant_id="your-restaurant-id",
    date="2024-08-27"
)
```

## Usage Patterns

### 1. Staff Asking for Table Recommendations
**Staff Query**: "What's the best table for a party of 6 at 7:30 PM?"

**AI Response**: The agent will use `getOptimalTableRecommendations` and provide:
- Specific table numbers and types
- Whether table combination is needed
- Total capacity explanation
- Why these tables were selected

### 2. Large Party Management
**Staff Query**: "I need seating for 12 people tonight at 8 PM"

**AI Response**: The system will:
- Use the combination algorithm to find suitable table groups
- Validate the combinations using database rules
- Provide clear setup instructions

### 3. Operational Planning
**Staff Query**: "Show me today's hourly availability"

**AI Response**: Generates comprehensive report with:
- Peak hours identification
- Quiet periods
- Utilization percentages
- Planning recommendations

## Technical Integration

### Database Functions Used
1. **`suggest_optimal_tables`**: Main recommendation algorithm
   - Parameters: `p_restaurant_id`, `p_party_size`, `p_start_time`, `p_end_time`
   - Returns: `table_ids[]`, `total_capacity`, `requires_combination`

2. **`validate_table_combination`**: Combination validation
   - Parameters: `p_table_ids[]`, `p_party_size`
   - Returns: `is_valid`, `total_capacity`, `validation_message`

3. **`get_table_availability_by_hour`**: Hourly reporting
   - Parameters: `p_restaurant_id`, `p_date`
   - Returns: Hourly availability data with utilization metrics

### Error Handling
The system gracefully handles:
- No available tables for requested criteria
- Database connection issues
- Invalid party sizes or time ranges
- Table combination validation failures

## Migration from Legacy System

### Before (Legacy)
```python
# Old approach using getTableSuggestions
getTableSuggestions(restaurant_id, party_size, preferences)
```

### After (Advanced)
```python
# New approach using database-level algorithm
getOptimalTableRecommendations(restaurant_id, party_size, booking_time)
```

### Benefits of Migration
- **More Accurate**: Uses real-time database data and sophisticated algorithms
- **Better Performance**: Database-level optimization reduces processing time
- **Combination Logic**: Automatically handles complex table combinations
- **Validation**: Built-in validation prevents booking conflicts
- **Reporting**: Enhanced operational insights

## Testing

Use the provided test script to verify functionality:

```bash
python test_optimal_recommendations.py
```

For interactive testing:
```bash
python AI_Agent_Restaurant.py
# Ask: "What tables do you recommend for a party of 4 at 7 PM?"
```

## Configuration

Ensure your environment includes:
```env
EXPO_PUBLIC_SUPABASE_URL=your-rms-database-url
EXPO_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
```

The system automatically connects to your RMS database and uses the existing PostgreSQL functions.

## Best Practices

1. **Always use `getOptimalTableRecommendations`** for new table recommendation requests
2. **Keep `getTableSuggestions`** for backward compatibility but prefer the new system
3. **Use `validateTableCombination`** before confirming complex table setups
4. **Generate availability reports** during slow periods for better planning
5. **Test with real restaurant IDs** to ensure proper database connectivity

## Support

The system is designed to be backward compatible. If the new tools fail, the agent will fall back to legacy tools automatically. All responses include clear explanations of the recommendation logic for staff understanding.
