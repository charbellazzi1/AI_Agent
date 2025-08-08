# AI Agent Restaurant System - Developer Guide

## Architecture Overview

This is a **dual AI agent system** for restaurant operations:

- **`AI_Agent.py`**: Customer-facing agent for restaurant discovery and booking
- **`AI_Agent_Restaurant.py`**: Staff-facing agent for operational assistance and customer service
- **`flask_api_ai.py`**: Unified Flask API serving both agents via different endpoints

Both agents use **LangChain + LangGraph** with **Google Gemini** LLM and **Supabase** database.

## Critical Patterns & Conventions

### Tool-Based Architecture
Both agents follow a mandatory tool workflow:
```python
# All tools must call this when done gathering data
@tool
def finishedUsingTools() -> str:
    """Call this when you're done using tools and ready to respond."""
    return "Tools usage completed."
```

### Database Integration Patterns
- Use specific column selections for performance: `select("id, name, cuisine_type")`
- Tools return JSON strings, not objects: `return json.dumps(data)`
- Staff agent queries include `restaurant_id` filtering
- Customer queries use `.ilike()` for case-insensitive search

### Response Formatting Requirements

**Customer Agent** must format restaurant recommendations:
```python
# Required format for UI integration
"I found great Italian restaurants!
RESTAURANTS_TO_SHOW: restaurant-1,restaurant-2,restaurant-3"
```

**Staff Agent** returns structured operational data in JSON format.

## Key Tools by Agent

### Customer Agent (`AI_Agent.py`)
- `getAllRestaurants()` - Get all restaurants with ai_featured prioritization
- `getRestaurantsByCuisineType(cuisineType)` - Filter by cuisine
- `getAllCuisineTypes()` - Available cuisine options

### Staff Agent (`AI_Agent_Restaurant.py`)
- `getTodaysBookings(restaurant_id)` - Today's reservations with customer data
- `getAvailableTables(restaurant_id, time, party_size)` - Smart table availability
- `getCustomerHistory(identifier, restaurant_id)` - Customer preferences & history
- `getTableSuggestions(restaurant_id, party_size, preferences)` - AI-powered seating recommendations
- `getRestaurantStats(restaurant_id, period)` - Operational analytics
- `checkBookingDetails(confirmation_code)` - Booking lookup

## Development Workflows

### Local Testing
```bash
# Test staff agent directly
python AI_Agent_Restaurant.py

# Test customer agent directly  
python AI_Agent.py

# Run Flask API locally
python flask_api_ai.py
```

### Environment Setup
Required environment variables:
```env
GOOGLE_API_KEY=your-gemini-api-key
EXPO_PUBLIC_SUPABASE_URL=your-supabase-url
EXPO_PUBLIC_SUPABASE_ANON_KEY=your-supabase-anon-key
```

### Database Schema Dependencies
**CRITICAL**: Always reference `database-schema.md` for complete schema documentation, relationships, and query patterns. This file contains:
- Complete table relationships and foreign keys
- Column selection patterns for optimal performance  
- AI agent-specific query examples
- Common data types and constraints

Key tables: `restaurants`, `bookings`, `restaurant_tables`, `restaurant_customers`, `profiles`, `customer_notes`, `booking_tables`, `table_combinations`

**Schema Update Protocol**: When database schema changes, update `database-schema.md` first, then modify affected AI tools and column selection strings.

## Deployment & Integration

- **Vercel deployment** via `vercel.json` configuration
- **Stateless requests** - no server-side conversation history
- **Graceful fallbacks** - API returns error states when AI agents unavailable
- **Frontend integration** expects specific JSON response formats

## Error Handling Pattern
```python
try:
    # Database/API operation
    result = supabase.table("table").select().execute()
    return json.dumps(result.data)
except Exception as e:
    return f"Error description: {str(e)}"
```

## Testing Approach
- Interactive chat functions in both agent files for immediate testing
- Flask API provides health checks and graceful degradation
- Tool responses logged for debugging: `print(f"AI is looking for...")`
