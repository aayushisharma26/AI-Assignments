"""
In-memory session store.

Keeps conversation history per session_id in a plain dict, guarded by a
lock since FastAPI can handle requests concurrently. No database and no
persistence across server restarts, by design for this assignment.
"""

import threading
from typing import Dict, List

from config import settings

Message = Dict[str, str]  # {"role": "user" | "assistant", "content": "..."}


class SessionManager:
    def __init__(self, max_history_messages: int) -> None:
        self._sessions: Dict[str, List[Message]] = {}
        self._lock = threading.Lock()
        self._max_history_messages = max_history_messages

    def get_history(self, session_id: str) -> List[Message]:
        with self._lock:
            return list(self._sessions.get(session_id, []))

    def add_exchange(self, session_id: str, user_message: str, assistant_reply: str) -> None:
        with self._lock:
            history = self._sessions.setdefault(session_id, [])
            history.append({"role": "user", "content": user_message})
            history.append({"role": "assistant", "content": assistant_reply})
            overflow = len(history) - self._max_history_messages
            if overflow > 0:
                del history[:overflow]

    def clear_session(self, session_id: str) -> None:
        with self._lock:
            self._sessions.pop(session_id, None)


session_manager = SessionManager(max_history_messages=settings.max_history_messages)
