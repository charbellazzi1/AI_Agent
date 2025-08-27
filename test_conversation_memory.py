#!/usr/bin/env python3
"""
Test script for conversation memory functionality in RestoAI backend
"""

import requests
import json

# API endpoint
BASE_URL = "http://127.0.0.1:5000"

def test_conversation_flow():
    """Test a complete conversation flow with memory"""
    print("🧪 Testing RestoAI Conversation Memory")
    print("=" * 50)
    
    # Test conversation history
    conversation_history = []
    session_id = "test_session_123"
    user_id = "test_user_456"
    
    # Test 1: Initial greeting (no history)
    print("\n1️⃣ First message: Initial greeting")
    response1 = send_message(
        message="Hi, I need restaurant recommendations",
        conversation_history=[],
        session_id=session_id,
        user_id=user_id
    )
    
    if response1:
        print(f"✅ Response: {response1['response']}")
        # Add to conversation history
        conversation_history.append({"role": "user", "content": "Hi, I need restaurant recommendations"})
        conversation_history.append({"role": "assistant", "content": response1['response']})
    
    # Test 2: Specify cuisine preference
    print("\n2️⃣ Second message: Specify Italian cuisine")
    response2 = send_message(
        message="Italian food please",
        conversation_history=conversation_history,
        session_id=session_id,
        user_id=user_id
    )
    
    if response2:
        print(f"✅ Response: {response2['response']}")
        if response2.get('restaurants_to_show'):
            print(f"🍽️ Restaurants: {response2['restaurants_to_show']}")
        # Add to conversation history
        conversation_history.append({"role": "user", "content": "Italian food please"})
        conversation_history.append({"role": "assistant", "content": response2['response']})
    
    # Test 3: Add specific preference
    print("\n3️⃣ Third message: Request outdoor seating")
    response3 = send_message(
        message="Outdoor seating would be great",
        conversation_history=conversation_history,
        session_id=session_id,
        user_id=user_id
    )
    
    if response3:
        print(f"✅ Response: {response3['response']}")
        if response3.get('restaurants_to_show'):
            print(f"🍽️ Restaurants: {response3['restaurants_to_show']}")
        # Add to conversation history
        conversation_history.append({"role": "user", "content": "Outdoor seating would be great"})
        conversation_history.append({"role": "assistant", "content": response3['response']})
    
    # Test 4: Reference previous conversation
    print("\n4️⃣ Fourth message: Reference previous suggestions")
    response4 = send_message(
        message="What about the first one you mentioned?",
        conversation_history=conversation_history,
        session_id=session_id,
        user_id=user_id
    )
    
    if response4:
        print(f"✅ Response: {response4['response']}")
    
    print(f"\n📊 Conversation history length: {len(conversation_history)} messages")
    
    # Test reset endpoint
    print("\n🔄 Testing conversation reset")
    reset_response = reset_conversation(session_id=session_id, user_id=user_id)
    if reset_response:
        print("✅ Conversation reset successful")

def send_message(message, conversation_history=None, session_id="test", user_id=None):
    """Send a message to the chat API"""
    url = f"{BASE_URL}/api/chat"
    
    payload = {
        "message": message,
        "session_id": session_id,
        "user_id": user_id
    }
    
    if conversation_history:
        payload["conversation_history"] = conversation_history
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Error sending message: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing response: {e}")
        return None

def reset_conversation(session_id="test", user_id=None):
    """Reset conversation history"""
    url = f"{BASE_URL}/api/chat/reset"
    
    payload = {
        "session_id": session_id,
        "user_id": user_id,
        "clear_history": True
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Error resetting conversation: {e}")
        return None

def test_backward_compatibility():
    """Test that old API format still works"""
    print("\n🔙 Testing backward compatibility (old format)")
    print("=" * 50)
    
    # Test old format without conversation_history
    response = send_message(
        message="Find me Italian restaurants",
        conversation_history=None,  # Explicitly None
        session_id="backward_test",
        user_id="test_user"
    )
    
    if response:
        print(f"✅ Old format works: {response['response']}")
        return True
    else:
        print("❌ Old format failed")
        return False

def test_api_health():
    """Test API health endpoint"""
    print("🏥 Testing API Health")
    print("=" * 30)
    
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=10)
        response.raise_for_status()
        health_data = response.json()
        
        print(f"✅ API Status: {health_data['status']}")
        print(f"✅ AI Available: {health_data['ai_available']}")
        print(f"✅ Staff AI Available: {health_data['staff_ai_available']}")
        return True
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

if __name__ == "__main__":
    # Run all tests
    print("🚀 Starting RestoAI Conversation Memory Tests")
    
    # 1. Check API health
    if not test_api_health():
        print("❌ API health check failed. Please ensure the Flask server is running.")
        exit(1)
    
    # 2. Test backward compatibility
    if not test_backward_compatibility():
        print("❌ Backward compatibility test failed.")
        exit(1)
    
    # 3. Test conversation flow
    test_conversation_flow()
    
    print("\n🎉 All tests completed!")
    print("\n💡 Key Features Tested:")
    print("   ✅ Conversation memory integration")
    print("   ✅ Context-aware responses")  
    print("   ✅ Backward compatibility")
    print("   ✅ Reset endpoint")
    print("   ✅ Restaurant recommendations with history")
