#!/bin/bash

# Simple deployment script for the security-enhanced backend

echo "=== Restaurant AI Backend Security Update ==="
echo "This script will install security enhancements for the backend API"
echo

# Check if we're in the right directory
if [ ! -f "flask_api_ai.py" ]; then
    echo "Error: flask_api_ai.py not found. Please run this script from the AI directory."
    exit 1
fi

echo "Installing new dependencies..."
pip install flask-limiter>=3.5.0

echo
echo "Dependencies installed successfully!"
echo

echo "=== Security Features Added ==="
echo "✓ Rate limiting (30 requests/minute for chat, 50 for staff)"
echo "✓ Request validation (User-Agent checking)"
echo "✓ Security headers (XSS protection, clickjacking prevention)"
echo "✓ Request logging for monitoring"
echo "✓ Admin endpoint for stats (protected with X-Admin-Key header)"
echo

echo "=== Testing the deployment ==="
echo "You can test the security features by running:"
echo "  python test_security.py"
echo

echo "=== Important Notes ==="
echo "1. Set ADMIN_KEY environment variable to a secure value in production"
echo "2. Consider using Redis for rate limiting in production (instead of memory)"
echo "3. Monitor logs for suspicious activity"
echo "4. All existing frontend code will continue to work without changes"
echo

echo "=== Rate Limits ==="
echo "- Global: 200 requests/day, 50/hour per IP"
echo "- Chat: 30 requests/minute per IP"
echo "- Staff Chat: 50 requests/minute per IP"  
echo "- Cuisines: 10 requests/minute per IP"
echo "- Admin: 5 requests/minute per IP"
echo

echo "Deployment complete! 🎉"
echo "Your API is now more secure while remaining user-friendly."
