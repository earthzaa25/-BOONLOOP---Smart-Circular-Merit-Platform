import logging
from datetime import datetime, timedelta
from linebot.v3.messaging import (
    MessagingApi,
    ReplyMessageRequest,
    TextMessage,
)

from config.constants import MERIT_PACKAGES
from services.sheets_service import (
    get_member, set_session, get_session, clear_session, create_booking,
)
from utils.booking_flex import (
    build_package_type_flex,
    build_package_items_flex,
    build_date_picker_flex,
    build_location_flex,
    build_time_flex,
    build_ceremony_flex,
    build_payment_flex,
    build_confirm_flex,
    build_booking_success_flex,
)

logger = logging.getLogger(__name__)

# ขั้นตอนการจอง
STEP_SELECT_TYPE = "select_type"
STEP_SELECT_ITEM = "select_item"
STEP_SELECT_DATE = "select_date"
STEP_SELECT_LOCATION = "select_location"
STEP_SELECT_TIME = "select_time"
STEP_SELECT_CEREMONY = "select_ceremony"
STEP_SELECT_PAYMENT = "select_payment"
STEP_CONFIRM = "confirm"

# สถานที่รับชุด (แก้ไขได้)
LOCATIONS = [
    "วัดหนองขาว",
    "ศาลเจ้าชุมชน",
    "โรงเรียนหนองขาวโกวิทพิทยาคม",
    "ศูนย์ BoonLoop",
]

# ช่วงเวลารับ
TIME_SLOTS = ["09:00-10:00", "10:00-11:00", "13:00-14:00", "15:00-16:00"]


def start_booking(user_id, reply_token, line_bot_api):
    """เริ่มการจอง — Step 1: เลือกประเภทชุด"""
    member = get_member(user_id)
    if not member:
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=reply_token,
                messages=[TextMessage(text="กรุณาสมัครสมาชิกก่อนนะคะ พิมพ์ 'สมัคร' 🙏")],
            )
        )
        return
    set_session(user_id, STEP_SELECT_TYPE, {})
    flex = build_package_type_flex()
    line_bot_api.reply_message(
        ReplyMessageRequest(reply_token=reply_token, messages=[flex])
    )


def handle_booking_postback(user_id, data: dict, reply_token, line_bot_api):
    """จัดการ postback ระหว่างการจอง

    data เช่น {"action": "booking", "step": "type", "value": "khao_phansa"}
    """
    step = data.get("step")
    value = data.get("value")

    session = get_session(user_id)
    session_data = session.get("session_data", {}) if session else {}

    try:
        if step == "type":
            _step_item(user_id, value, session_data, reply_token, line_bot_api)
        elif step == "item":
            _step_date(user_id, value, session_data, reply_token, line_bot_api)
        elif step == "date":
            _step_location(user_id, value, session_data, reply_token, line_bot_api)
        elif step == "location":
            _step_time(user_id, value, session_data, reply_token, line_bot_api)
        elif step == "time":
            _step_ceremony(user_id, value, session_data, reply_token, line_bot_api)
        elif step == "ceremony":
            _step_payment(user_id, value, session_data, reply_token, line_bot_api)
        elif step == "payment":
            _step_confirm(user_id, value, session_data, reply_token, line_bot_api)
        elif step == "confirm":
            _finalize_booking(user_id, value, session_data, reply_token, line_bot_api)
        elif step == "cancel":
            clear_session(user_id)
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=reply_token,
                    messages=[TextMessage(text="ยกเลิกการจองแล้ว 🙏 พิมพ์ 'ทำบุญ' เพื่อเริ่มใหม่")],
                )
            )
    except Exception as e:
        logger.error(f"booking postback error: {e}")
        clear_session(user_id)
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=reply_token,
                messages=[TextMessage(text="เกิดข้อผิดพลาด กรุณาเริ่มจองใหม่ พิมพ์ 'ทำบุญ' 🙏")],
            )
        )


# ─── Step 2: เลือกชุดในประเภทนั้น ───────────────
def _step_item(user_id, package_type, session_data, reply_token, line_bot_api):
    if package_type not in MERIT_PACKAGES:
        package_type = "khao_phansa"
    session_data["package_type"] = package_type
    set_session(user_id, STEP_SELECT_ITEM, session_data)
    flex = build_package_items_flex(package_type)
    line_bot_api.reply_message(
        ReplyMessageRequest(reply_token=reply_token, messages=[flex])
    )


# ─── Step 3: เลือกวันรับ ────────────────────────
def _step_date(user_id, item_key, session_data, reply_token, line_bot_api):
    pkg_type = session_data.get("package_type", "khao_phansa")
    item = MERIT_PACKAGES[pkg_type]["items"].get(item_key)
    if not item:
        raise ValueError("invalid item")
    session_data["package_name"] = item["name"]
    session_data["price"] = item["price"]
    session_data["eco_score"] = item["eco_score"]
    set_session(user_id, STEP_SELECT_DATE, session_data)
    flex = build_date_picker_flex()
    line_bot_api.reply_message(
        ReplyMessageRequest(reply_token=reply_token, messages=[flex])
    )


# ─── Step 4: เลือกสถานที่ ───────────────────────
def _step_location(user_id, date_value, session_data, reply_token, line_bot_api):
    session_data["pickup_date"] = date_value
    set_session(user_id, STEP_SELECT_LOCATION, session_data)
    flex = build_location_flex(LOCATIONS)
    line_bot_api.reply_message(
        ReplyMessageRequest(reply_token=reply_token, messages=[flex])
    )


# ─── Step 5: เลือกเวลา ──────────────────────────
def _step_time(user_id, location_idx, session_data, reply_token, line_bot_api):
    idx = int(location_idx)
    session_data["location"] = LOCATIONS[idx]
    set_session(user_id, STEP_SELECT_TIME, session_data)
    flex = build_time_flex(TIME_SLOTS)
    line_bot_api.reply_message(
        ReplyMessageRequest(reply_token=reply_token, messages=[flex])
    )


# ─── Step 6: เลือกรูปแบบพิธี ─────────────────────
def _step_ceremony(user_id, time_idx, session_data, reply_token, line_bot_api):
    idx = int(time_idx)
    session_data["pickup_time"] = TIME_SLOTS[idx]
    set_session(user_id, STEP_SELECT_CEREMONY, session_data)
    flex = build_ceremony_flex()
    line_bot_api.reply_message(
        ReplyMessageRequest(reply_token=reply_token, messages=[flex])
    )


# ─── Step 7: เลือกการชำระเงิน ────────────────────
def _step_payment(user_id, ceremony, session_data, reply_token, line_bot_api):
    ceremony_map = {"self": "เข้าร่วมพิธีด้วยตนเอง", "community": "มอบหมายให้ชุมชนดำเนินการ"}
    session_data["ceremony_type"] = ceremony_map.get(ceremony, ceremony)
    set_session(user_id, STEP_SELECT_PAYMENT, session_data)
    flex = build_payment_flex()
    line_bot_api.reply_message(
        ReplyMessageRequest(reply_token=reply_token, messages=[flex])
    )


# ─── ยืนยันการจอง ───────────────────────────────
def _step_confirm(user_id, payment_method, session_data, reply_token, line_bot_api):
    payment_map = {"qr": "QR Payment", "promptpay": "PromptPay", "cash": "เงินสด (มัดจำ)"}
    session_data["payment_method"] = payment_map.get(payment_method, payment_method)
    set_session(user_id, STEP_CONFIRM, session_data)
    flex = build_confirm_flex(session_data)
    line_bot_api.reply_message(
        ReplyMessageRequest(reply_token=reply_token, messages=[flex])
    )


# ─── บันทึกลง Sheet ─────────────────────────────
def _finalize_booking(user_id, value, session_data, reply_token, line_bot_api):
    if value != "yes":
        clear_session(user_id)
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=reply_token,
                messages=[TextMessage(text="ยกเลิกการจองแล้ว 🙏")],
            )
        )
        return

    booking_id = create_booking(
        line_user_id=user_id,
        package_type=session_data.get("package_type", ""),
        package_name=session_data.get("package_name", ""),
        price=session_data.get("price", 0),
        pickup_date=session_data.get("pickup_date", ""),
        location=session_data.get("location", ""),
        eco_score=session_data.get("eco_score", 10),
    )
    clear_session(user_id)
    flex = build_booking_success_flex(booking_id, session_data)
    line_bot_api.reply_message(
        ReplyMessageRequest(reply_token=reply_token, messages=[flex])
    )
