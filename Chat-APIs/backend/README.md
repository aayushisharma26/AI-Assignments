# Chat API (backend)

FastAPI backend that wraps Groq's chat-completion API behind a small REST
interface, with per-session conversation history kept in memory.

## Architecture

```
backend/
├── api/index.py       FastAPI app + routes (entrypoint for Vercel)
├── app.py             Re-exports api/index.py's app for local `uvicorn app:app`
├── chat_service.py    Builds the message list, calls Groq, maps errors
├── session_manager.py In-memory per-session history store (thread-safe)
├── models.py           Pydantic request/response schemas
├── config.py           Loads and validates environment variables
└── vercel.json          Rewrites all paths to api/index.py when deployed
```

Request flow: `api/index.py` → `chat_service.get_chat_reply()` → Groq API,
recording the exchange via `session_manager` on success.

## Setup

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then fill in GROQ_API_KEY
uvicorn app:app --reload --port 8000
```

## Environment variables

| Variable                | Required | Default                                | Description                                  |
|--------------------------|----------|-----------------------------------------|-----------------------------------------------|
| `GROQ_API_KEY`           | yes      | —                                        | API key from console.groq.com/keys           |
| `GROQ_MODEL`             | no       | `llama-3.3-70b-versatile`                | Groq model id                                 |
| `GROQ_TEMPERATURE`       | no       | `0.7`                                    | Sampling temperature                          |
| `GROQ_MAX_TOKENS`        | no       | `1024`                                   | Max tokens in the model's reply               |
| `MAX_HISTORY_MESSAGES`   | no       | `20`                                     | Messages kept per session before trimming     |
| `SYSTEM_PROMPT`          | no       | `You are a helpful, concise AI assistant.` | System prompt prepended to every request    |
| `ALLOWED_ORIGINS`        | no       | `*`                                       | Comma-separated frontend origins allowed by CORS |

## API reference

### `GET /health`
```json
{ "status": "healthy", "message": "Server is running" }
```

### `POST /chat`
Request:
```json
{ "session_id": "sess_abc123", "message": "Hello!" }
```
Success (200):
```json
{ "session_id": "sess_abc123", "reply": "Hi there! How can I help?", "model": "llama-3.3-70b-versatile" }
```
Error (429/502/503):
```json
{ "error": "chat_service_error", "detail": "Groq rate limit exceeded. Try again shortly." }
```

### `DELETE /chat/{session_id}`
Clears server-side history for a session. Always returns 204, whether or
not the session existed.

## Notes / known limitations

- Session history is in-memory only — it does not survive a server
  restart, and is not shared across multiple server instances.
- Sessions are never evicted except via `DELETE /chat/{session_id}`; a
  long-running deployment with many distinct session ids will accumulate
  memory. Fine for this assignment's scope, worth a TTL/eviction pass
  before any real deployment.
- CORS allows all origins by default (`ALLOWED_ORIGINS` unset). Set it to
  the deployed frontend's exact origin before shipping beyond localhost.
- No auth or rate limiting on `/chat` — anyone who can reach the API can
  spend your Groq quota.
