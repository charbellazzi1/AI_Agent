# RLS Authentication Solution for AI Agents

## Problem
With Row Level Security (RLS) enabled on Supabase tables, the AI agents cannot access data because they're using the anonymous key without user context.

## Solution Architecture

### 1. Frontend Changes Required

**For Customer Chat API (`/api/chat`):**
```javascript
// Add JWT token to requests
const { data: { session } } = await supabase.auth.getSession();

const response = await fetch('/api/chat', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${session?.access_token}` // Add this
  },
  body: JSON.stringify({
    message: userMessage,
    conversation_history: conversationHistory,
    session_id: sessionId,
    user_id: session?.user?.id // Add this
  })
});
```

**For Staff Chat API (`/api/staff/chat`):**
```javascript
// Add JWT token and restaurant context
const { data: { session } } = await supabase.auth.getSession();

const response = await fetch('/api/staff/chat', {
  method: 'POST', 
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${session?.access_token}` // Add this
  },
  body: JSON.stringify({
    message: userMessage,
    conversation_history: conversationHistory,
    restaurant_id: restaurantId, // Make sure this is included
    session_id: sessionId,
    user_id: session?.user?.id // Add this
  })
});
```

### 2. Backend Authentication Middleware

The Flask API will:
- Extract JWT tokens from Authorization headers
- Create authenticated Supabase clients for each request
- Pass these clients to AI agents
- Ensure AI operates with user's privileges

### 3. AI Agent Updates

Both AI agents will:
- Accept authenticated Supabase clients instead of using global anonymous client
- Automatically inherit user's RLS permissions
- Work transparently with existing tools

### 4. RLS Policy Considerations

For tables the AI needs to access, ensure policies allow:
- **Customer AI**: Access to restaurants, availability, reviews (public data)
- **Staff AI**: Access to restaurant-specific data based on staff permissions

## Benefits

1. **Security**: AI respects user permissions and RLS policies
2. **Compliance**: All data access follows your existing security model
3. **Transparency**: Clear audit trail of who accessed what data
4. **Scalability**: Works with any RLS policy changes automatically

## Implementation Steps

1. Update Flask API with JWT authentication middleware
2. Modify AI agents to accept authenticated clients
3. Update frontend to send JWT tokens
4. Test with different user roles and permissions
5. Add fallback handling for unauthenticated requests

## Testing Strategy

1. Test with regular users (should see public restaurant data)
2. Test with staff users (should see restaurant-specific data)  
3. Test with managers (should see broader restaurant access)
4. Test with unauthenticated requests (should gracefully degrade)
