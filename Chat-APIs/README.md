# Chat APIs & Web Chat Interface

**OS3 Infotech — Assignment L1-02.** A FastAPI backend that exposes chatbot functionality (via Groq's LLM API) behind REST endpoints, and a vanilla HTML/CSS/JS web chat interface that talks to it.

```
Chat-APIs/
├── backend/     FastAPI app — see backend/README.md for full docs
└── frontend/    Static chat UI (HTML/CSS/JS, no framework)
```

## Quick Start

**Backend**
```bash
cd backend
source venv/bin/activate
uvicorn app:app --reload --port 8000
```

**Frontend** (separate terminal)
```bash
cd frontend
python3 -m http.server 5500
```

Then open **http://localhost:5500** in a browser. The frontend is preconfigured to call the backend at `http://localhost:8000` (see `frontend/config.js`).

For architecture details, environment variables, API reference, and example requests/responses, see **[backend/README.md](backend/README.md)**.
