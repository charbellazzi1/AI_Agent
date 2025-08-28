# Security Features

This document outlines the security features implemented in the Restaurant AI API backend.

## Overview

The security implementation focuses on lightweight protection that doesn't require user management or API key distribution, making it easy for frontend applications to integrate without additional complexity.

## Implemented Security Features

### 1. Rate Limiting
- **Global Limits**: 200 requests per day, 50 per hour per IP address
- **Chat Endpoint**: 30 requests per minute per IP
- **Staff Chat Endpoint**: 50 requests per minute per IP (higher limit for restaurant staff)
- **Cuisine Endpoint**: 10 requests per minute per IP
- **Admin Endpoint**: 5 requests per minute per IP

### 2. Request Validation
- Validates User-Agent headers to ensure requests come from legitimate sources
- Accepts requests from:
  - Mobile apps (Expo, React Native, Android, iOS)
  - Web browsers (Chrome, Firefox, Safari, Edge)
  - Development environments (no User-Agent)
- Blocks suspicious or automated requests

### 3. Security Headers
- `X-Content-Type-Options: nosniff` - Prevents MIME type sniffing
- `X-Frame-Options: DENY` - Prevents clickjacking attacks
- `X-XSS-Protection: 1; mode=block` - Enables XSS filtering
- `Referrer-Policy: strict-origin-when-cross-origin` - Controls referrer information

### 4. Request Logging
- Logs all incoming requests with:
  - HTTP method and path
  - Client IP address
  - User-Agent string
  - Timestamp
- Helps with monitoring and debugging

### 5. Error Handling
- Custom error responses for rate limit exceeded (429)
- Graceful handling of validation failures (403)
- Structured error messages in JSON format

### 6. Admin Monitoring (Optional)
- Simple admin endpoint: `/api/admin/stats`
- Requires `X-Admin-Key` header for access
- Returns basic system status and rate limit information
- Protected with its own rate limit

## Frontend Integration

### No Changes Required
The security features are implemented server-side and don't require any changes to existing frontend code. The frontends can continue making requests to:
- `https://restoai-sigma.vercel.app/api/chat`
- `https://restoai-sigma.vercel.app/api/staff/chat`
- `https://restoai-sigma.vercel.app/api/restaurants/cuisines`

### Automatic Handling
- Rate limits are automatically enforced
- Valid User-Agent headers are automatically sent by browsers and mobile apps
- Error responses are handled gracefully with appropriate HTTP status codes

## Configuration

### Environment Variables
- `ADMIN_KEY`: Set this to a secure value for admin endpoint access (default: "admin123")

### Rate Limit Customization
Rate limits can be adjusted in `flask_api_ai.py`:
```python
# Global limits
default_limits=["200 per day", "50 per hour"]

# Endpoint-specific limits
@limiter.limit("30 per minute")  # Chat endpoint
@limiter.limit("50 per minute")  # Staff chat endpoint
@limiter.limit("10 per minute")  # Cuisine endpoint
```

## Deployment Considerations

### Production Security
1. Change the default `ADMIN_KEY` to a strong, random value
2. Consider using Redis for rate limiting storage instead of memory for better persistence
3. Monitor logs for suspicious activity patterns
4. Consider adding IP whitelisting for admin endpoints

### Scaling
- The current implementation uses in-memory storage for rate limiting
- For production with multiple instances, consider using Redis:
  ```python
  storage_uri="redis://localhost:6379"
  ```

## Benefits

1. **User Friendly**: No API keys or user management required
2. **Minimal Frontend Changes**: Zero changes needed to existing frontend code
3. **Abuse Prevention**: Rate limiting prevents excessive usage
4. **Monitoring**: Request logging helps track usage patterns
5. **Security Headers**: Protection against common web vulnerabilities
6. **Graceful Degradation**: Proper error handling and responses

## Limitations

1. **IP-based**: Rate limiting is per IP, so users behind the same NAT/proxy share limits
2. **Memory Storage**: Rate limit data is lost on server restart (can be fixed with Redis)
3. **Basic Validation**: User-Agent validation can be bypassed but provides basic protection

## Testing

### Rate Limit Testing
```bash
# Test rate limits by making multiple requests quickly
for i in {1..35}; do
  curl -X POST https://restoai-sigma.vercel.app/api/chat \
    -H "Content-Type: application/json" \
    -d '{"message": "test"}' && echo " - Request $i"
done
```

### Admin Endpoint Testing
```bash
# Test admin endpoint
curl -H "X-Admin-Key: admin123" https://restoai-sigma.vercel.app/api/admin/stats
```

This security implementation provides a good balance between protection and usability, ensuring the API is secure without creating barriers for legitimate users.
