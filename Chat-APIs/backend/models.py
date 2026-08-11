"""
Pydantic request/response schemas shared between app.py and chat_service.py.
"""

from typing import Optional

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    session_id: str = Field(..., min_length=1, description="Client-generated session identifier")
    message: str = Field(..., min_length=1, max_length=4000, description="User's chat message")


class ChatResponse(BaseModel):
    session_id: str
    reply: str
    model: str


class HealthResponse(BaseModel):
    status: str
    message: str


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
