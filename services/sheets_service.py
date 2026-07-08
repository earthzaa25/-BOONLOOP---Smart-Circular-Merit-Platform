import os
import time
import logging
import requests

logger = logging.getLogger(__name__)

WEBAPP_URL = os.environ.get(
    "SHEETS_WEBAPP_URL",
    "https://script.google.com/macros/s/AKfycbxlEf9TdN0qPD_L8z-O-IMaT8BPPNJhbuZRGx0ktUFtZkdBZicFIYLGWJfEeLSWBdlc/exec"
)

# cache ข้อมูลสมาชิก (ลดการเรียก Sheet ซ้ำ)
_member_cache = {}
_MEMBER_TTL = 30  # วินาที


def _call(payload: dict) -> dict:
    if not WEBAPP_URL:
        raise ValueError("SHEETS_WEBAPP_URL not set")
    last_err = None
    # ลองสูงสุด 2 ครั้ง เผื่อ Apps Script อืดชั่วคราว
    for attempt in range(2):
        try:
            res = requests.post(WEBAPP_URL, json=payload, timeout=30)
            res.raise_for_status()
            return res.json()
        except requests.exceptions.Timeout as e:
            last_err = e
            logger.warning(f"Sheets timeout (ครั้งที่ {attempt + 1}), ลองใหม่...")
            continue
        except Exception as e:
            last_err = e
            logger.error(f"Sheets API error: {e}")
            raise
    logger.error(f"Sheets API error หลัง retry: {last_err}")
    raise last_err


def _invalidate_member(line_user_id: str):
    _member_cache.pop(line_user_id, None)


def get_member(line_user_id: str, use_cache: bool = True) -> dict | None:
    now = time.time()
    if use_cache:
        entry = _member_cache.get(line_user_id)
        if entry and now - entry[0] < _MEMBER_TTL:
            return entry[1]
    result = _call({"action": "getMember", "line_user_id": line_user_id})
    data = result.get("data")
    _member_cache[line_user_id] = (now, data)
    return data


def register_member(line_user_id: str, display_name: str) -> dict:
    result = _call({
        "action": "registerMember",
        "line_user_id": line_user_id,
        "display_name": display_name
    })
    if not result.get("success"):
        raise Exception(result.get("error", "register failed"))
    _invalidate_member(line_user_id)
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
    _invalidate_member(line_user_id)
    return result.get("booking_id")


def add_points(line_user_id: str, points: int, eco_score: int, reason: str):
    _call({
        "action": "addPoints",
        "line_user_id": line_user_id,
        "points": points,
        "eco_score": eco_score,
        "reason": reason
    })
    _invalidate_member(line_user_id)


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


# ─── Payments (สลิป + ยืนยันการจ่าย) ───────────

def save_payment(line_user_id: str, booking_id: str, amount: float,
                 slip_amount: float, slip_datetime: str, slip_ref: str,
                 auto_match: bool) -> dict:
    result = _call({
        "action": "savePayment",
        "line_user_id": line_user_id,
        "booking_id": booking_id,
        "amount": amount,
        "slip_amount": slip_amount,
        "slip_datetime": slip_datetime,
        "slip_ref": slip_ref,
        "auto_match": auto_match,
    })
    return result


def get_booking(booking_id: str) -> dict | None:
    result = _call({"action": "getBooking", "booking_id": booking_id})
    return result.get("data")


def get_latest_pending_booking(line_user_id: str) -> dict | None:
    """ดึงการจองล่าสุดที่ยังรอชำระเงินของผู้ใช้"""
    result = _call({"action": "getLatestPendingBooking", "line_user_id": line_user_id})
    return result.get("data")


# ─── Phase 3: My Bookings / Return / Eco ──────

def get_my_bookings(line_user_id: str) -> list:
    result = _call({"action": "getMyBookings", "line_user_id": line_user_id})
    return result.get("data", [])


def cancel_booking(booking_id: str, line_user_id: str) -> dict:
    return _call({"action": "cancelBooking", "booking_id": booking_id, "line_user_id": line_user_id})


def get_returnable(line_user_id: str) -> list:
    result = _call({"action": "getReturnable", "line_user_id": line_user_id})
    return result.get("data", [])


def return_equipment(booking_id: str, line_user_id: str, donate: bool) -> dict:
    result = _call({
        "action": "returnEquipment", "booking_id": booking_id,
        "line_user_id": line_user_id, "donate": donate
    })
    _invalidate_member(line_user_id)
    return result


def get_eco_stats(line_user_id: str) -> dict:
    result = _call({"action": "getEcoStats", "line_user_id": line_user_id})
    return result.get("data", {})
