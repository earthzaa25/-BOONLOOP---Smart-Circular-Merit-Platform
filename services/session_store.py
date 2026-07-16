import os
import json
import time
import sqlite3
import logging

logger = logging.getLogger(__name__)

# เก็บ session ลง SQLite บนดิสก์ — ทุก worker เห็นร่วมกัน
# (ถ้าเก็บใน memory จะแยกกันคนละ worker ทำให้จองแล้วหลุดกลางคัน)
DB_PATH = os.environ.get("SESSION_DB", "/tmp/boonloop_sessions.db")
_TTL = 1800  # 30 นาที


def _conn():
    c = sqlite3.connect(DB_PATH, timeout=5)
    c.execute("PRAGMA journal_mode=WAL")  # ให้หลาย worker อ่าน/เขียนพร้อมกันได้
    return c


def _init():
    try:
        with _conn() as c:
            c.execute("""CREATE TABLE IF NOT EXISTS sessions (
                user_id TEXT PRIMARY KEY,
                step TEXT,
                data TEXT,
                updated_at REAL
            )""")
    except Exception as e:
        logger.error(f"init session db error: {e}")


_init()


def get_session(line_user_id: str) -> dict | None:
    try:
        with _conn() as c:
            row = c.execute(
                "SELECT step, data, updated_at FROM sessions WHERE user_id=?",
                (line_user_id,),
            ).fetchone()
        if not row:
            return None
        step, data, updated = row
        if time.time() - updated > _TTL:
            clear_session(line_user_id)
            return None
        return {"step": step, "session_data": json.loads(data or "{}")}
    except Exception as e:
        logger.error(f"get_session error: {e}")
        return None


def set_session(line_user_id: str, step: str, session_data: dict):
    try:
        with _conn() as c:
            c.execute(
                "INSERT OR REPLACE INTO sessions (user_id, step, data, updated_at) VALUES (?,?,?,?)",
                (line_user_id, step, json.dumps(session_data or {}, ensure_ascii=False), time.time()),
            )
    except Exception as e:
        logger.error(f"set_session error: {e}")


def clear_session(line_user_id: str):
    try:
        with _conn() as c:
            c.execute("DELETE FROM sessions WHERE user_id=?", (line_user_id,))
    except Exception as e:
        logger.error(f"clear_session error: {e}")
