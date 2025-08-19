from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Try to import AI functionality with graceful fallback
AI_AVAILABLE = False
STAFF_AI_AVAILABLE = False

try:
    from AI_Agent import chat_with_bot, getAllCuisineTypes
    AI_AVAILABLE = True
    logger.info("AI Agent imported successfully")
except Exception as e:
    logger.warning(f"AI Agent import failed: {e}")
    AI_AVAILABLE = False

try:
    from AI_Agent_Restaurant import chat_with_staff_bot
    STAFF_AI_AVAILABLE = True
    logger.info("Restaurant Staff AI Agent imported successfully")
except Exception as e:
    logger.warning(f"Restaurant Staff AI Agent import failed: {e}")
    STAFF_AI_AVAILABLE = False

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'status': 'healthy',
        'message': 'Restaurant AI Agent API is running',
        'ai_available': AI_AVAILABLE,
        'staff_ai_available': STAFF_AI_AVAILABLE,
        'environment_check': {
            'GOOGLE_API_KEY': 'Set' if os.getenv('GOOGLE_API_KEY') else 'Missing',
            'EXPO_PUBLIC_SUPABASE_URL': 'Set' if os.getenv('EXPO_PUBLIC_SUPABASE_URL') else 'Missing',
            'EXPO_PUBLIC_SUPABASE_ANON_KEY': 'Set' if os.getenv('EXPO_PUBLIC_SUPABASE_ANON_KEY') else 'Missing'
        }
    }), 200

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'message': 'Restaurant AI Agent API is running',
        'ai_available': AI_AVAILABLE,
        'staff_ai_available': STAFF_AI_AVAILABLE
    }), 200

@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Main chat endpoint to send messages to the AI agent.
    Note: Chat history is managed by the frontend.
    """
    try:
        if not AI_AVAILABLE:
            return jsonify({
                'error': 'AI functionality not available',
                'message': 'Please check environment variables and dependencies',
                'status': 'error'
            }), 503

        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({
                'error': 'Message is required',
                'status': 'error'
            }), 400
        
        user_message = data['message'].strip()
        session_id = data.get('session_id', 'default')
        user_id = data.get('user_id')  # Optional user ID for personalization
        
        if not user_message:
            return jsonify({
                'error': 'Message cannot be empty',
                'status': 'error'
            }), 400
        
        logger.info(f"Received message from session {session_id} (user: {user_id}): {user_message}")
        
        # Get AI response - each request is stateless since frontend manages history
        # Pass user_id for personalized responses
        ai_response = chat_with_bot(user_message, memory=None, user_id=user_id)
        
        logger.info(f"AI response for session {session_id}: {ai_response}")
        
        # Check if response contains restaurant recommendations
        restaurants_to_show = []
        response_text = ai_response
        
        if "RESTAURANTS_TO_SHOW:" in ai_response:
            parts = ai_response.split("RESTAURANTS_TO_SHOW:")
            response_text = parts[0].strip()
            if len(parts) > 1:
                restaurant_ids = [id.strip() for id in parts[1].strip().split(',') if id.strip()]
                restaurants_to_show = restaurant_ids
        
        return jsonify({
            'response': response_text,
            'restaurants_to_show': restaurants_to_show,
            'session_id': session_id,
            'user_id': user_id,
            'status': 'success'
        }), 200
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e),
            'status': 'error'
        }), 500

@app.route('/api/restaurants/cuisines', methods=['GET'])
def get_cuisine_types():
    """Get all available cuisine types."""
    try:
        if not AI_AVAILABLE:
            return jsonify({
                'error': 'AI functionality not available',
                'status': 'error'
            }), 503

        # Call the tool safely to get cuisine types (@tool wraps it as a Tool object)
        try:
            # Preferred path for no-arg tools
            cuisine_types_str = getAllCuisineTypes.invoke({})
        except Exception:
            try:
                # Some versions accept a positional empty string
                cuisine_types_str = getAllCuisineTypes("")
            except Exception:
                try:
                    # Older API
                    cuisine_types_str = getAllCuisineTypes.run("")
                except Exception:
                    try:
                        # Access original function if exposed
                        func = getattr(getAllCuisineTypes, "func", None)
                        cuisine_types_str = func() if callable(func) else "[]"
                    except Exception:
                        cuisine_types_str = "[]"
        
        # Parse the JSON response
        import json
        try:
            cuisine_types = json.loads(cuisine_types_str)
        except:
            cuisine_types = []
        
        return jsonify({
            'cuisine_types': cuisine_types,
            'status': 'success'
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting cuisine types: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e),
            'status': 'error'
        }), 500

@app.route('/api/staff/chat', methods=['POST'])
def staff_chat():
    """
    Chat endpoint specifically for restaurant staff assistance.
    Requires restaurant_id in the request.
    """
    try:
        if not STAFF_AI_AVAILABLE:
            return jsonify({
                'error': 'Staff AI functionality not available',
                'message': 'Please check environment variables and dependencies',
                'status': 'error'
            }), 503

        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({
                'error': 'Message is required',
                'status': 'error'
            }), 400
        
        user_message = data['message'].strip()
        restaurant_id = data.get('restaurant_id')
        session_id = data.get('session_id', 'staff_default')
        
        if not user_message:
            return jsonify({
                'error': 'Message cannot be empty',
                'status': 'error'
            }), 400
        
        logger.info(f"Received staff message from session {session_id}: {user_message}")
        
        # Get Staff AI response
        staff_response = chat_with_staff_bot(user_message, restaurant_id)
        
        logger.info(f"Staff AI response for session {session_id}: {staff_response}")
        
        return jsonify({
            'response': staff_response,
            'session_id': session_id,
            'restaurant_id': restaurant_id,
            'status': 'success'
        }), 200
        
    except Exception as e:
        logger.error(f"Error in staff chat endpoint: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e),
            'status': 'error'
        }), 500

@app.route('/api/test', methods=['POST'])
def test_endpoint():
    """Test endpoint for debugging purposes."""
    try:
        data = request.get_json()
        
        return jsonify({
            'message': 'Test endpoint working',
            'received_data': data,
            'ai_available': AI_AVAILABLE,
            'staff_ai_available': STAFF_AI_AVAILABLE,
            'status': 'success'
        }), 200
        
    except Exception as e:
        logger.error(f"Error in test endpoint: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e),
            'status': 'error'
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Endpoint not found',
        'status': 'error'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'error': 'Internal server error',
        'status': 'error'
    }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 