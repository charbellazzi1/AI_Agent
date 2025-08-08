# 🍽️ Restaurant Staff AI Assistant

An intelligent AI assistant specifically designed to help restaurant staff work more efficiently and provide exceptional customer service.

## 🎯 Core Purpose

Help restaurant staff work smarter, not harder by providing instant access to:
- Table availability and smart assignment suggestions
- Customer history and preferences  
- Operational insights and statistics
- Quick answers to common staff questions

## ✨ Key Features

### 1. 🪑 Smart Table Assignment Helper
- **Intelligent Suggestions**: "Party of 4 → I recommend Table 12 (window seat, perfect size, available now)"
- **Customer Preferences**: Considers table type preferences, past seating choices
- **Real-time Availability**: Shows current table status and estimated turnover times
- **Table Combinations**: Suggests combining tables for larger parties

### 2. 🤝 Staff Decision Helper  
- **Capacity Questions**: "Can I fit a party of 6 at 7pm?" → "Yes! Combine tables 8+9, or wait 15 mins for table 15"
- **Complex Scenarios**: Helps with challenging seating situations and overbooking
- **Alternative Solutions**: Provides multiple options with pros/cons

### 3. 👤 Customer Context Assistant
- **VIP Recognition**: "John Smith - comes monthly, vegetarian, tips well, prefers quiet tables"
- **Dietary Restrictions**: Instant access to allergies and dietary preferences
- **Service History**: Previous visits, special occasions, preferences
- **Personalization Tips**: How to provide exceptional personalized service

### 4. 📊 Operations Insights
- **Real-time Stats**: Covers, bookings, peak times, table turnover
- **Proactive Alerts**: Long-seated tables, potential no-shows, timing issues
- **Performance Metrics**: No-show rates, average party sizes, busy periods

### 5. ⚡ Quick Operational Answers
- **Instant Information**: "How many covers tonight?", "What's our busiest time?", "Which tables are free?"
- **Booking Details**: Quick lookup by confirmation code or customer name
- **Current Status**: Real-time overview of restaurant operations

## 🚀 Implementation Options

### Option A: Chat Helper in Dashboard
```
Small chat widget in existing dashboard sidebar
Staff types questions while managing tables  
AI gives quick answers using restaurant's data
```

### Option B: Smart Notifications  
```
AI watches operations and sends helpful alerts
Shows up in existing notification system
Proactive suggestions to improve service
```

### Option C: Enhanced Table Management
```
Add AI suggestions to existing table assignment interface
When assigning tables, show: "💡 AI suggests: Table 7 (customer prefers window seats)"
```

## 🛠️ Technical Setup

### Files Structure
```
AI_Agent_Restaurant.py    # Main staff AI agent
flask_api_ai.py          # API endpoints for both customer and staff AI
demo_staff_ai.py         # Demo showing AI capabilities
test_staff_ai.py         # Testing script
test_api.py              # API testing client
```

### API Endpoints

#### Staff AI Chat
```http
POST /api/staff/chat
Content-Type: application/json

{
  "message": "How many covers do we have today?",
  "restaurant_id": "uuid-of-restaurant",
  "session_id": "optional-session-id"
}
```

Response:
```json
{
  "response": "📊 Today's Covers Summary: 89 guests, 23 bookings...",
  "session_id": "staff_session",
  "restaurant_id": "uuid-of-restaurant", 
  "status": "success"
}
```

#### Health Check
```http
GET /
```

Response:
```json
{
  "status": "healthy",
  "ai_available": true,
  "staff_ai_available": true,
  "environment_check": {...}
}
```

## 🎭 Real Restaurant Staff Use Cases

### Busy Friday Night
**Staff**: "AI, where can I seat this party of 8?"
**AI**: "Combine tables 15+16 (available now) or wait 10 minutes for table 20 (premium booth). Table 20 worth the wait for this party size."

### Customer Complaint
**Staff**: "Tell me about table 5's dining history"  
**AI**: "Sarah & Mike Johnson - 6th visit this year, usually wonderful experience. Last visit 3 weeks ago (5 stars). Wife has shellfish allergy - check if kitchen followed protocols."

### Planning
**Staff**: "How many staff do I need for Saturday dinner?"
**AI**: "Projected 120 covers, peak 7-8 PM (35 covers). Recommend 4 servers minimum, 5 preferred. Last Saturday similar volume worked well with 4."

### Service Recovery
**Staff**: "This customer had a bad experience last time - what happened?"
**AI**: "Table 8, party of 4, May 15th. Issues: 45-min wait despite reservation, wrong order delivered twice. Offered dessert comp. Customer left 2-star review mentioning poor communication."

## 🔧 Environment Setup

### Required Environment Variables
```bash
GOOGLE_API_KEY=your_google_ai_api_key
EXPO_PUBLIC_SUPABASE_URL=your_supabase_url  
EXPO_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
```

### Required Python Packages
```bash
pip install -r requirements.txt
```

### Database Requirements
The AI connects to your existing Supabase database and uses tables:
- `restaurants`
- `bookings` 
- `restaurant_tables`
- `restaurant_customers`
- `customer_notes`
- `booking_tables`
- `profiles`

## 🧪 Testing & Demo

### Run the Demo
```bash
python demo_staff_ai.py
```
Shows realistic AI responses with sample restaurant data.

### Test Live AI (requires valid restaurant UUID)
```bash
python test_staff_ai.py
```

### Test API
```bash
python flask_api_ai.py  # Start server
python test_api.py      # Test endpoints
```

## 🚀 Getting Started (Week by Week)

### Week 1: Basic Chat Integration
- Add chat widget to existing dashboard
- Connect to `/api/staff/chat` endpoint
- Staff can ask basic questions about bookings and tables

### Week 2: Customer Context
- Integrate customer lookup functionality
- Show AI suggestions when viewing booking details
- Add customer preference alerts

### Week 3: Smart Table Assignment  
- Add AI suggestions to table assignment interface
- Show recommended tables when seating customers
- Implement smart availability checks

### Week 4: Proactive Insights
- Add operational alerts and notifications
- Peak time staffing suggestions
- Performance insights dashboard

## 🔧 Customization

### Adding New Staff Tools
1. Create new tool function in `AI_Agent_Restaurant.py`
2. Add to tools list
3. Update system prompt with new capability
4. Test with staff scenarios

### Integrating with Existing Systems
- Use restaurant_id to filter data for specific location
- Connect to existing user authentication
- Integrate with current table management system
- Add to existing notification framework

## 📋 Staff Training

### Quick Reference Commands
```
"How many covers today?"
"Show me table availability" 
"Tell me about [customer name]"
"Can we fit a party of [X] at [time]?"
"What's our busiest time today?"
"Who's running late?"
"Suggest a table for [party size]"
```

### Best Practices
- Always include restaurant context in queries
- Use specific customer identifiers (name, phone, confirmation code)
- Ask for alternatives when first suggestion doesn't work
- Leverage customer history for personalized service

## 🎯 Success Metrics

Track these KPIs to measure AI impact:
- **Table Turn Time**: Faster assignments = more covers
- **Customer Satisfaction**: Better service through insights
- **Staff Efficiency**: Quick answers = more time for guests  
- **Revenue per Cover**: Personalized service = higher spend
- **No-show Reduction**: Proactive management

---

**Ready to revolutionize your restaurant operations? Start with the basic chat integration and grow from there!** 🚀
