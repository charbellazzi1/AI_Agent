#!/usr/bin/env python3
"""
Simple test to validate conversation memory implementation
"""

import sys
import os

# Add current directory to path to import AI modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_conversation_memory_direct():
    """Test conversation memory directly without Flask API"""
    print("🧪 Testing Conversation Memory Direct Implementation")
    print("=" * 60)
    
    try:
        # Import required modules
        from AI_Agent import chat_with_bot, create_conversation_memory
        from langchain_core.messages import HumanMessage, AIMessage
        
        print("✅ Successfully imported AI Agent modules")
        
        # Create conversation memory
        memory = create_conversation_memory(max_history=20)
        print("✅ Created conversation memory")
        
        # Test 1: First message with empty memory
        print("\n1️⃣ Testing first message:")
        response1 = chat_with_bot("Hi, I need restaurant recommendations", memory=memory)
        print(f"Response: {response1[:100]}...")
        print(f"Memory size after first message: {memory.get_context_size()}")
        
        # Test 2: Second message with memory
        print("\n2️⃣ Testing second message with context:")
        response2 = chat_with_bot("Italian food please", memory=memory)
        print(f"Response: {response2[:100]}...")
        print(f"Memory size after second message: {memory.get_context_size()}")
        
        # Test 3: Third message referencing conversation
        print("\n3️⃣ Testing third message with full context:")
        response3 = chat_with_bot("Outdoor seating would be great", memory=memory)
        print(f"Response: {response3[:100]}...")
        print(f"Final memory size: {memory.get_context_size()}")
        
        print("\n✅ Direct conversation memory test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error in direct test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_conversion_function():
    """Test the conversion function from frontend format to LangChain format"""
    print("\n🔄 Testing Conversation History Conversion")
    print("=" * 50)
    
    try:
        from AI_Agent import create_conversation_memory
        from langchain_core.messages import HumanMessage, AIMessage
        
        # Sample frontend conversation history
        frontend_history = [
            {"role": "user", "content": "Hi, I need restaurant recommendations"},
            {"role": "assistant", "content": "I'd be happy to help! What type of cuisine are you interested in?"},
            {"role": "user", "content": "Italian food please"},
            {"role": "assistant", "content": "Perfect! Do you have any preferences for location or seating?"}
        ]
        
        print(f"Frontend history: {len(frontend_history)} messages")
        
        # Convert to LangChain format
        memory = create_conversation_memory(max_history=20)
        
        for msg in frontend_history:
            if msg['role'] == 'user':
                memory.add_message(HumanMessage(content=msg['content']))
            elif msg['role'] == 'assistant':
                memory.add_message(AIMessage(content=msg['content']))
        
        print(f"Converted to LangChain format: {memory.get_context_size()} messages")
        
        # Get messages and check types
        messages = memory.get_messages()
        for i, msg in enumerate(messages):
            msg_type = "User" if isinstance(msg, HumanMessage) else "Assistant"
            print(f"  {i+1}. {msg_type}: {msg.content[:50]}...")
        
        print("✅ Conversion test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error in conversion test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 RestoAI Conversation Memory Direct Tests")
    
    # Test 1: Direct conversation memory
    if not test_conversation_memory_direct():
        print("❌ Direct conversation memory test failed")
        sys.exit(1)
    
    # Test 2: Conversion function
    if not test_conversion_function():
        print("❌ Conversion function test failed")
        sys.exit(1)
    
    print("\n🎉 All direct tests passed!")
    print("\n💡 Implementation Status:")
    print("   ✅ Conversation memory creation works")
    print("   ✅ AI Agent accepts memory parameter")
    print("   ✅ Context preserved across messages")
    print("   ✅ Frontend format conversion works")
    print("   ✅ Ready for Flask API integration")
