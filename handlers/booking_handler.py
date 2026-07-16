import logging
from datetime import datetime, timedelta
from linebot.v3.messaging import (
    MessagingApi,
    ReplyMessageRequest,
    TextMessage,
    ImageMessage,
)

from config.constants import MERIT_PACKAGES
from services.sheets_service import (
    get_member, create_booking,
)
from services.session_store import set_session, get_session, clear_session
from services.content_service import get_packages, get_options, find_category, get_events
from utils.promptpay import get_qr_url, is_static_qr, get_static_qr_url
from utils.reply import safe_reply
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


def start_booking(user_id, reply_token, line_bot_api):
    """เริ่มการจอง — Step 1: เลือกประเภทชุด (ดึงจาก Google Sheet)"""
    member = get_member(user_id)
    if not member:
        safe_reply(line_bot_api, reply_token, [TextMessage(text="กรุณาสมัครสมาชิกก่อนนะคะ พิมพ์ 'สมัคร' 🙏")], user_id)
        return

    packages = get_packages()
    if not packages:
        safe_reply(line_bot_api, reply_token, [TextMessage(text="ขณะนี้ยังไม่มีกิจกรรมเปิดให้จอง กรุณาติดตามข่าวสารเร็วๆ นี้ 🙏")], user_id)
        return

    set_session(user_id, STEP_SELECT_TYPE, {})
    flex = build_package_type_flex(packages)
    safe_reply(line_bot_api, reply_token, [flex], user_id)


def handle_booking_postback(user_id, data: dict, reply_token, line_bot_api):
    """จัดการ postback ระหว่างการจอง

    data เช่น {"action": "booking", "step": "type", "value": "khao_phansa"}
    """
    step = data.get("step")
    value = data.get("value")

    # วันที่จากปฏิทินมาเป็น 2026-07-20 → แปลงเป็น 20/07/2026
    picked = data.get("picked_date")
    if step == "date" and picked:
        try:
            value = datetime.strptime(picked, "%Y-%m-%d").strftime("%d/%m/%Y")
        except ValueError:
            logger.warning(f"รูปแบบวันที่ไม่ถูกต้อง: {picked}")

    session = get_session(user_id)
    session_data = session.get("session_data", {}) if session else {}

    # ถ้าจองค้างไว้นานจน session หมดอายุ — บอกให้ชัด ไม่ใช่ error งงๆ
    if step not in ("type", "cancel") and not session_data:
        logger.warning(f"session หาย/หมดอายุ (user={user_id[:8]}… step={step})")
        safe_reply(
            line_bot_api, reply_token,
            [TextMessage(text="การจองนี้หมดอายุแล้ว (เกิน 30 นาที)\nพิมพ์ 'ทำบุญ' เพื่อเริ่มจองใหม่ 🙏")],
            user_id,
        )
        return

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
            safe_reply(line_bot_api, reply_token, [TextMessage(text="ยกเลิกการจองแล้ว 🙏 พิมพ์ 'ทำบุญ' เพื่อเริ่มใหม่")], user_id)
    except Exception as e:
        logger.error(f"booking postback error: {e}")
        clear_session(user_id)
        safe_reply(line_bot_api, reply_token, [TextMessage(text="เกิดข้อผิดพลาด กรุณาเริ่มจองใหม่ พิมพ์ 'ทำบุญ' 🙏")], user_id)


# ─── Step 2: เลือกชุดในประเภทนั้น ───────────────
def _step_item(user_id, package_type, session_data, reply_token, line_bot_api):
    packages = get_packages()
    cat = find_category(packages, package_type)
    if not cat:
        # fallback ไปประเภทแรกที่มี
        cat = packages[0] if packages else None
        if not cat:
            raise ValueError("no packages")
        package_type = cat["category"]
    session_data["package_type"] = package_type
    set_session(user_id, STEP_SELECT_ITEM, session_data)
    flex = build_package_items_flex(cat)
    safe_reply(line_bot_api, reply_token, [flex], user_id)


# ─── Step 3: เลือกวันรับ ────────────────────────
def _step_date(user_id, item_idx, session_data, reply_token, line_bot_api):
    pkg_type = session_data.get("package_type")
    packages = get_packages()
    cat = find_category(packages, pkg_type)
    if not cat:
        raise ValueError("invalid category")
    idx = int(item_idx)
    items = cat["items"]
    if idx < 0 or idx >= len(items):
        raise ValueError("invalid item index")
    item = items[idx]
    session_data["package_name"] = item["name"]
    session_data["price"] = item["price"]
    session_data["eco_score"] = item["eco_score"]
    set_session(user_id, STEP_SELECT_DATE, session_data)
    flex = build_date_picker_flex(get_events())
    safe_reply(line_bot_api, reply_token, [flex], user_id)


# ─── Step 4: เลือกสถานที่ ───────────────────────
def _step_location(user_id, date_value, session_data, reply_token, line_bot_api):
    session_data["pickup_date"] = date_value
    set_session(user_id, STEP_SELECT_LOCATION, session_data)
    locations = get_options().get("location", [])
    flex = build_location_flex(locations)
    safe_reply(line_bot_api, reply_token, [flex], user_id)


# ─── Step 5: เลือกเวลา ──────────────────────────
def _step_time(user_id, location_idx, session_data, reply_token, line_bot_api):
    idx = int(location_idx)
    locations = get_options().get("location", [])
    session_data["location"] = locations[idx] if idx < len(locations) else ""
    set_session(user_id, STEP_SELECT_TIME, session_data)
    time_slots = get_options().get("time", [])
    flex = build_time_flex(time_slots)
    safe_reply(line_bot_api, reply_token, [flex], user_id)


# ─── Step 6: เลือกรูปแบบพิธี ─────────────────────
def _step_ceremony(user_id, time_idx, session_data, reply_token, line_bot_api):
    idx = int(time_idx)
    time_slots = get_options().get("time", [])
    session_data["pickup_time"] = time_slots[idx] if idx < len(time_slots) else ""
    set_session(user_id, STEP_SELECT_CEREMONY, session_data)
    ceremonies = get_options().get("ceremony", [])
    flex = build_ceremony_flex(ceremonies)
    safe_reply(line_bot_api, reply_token, [flex], user_id)


# ─── Step 7: เลือกการชำระเงิน ────────────────────
def _step_payment(user_id, ceremony_idx, session_data, reply_token, line_bot_api):
    idx = int(ceremony_idx)
    ceremonies = get_options().get("ceremony", [])
    session_data["ceremony_type"] = ceremonies[idx] if idx < len(ceremonies) else ""
    set_session(user_id, STEP_SELECT_PAYMENT, session_data)
    flex = build_payment_flex()
    safe_reply(line_bot_api, reply_token, [flex], user_id)


# ─── ยืนยันการจอง ───────────────────────────────
def _step_confirm(user_id, payment_method, session_data, reply_token, line_bot_api):
    payment_map = {"qr": "QR Payment", "promptpay": "PromptPay", "cash": "เงินสด (มัดจำ)"}
    session_data["payment_method"] = payment_map.get(payment_method, payment_method)
    set_session(user_id, STEP_CONFIRM, session_data)
    flex = build_confirm_flex(session_data)
    safe_reply(line_bot_api, reply_token, [flex], user_id)


# ─── บันทึกลง Sheet ─────────────────────────────
def _finalize_booking(user_id, value, session_data, reply_token, line_bot_api):
    if value != "yes":
        clear_session(user_id)
        safe_reply(line_bot_api, reply_token, [TextMessage(text="ยกเลิกการจองแล้ว 🙏")], user_id)
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

    price = session_data.get("price", 0)
    payment_method = session_data.get("payment_method", "")
    messages = [build_booking_success_flex(booking_id, session_data)]

    # ถ้าเลือก QR/PromptPay → ส่ง QR code + วิธีจ่าย
    if "เงินสด" not in payment_method:
        if is_static_qr():
            # ใช้รูป QR static — ลูกค้าต้องกรอกยอดเอง
            qr_url = get_static_qr_url()
            messages.append(ImageMessage(original_content_url=qr_url, preview_image_url=qr_url))
            messages.append(TextMessage(
                text=(
                    f"💸 สแกน QR ด้านบนเพื่อชำระเงิน\n\n"
                    f"⚠️ กรุณากรอกยอด *{price} บาท* ด้วยตนเอง\n"
                    f"(QR นี้ไม่ได้ระบุยอดอัตโนมัติ)\n\n"
                    f"หลังโอนแล้ว กรุณา *ส่งรูปสลิป* กลับมาในแชทนี้\n"
                    f"ระบบจะตรวจสอบให้ 🙏"
                )
            ))
        else:
            # สร้าง QR แบบมียอดอัตโนมัติ
            qr_url = get_qr_url(price)
            messages.append(ImageMessage(original_content_url=qr_url, preview_image_url=qr_url))
            messages.append(TextMessage(
                text=(
                    f"💸 สแกน QR เพื่อชำระ {price} บาท\n\n"
                    f"หลังโอนแล้ว กรุณา *ส่งรูปสลิป* กลับมาในแชทนี้\n"
                    f"ระบบจะตรวจสอบอัตโนมัติ 🙏"
                )
            ))
    else:
        messages.append(TextMessage(
            text=f"💵 ชำระเงินสด {price} บาท ตอนรับชุดที่ {session_data.get('location', '')} 🙏"
        ))

    safe_reply(line_bot_api, reply_token, messages, user_id)
