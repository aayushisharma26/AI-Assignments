"""
Business logic for talking to Groq's chat-completion API.

Builds the message list (system prompt + prior history + new user
message), calls Groq, and records the exchange in the session store.
Raises ChatServiceError for anything app.py should turn into an HTTP
error response, so this module has no FastAPI/HTTP concerns of its own.
"""

from groq import (
    APIConnectionError,
    APIStatusError,
    AuthenticationError,
    Groq,
    RateLimitError,
)

from config import settings
from session_manager import session_manager


class ChatServiceError(Exception):
    def __init__(self, message: str, status_code: int) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


_client = Groq(api_key=settings.groq_api_key)


def get_chat_reply(session_id: str, user_message: str) -> str:
    history = session_manager.get_history(session_id)

    messages = [{"role": "system", "content": settings.system_prompt}]
    messages.extend(history)
    messages.append({"role": "user", "content": user_message})

    try:
        completion = _client.chat.completions.create(
            model=settings.groq_model,
            messages=messages,
            temperature=settings.groq_temperature,
            max_tokens=settings.groq_max_tokens,
        )
    except AuthenticationError as exc:
        raise ChatServiceError("Groq authentication failed. Check GROQ_API_KEY.", 500) from exc
    except RateLimitError as exc:
        raise ChatServiceError("Groq rate limit exceeded. Try again shortly.", 429) from exc
    except APIConnectionError as exc:
        raise ChatServiceError("Could not reach Groq API.", 503) from exc
    except APIStatusError as exc:
        raise ChatServiceError(f"Groq API returned an error: {exc.message}", 502) from exc

    reply = completion.choices[0].message.content
    if not reply:
        raise ChatServiceError("Groq returned an empty response.", 502)

    session_manager.add_exchange(session_id, user_message, reply)
    return reply

