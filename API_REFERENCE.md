## RestoAI API Reference

This document provides precise instructions for using the RestoAI HTTP API.

- **Base URL (Production)**: `https://restoai-sigma.vercel.app`
- **Content Type**: `application/json`
- **Authentication**: None (ensure your deployment is protected as needed)

### Environments and Variables
- The API requires these environment variables on the server:
  - `GOOGLE_API_KEY`
  - `EXPO_PUBLIC_SUPABASE_URL`
  - `EXPO_PUBLIC_SUPABASE_ANON_KEY`

---

## Health & Diagnostics

### GET /
- **Description**: Root health and environment presence check.
- **Response (200)**:
```json
{
  "status": "healthy",
  "message": "Restaurant AI Agent API is running",
  "ai_available": true,
  "staff_ai_available": true,
  "environment_check": {
    "GOOGLE_API_KEY": "Set | Missing",
    "EXPO_PUBLIC_SUPABASE_URL": "Set | Missing",
    "EXPO_PUBLIC_SUPABASE_ANON_KEY": "Set | Missing"
  }
}
```

### GET /api/health
- **Description**: Lightweight health check.
- **Response (200)**:
```json
{ "status": "healthy", "message": "Restaurant AI Agent API is running", "ai_available": true, "staff_ai_available": true }
```

---

## Customer AI

### POST /api/chat
- **Description**: Customer-facing chat for restaurant discovery and info.
- **Request Body**:
```json
{ "message": "Suggest some Italian places", "session_id": "optional-session-id" }
```
- **Response (200)**:
```json
{
  "response": "Here are some options I found for that cuisine.",
  "restaurants_to_show": ["<restaurant-id>"] ,
  "session_id": "default",
  "status": "success"
}
```
- **Notes**:
  - When recommendations are made, the response may include `RESTAURANTS_TO_SHOW` semantics reflected as `restaurants_to_show` array in JSON.

---

## Restaurant Data

### GET /api/restaurants/cuisines
- **Description**: Returns the list of unique cuisine types.
- **Response (200)**:
```json
{ "cuisine_types": ["Italian", "Lebanese", "American"], "status": "success" }
```

---

## Staff AI

### POST /api/staff/chat
- **Description**: Staff-facing chat for operations (covers, availability, customer context, etc.).
- **Request Body**:
```json
{
  "message": "How many covers today?",
  "restaurant_id": "<uuid>",
  "session_id": "optional-session-id"
}
```
- **Response (200)**:
```json
{ "response": "Today's stats: ...", "restaurant_id": "<uuid>", "session_id": "staff_default", "status": "success" }
```
- **Notes**:
  - `restaurant_id` should be a valid UUID from your Supabase `restaurants` table.
  - If `restaurant_id` is missing or invalid, the API replies asking for a valid one.

---

## Test Utility

### POST /api/test
- **Description**: Echo-style endpoint for quick verification.
- **Request Body**: Any JSON (e.g., `{ "ping": "pong" }`).
- **Response (200)**:
```json
{ "message": "Test endpoint working", "received_data": { "ping": "pong" }, "status": "success" }
```

---

## Error Handling
- **400 Bad Request**: Missing/invalid parameters (e.g., empty `message`).
- **404 Not Found**: Unknown endpoint.
- **500 Internal Server Error**: Unhandled server errors.
- **503 Service Unavailable**: AI functionality not available (e.g., missing env vars or imports).

Example error:
```json
{ "error": "Message is required", "status": "error" }
```

---

## cURL Examples

Replace `<BASE>` with your deployment, e.g., `https://restoai-sigma.vercel.app`.

### Health
```bash
curl -s <BASE>/
curl -s <BASE>/api/health
```

### Cuisines
```bash
curl -s <BASE>/api/restaurants/cuisines
```

### Customer Chat
```bash
curl -s <BASE>/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Suggest some Italian places"}'
```

### Staff Chat
```bash
curl -s <BASE>/api/staff/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"How many covers today?","restaurant_id":"<uuid>"}'
```

### Test Endpoint
```bash
curl -s <BASE>/api/test \
  -H "Content-Type: application/json" \
  -d '{"ping":"pong"}'
```

---

## Integration Notes
- **CORS**: Enabled via `flask-cors`; suitable for browser clients.
- **Idempotency**: Chat endpoints are stateless per request; client manages history.
- **Timeouts/Cold Starts**: On serverless (Vercel) first hit can be slower.
- **Rate Limiting**: Not enforced at API level; add at the edge if needed.

---

## Deployment (Vercel)
1. Connect your GitHub repo to Vercel.
2. Set environment variables in Project → Settings → Environment Variables:
   - `GOOGLE_API_KEY`, `EXPO_PUBLIC_SUPABASE_URL`, `EXPO_PUBLIC_SUPABASE_ANON_KEY`
3. Ensure `vercel.json` routes to `flask_api_ai.py`.
4. Deploy. Test using the cURL examples above.

---

## Change Log
- 2025-08-08
  - Added cuisines tool invocation fix.
  - Enhanced customer chat fallback to include `restaurants_to_show` when tool results are present.


