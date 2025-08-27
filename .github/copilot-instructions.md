# AI Agent Restaurant System - Developer Guide

## Architecture Overview

This is a **dual AI agent system** with **conversation memory** for restaurant operations:

- **`AI_Agent.py`**: Customer-facing agent for restaurant discovery and booking with contextual conversations
- **`AI_Agent_Restaurant.py`**: Staff-facing agent for operational assistance and customer service
- **`flask_api_ai.py`**: Unified Flask API serving both agents via different endpoints with conversation history support
- **`availability_tools.py`**: Shared table availability logic with timezone-aware operations

Both agents use **LangChain + LangGraph** with **Google Gemini** LLM and **Supabase** database.

## Critical Patterns & Conventions

### Tool-Based Architecture
Both agents follow a mandatory tool workflow pattern:
```python
# All tools must call this when done gathering data
@tool
def finishedUsingTools() -> str:
    """Call this when you're done using tools and ready to respond."""
    return "Tools usage completed."
```

### Conversation Memory System (NEW)
**Customer Agent** supports conversation history for contextual responses:
```python
# Frontend sends conversation history
conversation_history = [
    {"role": "user", "content": "Hi, I need restaurant recommendations"},
    {"role": "assistant", "content": "What type of cuisine are you interested in?"}
]

# Backend converts to LangChain messages and maintains context
memory = create_conversation_memory(max_history=20)
for msg in conversation_history:
    if msg['role'] == 'user':
        memory.add_message(HumanMessage(content=msg['content']))
    elif msg['role'] == 'assistant':
        memory.add_message(AIMessage(content=msg['content']))
```

### Database Integration Patterns
- Use specific column selections for performance: `select("id, name, cuisine_type")`
- Tools return JSON strings, not objects: `return json.dumps(data)`
- Staff agent queries include `restaurant_id` filtering
- Customer queries use `.ilike()` for case-insensitive search
- Always reference `database-schema.md` for schema relationships

### Response Formatting Requirements

**Customer Agent** must format restaurant recommendations:
```python
# Required format for UI integration
"I found great Italian restaurants!
RESTAURANTS_TO_SHOW: restaurant-1,restaurant-2,restaurant-3"
```

**Staff Agent** returns structured operational data in JSON format.

## Key API Endpoints

### Customer Chat (with Memory)
```json
POST /api/chat
{
  "message": "Find Italian restaurants with outdoor seating", 
  "conversation_history": [{"role": "user", "content": "Hi"}],
  "session_id": "session_123",
  "user_id": "user_456"
}
```

### Staff Chat (Memory Ready)
```json
POST /api/staff/chat  
{
  "message": "How many bookings today?",
  "conversation_history": [],
  "restaurant_id": "rest_123",
  "session_id": "staff_session"
}
```

### Conversation Reset
```json
POST /api/chat/reset
{
  "session_id": "session_123",
  "clear_history": true
}
```

## Development Workflows

### Local Testing & Interactive Mode
```bash
# Test customer agent directly (with conversation memory)
python AI_Agent.py

# Test staff agent directly  
python AI_Agent_Restaurant.py

# Run Flask API locally
python flask_api_ai.py

# Test conversation memory implementation
python test_memory_direct.py

# Production readiness verification
python final_production_test.py
```

### MCP (Model Context Protocol) Integration
**IMPORTANT**: Always check for available MCPs and use them when relevant to enhance development productivity.

**Check Available MCPs:**
- Use available MCP discovery tools to see what protocols are accessible
- Common useful MCPs may include: file operations, database tools, testing utilities, documentation helpers
- Leverage MCPs for tasks like code analysis, schema validation, API testing, or data manipulation

**When to Use MCPs:**
- Database schema operations and validation
- API endpoint testing and debugging  
- File system operations for configuration
- Documentation generation and updates
- Code quality and testing automation
- External service integrations

### Environment Setup
Required environment variables:
```env
GOOGLE_API_KEY=your-gemini-api-key
EXPO_PUBLIC_SUPABASE_URL=your-supabase-url  
EXPO_PUBLIC_SUPABASE_ANON_KEY=your-supabase-anon-key
AVAILABILITY_TZ=Asia/Beirut  # For table availability calculations
```

### Testing Advanced Table Recommendations
Use this test pattern for the new table recommendation system:
```bash
# Test advanced table recommendation tools
python test_optimal_recommendations.py

# Interactive testing with new tools
python AI_Agent_Restaurant.py
# Then ask: "What's the best table for a party of 4 at 7 PM?"
```

## Key Tools by Agent

### Customer Agent (`AI_Agent.py`)
- `getAllRestaurants()` - Get all restaurants with ai_featured prioritization
- `getRestaurantsByCuisineType(cuisineType)` - Filter by cuisine with context awareness
- `getAllCuisineTypes()` - Available cuisine options
- `convertRelativeDate(relative_date)` - Handle "today", "tomorrow" for availability queries

### Staff Agent (`AI_Agent_Restaurant.py`)  

#### Core Operations
- `getTodaysBookings(restaurant_id)` - Today's reservations with customer data
- `getAvailableTables(restaurant_id, time, party_size)` - Smart table availability
- `getCustomerHistory(identifier, restaurant_id)` - Customer preferences & history

#### Legacy Table Recommendations
- `getTableSuggestions(restaurant_id, party_size, preferences)` - AI-powered seating recommendations

#### **Advanced Table Recommendation System (NEW)**
- `getOptimalTableRecommendations(restaurant_id, party_size, booking_time, turn_time)` - **Primary tool for table recommendations using RMS database's suggest_optimal_tables function**
  - Uses sophisticated database-level algorithms
  - Real-time availability checking with capacity optimization  
  - Automatic table combination suggestions for larger parties
  - Priority scoring and closest capacity matching
- `validateTableCombination(table_ids, party_size)` - Validates table combinations using database business rules
- `getTableAvailabilityReport(restaurant_id, date)` - Generates hourly availability reports for operational planning

#### **Enhanced Table Display (LATEST UPDATE)**
**System prompt now instructs AI to show BOTH recommended and alternative tables:**
- Uses `getOptimalTableRecommendations()` for smart suggestions  
- Uses `getAvailableTables()` for complete alternatives
- Presents results in structured format:
  ```
  RECOMMENDED TABLES (Optimal choices):
  • Table 12 (4-seat booth) - Perfect size, quiet corner
  
  OTHER AVAILABLE TABLES:
  • Table 8 (6-seat round) - Slightly larger but available
  • Table 20 (8-seat) - Large table, good for celebrations
  ```
- Provides staff complete flexibility and transparency in table selection

#### Waitlist Management
- `getWaitlist(restaurant_id, status)` - Current waitlist entries
- `getWaitlistStats(restaurant_id)` - Waitlist summary statistics
- `estimateWaitTime(restaurant_id, party_size)` - Wait time estimates

#### Analytics & Reporting  
- `getRestaurantStats(restaurant_id, date_filter)` - Operational statistics
- `checkBookingDetails(confirmation_code, booking_id)` - Detailed booking information

## Error Handling & Graceful Degradation
```python
# Standard pattern for all tools
try:
    result = supabase.table("table").select().execute()
    return json.dumps(result.data)
except Exception as e:
    return f"Error description: {str(e)}"

# Flask API graceful fallbacks
if not AI_AVAILABLE:
    return jsonify({'error': 'AI functionality not available'}), 503
```

## Deployment & Production

- **Vercel deployment** via `vercel.json` configuration  
- **Stateless requests** with frontend-managed conversation history (20-message sliding window)
- **Backward compatibility** - API works with/without conversation_history parameter
- **Production testing** - Use `final_production_test.py` before deployment

## Recent Conversation Memory Implementation

The system now supports contextual conversations through:
- Frontend sends conversation history as array of `{"role": "user|assistant", "content": "..."}`
- Backend converts to LangChain message format for AI processing
- 20-message sliding window managed by frontend for performance
- Session-based persistence in frontend (8-hour staff shifts)
- Reset functionality for clearing conversation context

See `CONVERSATION_MEMORY_IMPLEMENTATION.md` for complete implementation details.
