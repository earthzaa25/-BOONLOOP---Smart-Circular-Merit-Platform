import time
import logging

logger = logging.getLogger(__name__)

# เก็บ session การจองใน memory (เร็วกว่าเขียน Google Sheet ทุกขั้น)
_sessions = {}
_TTL = 1800  # 30 นาที — ถ้าจองค้างเกินนี้ session หมดอายุ


def get_session(line_user_id: str) -> dict | None:
    entry = _sessions.get(line_user_id)
    if not entry:
        return None
    if time.time() - entry["t"] > _TTL:
        _sessions.pop(line_user_id, None)
        return None
    return {"step": entry["step"], "session_data": entry["data"]}


def set_session(line_user_id: str, step: str, session_data: dict):
    _sessions[line_user_id] = {"step": step, "data": session_data, "t": time.time()}


def clear_session(line_user_id: str):
    _sessions.pop(line_user_id, None)
