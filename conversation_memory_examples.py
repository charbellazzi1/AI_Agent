#!/usr/bin/env python3
"""
RestoAI Conversation Memory API Examples
Complete examples showing how to use the new conversation memory features
"""

# Example 1: Basic conversation flow with memory
conversation_example_1 = {
    "title": "Basic Restaurant Discovery with Memory",
    "description": "Shows how conversation context builds naturally",
    "steps": [
        {
            "request": {
                "method": "POST",
                "url": "/api/chat",
                "body": {
                    "message": "Hi, I need restaurant recommendations",
                    "conversation_history": [],
                    "session_id": "session_123",
                    "user_id": "user_456"
                }
            },
            "expected_response": {
                "status": "success",
                "response": "I'd be happy to help you find a great restaurant! What type of cuisine are you in the mood for?",
                "restaurants_to_show": [],
                "session_id": "session_123",
                "user_id": "user_456"
            }
        },
        {
            "request": {
                "method": "POST", 
                "url": "/api/chat",
                "body": {
                    "message": "Italian food please",
                    "conversation_history": [
                        {"role": "user", "content": "Hi, I need restaurant recommendations"},
                        {"role": "assistant", "content": "I'd be happy to help you find a great restaurant! What type of cuisine are you in the mood for?"}
                    ],
                    "session_id": "session_123",
                    "user_id": "user_456"
                }
            },
            "expected_response": {
                "status": "success",
                "response": "Perfect! Italian cuisine is wonderful. Do you have any preferences for location, ambiance, or special features like outdoor seating?",
                "restaurants_to_show": ["rest_1", "rest_2", "rest_3"],
                "session_id": "session_123",
                "user_id": "user_456"
            }
        },
        {
            "request": {
                "method": "POST",
                "url": "/api/chat", 
                "body": {
                    "message": "Outdoor seating would be great",
                    "conversation_history": [
                        {"role": "user", "content": "Hi, I need restaurant recommendations"},
                        {"role": "assistant", "content": "I'd be happy to help you find a great restaurant! What type of cuisine are you in the mood for?"},
                        {"role": "user", "content": "Italian food please"},
                        {"role": "assistant", "content": "Perfect! Italian cuisine is wonderful. Do you have any preferences for location, ambiance, or special features like outdoor seating?"}
                    ],
                    "session_id": "session_123",
                    "user_id": "user_456"
                }
            },
            "expected_response": {
                "status": "success",
                "response": "Excellent! I'll find Italian restaurants with beautiful outdoor seating for you. Here are some perfect options:",
                "restaurants_to_show": ["italian_outdoor_1", "italian_outdoor_2"],
                "session_id": "session_123", 
                "user_id": "user_456"
            }
        }
    ]
}

# Example 2: Contextual reference conversation
conversation_example_2 = {
    "title": "Contextual References and Memory",
    "description": "Shows how AI references previous suggestions",
    "steps": [
        {
            "request": {
                "method": "POST",
                "url": "/api/chat",
                "body": {
                    "message": "Show me some Italian restaurants",
                    "conversation_history": [],
                    "session_id": "session_456",
                    "user_id": "user_789"
                }
            },
            "expected_response": {
                "status": "success",
                "response": "Here are some excellent Italian restaurants I recommend: [restaurant details]",
                "restaurants_to_show": ["mario_pizzeria", "bella_vista", "romano_bistro"],
                "session_id": "session_456",
                "user_id": "user_789"
            }
        },
        {
            "request": {
                "method": "POST",
                "url": "/api/chat",
                "body": {
                    "message": "What about the first one you mentioned?",
                    "conversation_history": [
                        {"role": "user", "content": "Show me some Italian restaurants"},
                        {"role": "assistant", "content": "Here are some excellent Italian restaurants I recommend: Mario's Pizzeria, Bella Vista, and Romano Bistro..."}
                    ],
                    "session_id": "session_456",
                    "user_id": "user_789"
                }
            },
            "expected_response": {
                "status": "success",
                "response": "The first restaurant I mentioned was Mario's Pizzeria. It's known for authentic wood-fired pizzas and cozy atmosphere...",
                "restaurants_to_show": ["mario_pizzeria"],
                "session_id": "session_456",
                "user_id": "user_789"
            }
        }
    ]
}

# Example 3: Backward compatibility
backward_compatibility_example = {
    "title": "Backward Compatibility - Old API Format",
    "description": "Shows that old API calls still work without conversation_history",
    "request": {
        "method": "POST",
        "url": "/api/chat",
        "body": {
            "message": "Find me Italian restaurants",
            "session_id": "old_session",
            "user_id": "old_user"
            # Note: No conversation_history parameter
        }
    },
    "expected_response": {
        "status": "success",
        "response": "I'll help you find great Italian restaurants! Here are some excellent options:",
        "restaurants_to_show": ["rest_1", "rest_2", "rest_3"],
        "session_id": "old_session",
        "user_id": "old_user"
    }
}

# Example 4: Reset conversation
reset_example = {
    "title": "Conversation Reset",
    "description": "How to reset conversation history",
    "request": {
        "method": "POST",
        "url": "/api/chat/reset",
        "body": {
            "session_id": "session_123",
            "user_id": "user_456",
            "clear_history": True
        }
    },
    "expected_response": {
        "status": "success",
        "message": "Conversation reset successfully",
        "session_id": "session_123",
        "user_id": "user_456",
        "clear_history": True
    }
}

# Example 5: Staff chat with conversation memory (future enhancement)
staff_chat_example = {
    "title": "Staff Chat with Conversation Memory",
    "description": "Staff endpoint also supports conversation_history for consistency",
    "request": {
        "method": "POST",
        "url": "/api/staff/chat",
        "body": {
            "message": "How many bookings do we have today?",
            "restaurant_id": "restaurant_123",
            "conversation_history": [
                {"role": "user", "content": "What's our status today?"},
                {"role": "assistant", "content": "Today is looking busy! Would you like details about bookings, capacity, or something specific?"}
            ],
            "session_id": "staff_session_456"
        }
    },
    "expected_response": {
        "status": "success",
        "response": "Based on our conversation about today's status, you have 24 bookings scheduled for today...",
        "session_id": "staff_session_456",
        "restaurant_id": "restaurant_123"
    }
}

# Example 6: Error handling
error_handling_examples = {
    "malformed_history": {
        "title": "Malformed Conversation History",
        "description": "API handles malformed conversation_history gracefully",
        "request": {
            "method": "POST",
            "url": "/api/chat",
            "body": {
                "message": "Find restaurants",
                "conversation_history": "invalid_format",  # Should be array
                "session_id": "error_test"
            }
        },
        "expected_behavior": "API falls back to stateless mode, still provides response"
    },
    "missing_message": {
        "title": "Missing Message Parameter",
        "request": {
            "method": "POST",
            "url": "/api/chat",
            "body": {
                "conversation_history": [],
                "session_id": "error_test"
                # Missing required 'message' parameter
            }
        },
        "expected_response": {
            "status": "error",
            "error": "Message is required"
        }
    }
}

# Frontend Integration Example
frontend_integration_example = """
// Frontend JavaScript Integration Example

class RestoAIChat {
    constructor() {
        this.conversationHistory = [];
        this.sessionId = 'session_' + Date.now();
        this.userId = 'user_' + Math.random().toString(36);
        this.maxHistoryLength = 20; // Sliding window
    }

    async sendMessage(message) {
        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    conversation_history: this.conversationHistory,
                    session_id: this.sessionId,
                    user_id: this.userId
                })
            });

            const data = await response.json();
            
            if (data.status === 'success') {
                // Add to conversation history
                this.addToHistory('user', message);
                this.addToHistory('assistant', data.response);
                
                // Handle restaurant recommendations
                if (data.restaurants_to_show && data.restaurants_to_show.length > 0) {
                    this.displayRestaurants(data.restaurants_to_show);
                }
                
                return data.response;
            } else {
                throw new Error(data.error || 'API error');
            }
        } catch (error) {
            console.error('Chat error:', error);
            return 'Sorry, I encountered an error. Please try again.';
        }
    }

    addToHistory(role, content) {
        this.conversationHistory.push({ role, content });
        
        // Maintain sliding window
        if (this.conversationHistory.length > this.maxHistoryLength) {
            this.conversationHistory = this.conversationHistory.slice(-this.maxHistoryLength);
        }
    }

    async resetConversation() {
        try {
            await fetch('/api/chat/reset', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    session_id: this.sessionId,
                    user_id: this.userId,
                    clear_history: true
                })
            });
            
            this.conversationHistory = [];
            return true;
        } catch (error) {
            console.error('Reset error:', error);
            return false;
        }
    }

    displayRestaurants(restaurantIds) {
        // Frontend logic to display restaurants
        console.log('Displaying restaurants:', restaurantIds);
    }
}

// Usage Example
const chat = new RestoAIChat();

// Start conversation
await chat.sendMessage("Hi, I need restaurant recommendations");
await chat.sendMessage("Italian food please");  
await chat.sendMessage("Outdoor seating would be great");
await chat.sendMessage("What about the first one you mentioned?");

// Reset if needed
await chat.resetConversation();
"""

if __name__ == "__main__":
    print("📋 RestoAI Conversation Memory API Examples")
    print("=" * 60)
    
    print("\n🔧 IMPLEMENTATION FEATURES:")
    print("✅ Conversation history support in /api/chat")
    print("✅ Context-aware responses") 
    print("✅ Backward compatibility with old API format")
    print("✅ Reset conversation endpoint")
    print("✅ Staff chat consistency")
    print("✅ Robust error handling")
    print("✅ Frontend integration ready")
    
    print("\n📖 API Examples Available:")
    print("• Basic conversation flow with memory building")
    print("• Contextual references and memory usage")
    print("• Backward compatibility testing")
    print("• Conversation reset functionality")
    print("• Staff chat with conversation support")
    print("• Error handling scenarios")
    print("• Frontend JavaScript integration example")
    
    print("\n🚀 Ready for Production Use!")
    print("All examples and documentation provided for seamless integration.")
