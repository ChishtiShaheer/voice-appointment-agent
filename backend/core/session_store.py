import time
import uuid

_sessions: dict[str, dict] = {}
SESSION_TTL_SECONDS = 60 * 60


def create_session() -> str:
    session_id = str(uuid.uuid4())
    _sessions[session_id] = {
        "state": "GREETING",
        "collected": {},
        "history": [],
        "pending_intent": None,
        "lookup_appointment_id": None,
        "created_at": time.time(),
    }
    return session_id


def get_session(session_id: str) -> dict | None:
    _cleanup()
    return _sessions.get(session_id)


def save_session(session_id: str, session: dict) -> None:
    session["updated_at"] = time.time()
    _sessions[session_id] = session


def delete_session(session_id: str) -> None:
    _sessions.pop(session_id, None)


def _cleanup() -> None:
    now = time.time()
    expired = [
        sid for sid, s in _sessions.items()
        if now - s.get("created_at", now) > SESSION_TTL_SECONDS
    ]
    for sid in expired:
        _sessions.pop(sid, None)
