"""
FastAPI application entrypoint.

Routes only — request/response shapes live in models.py, Groq calls live
in chat_service.py, and session state lives in session_manager.py.
"""

from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from chat_service import ChatServiceError, get_chat_reply
from config import settings
from models import ChatRequest, ChatResponse, ErrorResponse, HealthResponse
from session_manager import session_manager

app = FastAPI(title="Chat API")

# allow_origins defaults to "*" (dev-friendly) but should be set to the
# deployed frontend's exact origin via ALLOWED_ORIGINS in production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root() -> dict:
    return {"message": "Chat API is running"}


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(status="healthy", message="Server is running")


@app.post("/chat", response_model=ChatResponse, responses={502: {"model": ErrorResponse}, 503: {"model": ErrorResponse}})
async def chat(request: ChatRequest) -> ChatResponse:
    try:
        reply = get_chat_reply(request.session_id, request.message)
    except ChatServiceError as exc:
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(error="chat_service_error", detail=exc.message).model_dump(),
        )

    return ChatResponse(session_id=request.session_id, reply=reply, model=settings.groq_model)


@app.delete("/chat/{session_id}", status_code=204)
async def clear_chat(session_id: str) -> Response:
    session_manager.clear_session(session_id)
    return Response(status_code=204)
