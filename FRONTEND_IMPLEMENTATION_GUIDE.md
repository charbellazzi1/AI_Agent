# 🎯 Frontend Implementation Guide: JWT Authentication for AI

## 📋 Summary for Frontend Engineer

The backend AI system now requires JWT authentication to work with Row Level Security (RLS). You need to update API calls to include the user's JWT token in the Authorization header.

## 🔧 Required Changes

### 1. **Customer Chat API Updates**

**Location**: Your customer chat component (where users interact with restaurant AI)

**BEFORE** (Current Implementation):
```javascript
const sendMessageToAI = async (message) => {
  const response = await fetch('/api/chat', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      message: message,
      conversation_history: conversationHistory,
      session_id: sessionId
    })
  });
  
  return await response.json();
};
```

**AFTER** (Updated Implementation):
```javascript
const sendMessageToAI = async (message) => {
  // Get current user session
  const { data: { session } } = await supabase.auth.getSession();
  
  const headers = {
    'Content-Type': 'application/json',
  };
  
  // Add JWT token if user is authenticated
  if (session?.access_token) {
    headers['Authorization'] = `Bearer ${session.access_token}`;
  }
  
  const response = await fetch('/api/chat', {
    method: 'POST',
    headers: headers,
    body: JSON.stringify({
      message: message,
      conversation_history: conversationHistory,
      session_id: sessionId,
      user_id: session?.user?.id // Add user ID for personalization
    })
  });
  
  return await response.json();
};
```

### 2. **Staff Chat API Updates**

**Location**: Your staff/admin chat component (where restaurant staff interact with AI)

**BEFORE** (Current Implementation):
```javascript
const sendStaffMessage = async (message, restaurantId) => {
  const response = await fetch('/api/staff/chat', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      message: message,
      restaurant_id: restaurantId,
      conversation_history: conversationHistory,
      session_id: sessionId
    })
  });
  
  return await response.json();
};
```

**AFTER** (Updated Implementation):
```javascript
const sendStaffMessage = async (message, restaurantId) => {
  // Get current user session
  const { data: { session } } = await supabase.auth.getSession();
  
  const headers = {
    'Content-Type': 'application/json',
  };
  
  // Add JWT token if user is authenticated
  if (session?.access_token) {
    headers['Authorization'] = `Bearer ${session.access_token}`;
  }
  
  const response = await fetch('/api/staff/chat', {
    method: 'POST',
    headers: headers,
    body: JSON.stringify({
      message: message,
      restaurant_id: restaurantId,
      conversation_history: conversationHistory,
      session_id: sessionId,
      user_id: session?.user?.id // Add user ID for audit trail
    })
  });
  
  return await response.json();
};
```

### 3. **Helper Function (Recommended)**

Create a reusable helper function to handle authenticated API calls:

```javascript
// utils/aiApi.js
export const makeAuthenticatedAICall = async (endpoint, payload) => {
  try {
    // Get current user session
    const { data: { session } } = await supabase.auth.getSession();
    
    const headers = {
      'Content-Type': 'application/json',
    };
    
    // Add JWT token if available
    if (session?.access_token) {
      headers['Authorization'] = `Bearer ${session.access_token}`;
    }
    
    // Add user context to payload
    const enrichedPayload = {
      ...payload,
      user_id: session?.user?.id
    };
    
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: headers,
      body: JSON.stringify(enrichedPayload)
    });
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    return await response.json();
    
  } catch (error) {
    console.error('AI API call failed:', error);
    throw error;
  }
};

// Usage in components:
import { makeAuthenticatedAICall } from '../utils/aiApi';

// Customer chat
const result = await makeAuthenticatedAICall('/api/chat', {
  message: userMessage,
  conversation_history: conversationHistory,
  session_id: sessionId
});

// Staff chat  
const result = await makeAuthenticatedAICall('/api/staff/chat', {
  message: userMessage,
  restaurant_id: restaurantId,
  conversation_history: conversationHistory,
  session_id: sessionId
});
```

### 4. **Error Handling Updates**

Add proper error handling for authentication-related issues:

```javascript
const handleAIResponse = async (message) => {
  try {
    const result = await sendMessageToAI(message);
    
    // Handle successful response
    setAIResponse(result.response);
    if (result.restaurants_to_show) {
      setRestaurantsToShow(result.restaurants_to_show);
    }
    
  } catch (error) {
    if (error.message.includes('401')) {
      // Token expired or invalid
      alert('Your session has expired. Please log in again.');
      // Optionally redirect to login
      // navigation.navigate('Login');
      
    } else if (error.message.includes('403')) {
      // User doesn't have permission
      alert('You don\'t have permission to access this feature.');
      
    } else {
      // Other errors
      console.error('AI request failed:', error);
      alert('Sorry, there was an error processing your request.');
    }
  }
};
```

### 5. **User Experience Considerations**

**For Unauthenticated Users:**
- AI will still work but with limited functionality
- Consider showing a message like: "Sign in for personalized recommendations and booking features"

**For Authenticated Users:**
- AI gets full access to user's data and permissions
- Personalized responses based on user history

```javascript
const ChatInterface = () => {
  const [user, setUser] = useState(null);
  
  useEffect(() => {
    // Check authentication status
    const checkAuth = async () => {
      const { data: { session } } = await supabase.auth.getSession();
      setUser(session?.user || null);
    };
    
    checkAuth();
  }, []);
  
  return (
    <View>
      {!user && (
        <Text style={styles.authNotice}>
          💡 Sign in for personalized recommendations and booking features
        </Text>
      )}
      
      {/* Your chat interface */}
      <ChatComponent />
    </View>
  );
};
```

## 🧪 Testing Your Implementation

### Test Cases to Verify:

1. **Authenticated User Chat:**
   ```javascript
   // User is logged in
   await supabase.auth.signInWithPassword({ email, password });
   // Send message - should work with full functionality
   ```

2. **Unauthenticated User Chat:**
   ```javascript
   // User is not logged in
   await supabase.auth.signOut();
   // Send message - should work with limited functionality
   ```

3. **Staff Chat (Authenticated):**
   ```javascript
   // Staff user is logged in
   // Send staff message - should access restaurant data
   ```

## 🔍 How to Test

1. **Before implementing**: Test current chat functionality
2. **After implementing**: Verify both authenticated and unauthenticated scenarios work
3. **Check browser network tab**: Ensure `Authorization: Bearer <token>` header is present
4. **Test session expiry**: Verify proper error handling when tokens expire

## ⚠️ Important Notes

- **Backward Compatibility**: The API still works without JWT tokens (graceful degradation)
- **No Breaking Changes**: Existing functionality continues to work
- **Security**: JWT tokens are automatically handled by Supabase auth
- **Performance**: No impact on response times

## 🎯 Expected Benefits After Implementation

1. **Enhanced Security**: AI respects user permissions and RLS policies
2. **Personalization**: AI can access user-specific data (bookings, preferences)
3. **Staff Features**: Restaurant staff get access to operational data
4. **Audit Trail**: All AI interactions are logged with real user identity

## 📞 Support

If you encounter any issues:
1. Check browser console for error messages
2. Verify JWT token is being sent in Authorization header
3. Test with both authenticated and unauthenticated users
4. Reach out if you need clarification on any implementation details

**This is a straightforward addition - just add the Authorization header to existing API calls!** 🚀
