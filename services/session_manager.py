import asyncio
import time
from typing import Dict, Any, List, Optional

class SessionManager:
    def __init__(self, timeout_seconds: int = 1800):
        self.timeout_seconds = timeout_seconds
        self._sessions: Dict[int, Dict[str, Any]] = {}
        self._lock = asyncio.Lock()

    async def get_or_create(self, user_id: int) -> Dict[str, Any]:
        async with self._lock:
            if user_id not in self._sessions:
                self._sessions[user_id] = self._create_empty_session()
            self._sessions[user_id]["last_active"] = time.time()
            return self._sessions[user_id]

    async def get(self, user_id: int) -> Optional[Dict[str, Any]]:
        async with self._lock:
            session = self._sessions.get(user_id)
            if session:
                session["last_active"] = time.time()
            return session

    async def add_photo(self, user_id: int, photo_bytes: bytes) -> int:
        async with self._lock:
            if user_id not in self._sessions:
                self._sessions[user_id] = self._create_empty_session()
            session = self._sessions[user_id]
            session["photos"].append(photo_bytes)
            session["last_active"] = time.time()
            return len(session["photos"])

    async def update_settings(self, user_id: int, key: str, value: Any) -> None:
        async with self._lock:
            if user_id in self._sessions:
                self._sessions[user_id][key] = value
                self._sessions[user_id]["last_active"] = time.time()

    async def clear(self, user_id: int) -> None:
        async with self._lock:
            if user_id in self._sessions:
                del self._sessions[user_id]

    async def cleanup_inactive(self) -> int:
        now = time.time()
        removed = 0
        async with self._lock:
            to_remove = [
                uid for uid, s in self._sessions.items()
                if now - s.get("last_active", 0) > self.timeout_seconds
            ]
            for uid in to_remove:
                del self._sessions[uid]
                removed += 1
        return removed

    def _create_empty_session(self) -> Dict[str, Any]:
        return {
            "photos": [],
            "template": "Classic Grid",
            "format": "Square (1:1)",
            "border": "Thin",
            "border_color": "White",
            "corner": "Slightly Rounded",
            "spacing": "Medium",
            "background": "White",
            "caption": "",
            "caption_position": "Bottom",
            "last_active": time.time()
        }

session_manager = SessionManager()
