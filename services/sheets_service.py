import os
import logging
import requests

logger = logging.getLogger(__name__)

WEBAPP_URL = os.environ.get(
    "SHEETS_WEBAPP_URL",
    "https://script.google.com/macros/s/AKfycbxlEf9TdN0qPD_L8z-O-IMaT8BPPNJhbuZRGx0ktUFtZkdBZicFIYLGWJfEeLSWBdlc/exec"
)


def _call(payload: dict) -> dict:
    if not WEBAPP_URL:
        raise ValueError("SHEETS_WEBAPP_URL not set")
    try:
        res = requests.post(WEBAPP_URL, json=payload, timeout=15)
        res.raise_for_status()
        return res.json()
    except Exception as e:
        logger.error(f"Sheets API error: {e}")
        raise


def get_member(line_user_id: str) -> dict | None:
    result = _call({"action": "getMember", "line_user_id": line_user_id})
    return result.get("data")


def register_member(line_user_id: str, display_name: str) -> dict:
    result = _call({
        "action": "registerMember",
        "line_user_id": line_user_id,
        "display_name": display_name
    })
    if not result.get("success"):
        raise Exception(result.get("error", "register failed"))
    return result.get("data")


def create_booking(line_user_id: str, package_type: str, package_name: str,
                   price: int, pickup_date: str = "", location: str = "",
                   eco_score: int = 10) -> str:
    result = _call({
        "action": "createBooking",
        "line_user_id": line_user_id,
        "package_type": package_type,
        "package_name": package_name,
        "price": price,
        "pickup_date": pickup_date,
        "location": location,
        "eco_score": eco_score
    })
    if not result.get("success"):
        raise Exception(result.get("error", "booking failed"))
    return result.get("booking_id")


def add_points(line_user_id: str, points: int, eco_score: int, reason: str):
    _call({
        "action": "addPoints",
        "line_user_id": line_user_id,
        "points": points,
        "eco_score": eco_score,
        "reason": reason
    })


def get_points_summary(line_user_id: str) -> dict:
    result = _call({"action": "getPointsSummary", "line_user_id": line_user_id})
    return result.get("data", {"boon_points": 0, "eco_score": 0, "total_bookings": 0})


# ─── Sessions (การจอง 7 ขั้นตอน) ──────────────

def get_session(line_user_id: str) -> dict | None:
    result = _call({"action": "getSession", "line_user_id": line_user_id})
    return result.get("data")


def set_session(line_user_id: str, step: str, session_data: dict):
    _call({
        "action": "setSession",
        "line_user_id": line_user_id,
        "step": step,
        "session_data": session_data
    })


def clear_session(line_user_id: str):
    _call({"action": "clearSession", "line_user_id": line_user_id})
