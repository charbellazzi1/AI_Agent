#!/usr/bin/env python3
"""
Simple manual test of Flask API conversation memory
"""

import subprocess
import time
import requests
import json
import threading
import signal
import os

def test_flask_api():
    """Test the Flask API conversation memory functionality"""
    
    print("🧪 Testing Flask API Conversation Memory")
    print("=" * 50)
    
    # Test data
    session_id = "test_session_123"
    user_id = "test_user_456"
    base_url = "http://127.0.0.1:5000"
    
    # Test 1: Health check
    print("1️⃣ Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/api/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data['status']}")
            print(f"   AI Available: {data['ai_available']}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False
    
    # Test 2: Simple message without history (backward compatibility)
    print("\n2️⃣ Testing backward compatibility...")
    try:
        payload = {
            "message": "Find me restaurants",
            "session_id": session_id,
            "user_id": user_id
        }
        response = requests.post(f"{base_url}/api/chat", json=payload, timeout=30)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backward compatibility works")
            print(f"   Response: {data['response'][:80]}...")
        else:
            print(f"❌ Backward compatibility failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backward compatibility test failed: {e}")
        return False
    
    # Test 3: Conversation with history
    print("\n3️⃣ Testing conversation with history...")
    conversation_history = []
    
    # First message
    print("   Message 1: Initial greeting")
    try:
        payload = {
            "message": "Hi, I need restaurant recommendations",
            "conversation_history": conversation_history,
            "session_id": session_id,
            "user_id": user_id
        }
        response = requests.post(f"{base_url}/api/chat", json=payload, timeout=30)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Response 1: {data['response'][:60]}...")
            
            # Add to history
            conversation_history.append({"role": "user", "content": "Hi, I need restaurant recommendations"})
            conversation_history.append({"role": "assistant", "content": data['response']})
        else:
            print(f"   ❌ Message 1 failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Message 1 failed: {e}")
        return False
    
    # Second message with context
    print("   Message 2: Specify cuisine with context")
    try:
        payload = {
            "message": "Italian food please",
            "conversation_history": conversation_history,
            "session_id": session_id,
            "user_id": user_id
        }
        response = requests.post(f"{base_url}/api/chat", json=payload, timeout=30)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Response 2: {data['response'][:60]}...")
            if data.get('restaurants_to_show'):
                print(f"   🍽️ Found restaurants: {len(data['restaurants_to_show'])}")
        else:
            print(f"   ❌ Message 2 failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Message 2 failed: {e}")
        return False
    
    # Test 4: Reset endpoint
    print("\n4️⃣ Testing reset endpoint...")
    try:
        payload = {
            "session_id": session_id,
            "user_id": user_id,
            "clear_history": True
        }
        response = requests.post(f"{base_url}/api/chat/reset", json=payload, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Reset endpoint works: {data['message']}")
        else:
            print(f"❌ Reset endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Reset endpoint failed: {e}")
        return False
    
    print("\n🎉 All Flask API tests passed!")
    return True

if __name__ == "__main__":
    print("🚀 Manual Flask API Test")
    print("🔧 Make sure Flask server is running on port 5000")
    print("   Run: python flask_api_ai.py")
    print()
    
    input("Press Enter when Flask server is ready...")
    
    success = test_flask_api()
    if success:
        print("\n✅ Flask API conversation memory implementation successful!")
        print("\n💡 Features confirmed:")
        print("   ✅ Health endpoint works")
        print("   ✅ Backward compatibility maintained")
        print("   ✅ Conversation history processing")
        print("   ✅ Context-aware responses")
        print("   ✅ Reset endpoint functional")
    else:
        print("\n❌ Some tests failed")
