import logging
from linebot.v3.messaging import (
    MessagingApi,
    ReplyMessageRequest,
    TextMessage,
)
from linebot.v3.webhooks import MessageEvent

from config.constants import KEYWORDS, MERIT_PACKAGES
from services.sheets_service import get_member, get_points_summary
from handlers.booking_handler import start_booking
from utils.flex_messages import (
    build_booking_menu_flex,
    build_points_flex,
    build_project_info_flex,
    build_return_equipment_flex,
    build_help_flex,
)

logger = logging.getLogger(__name__)


def handle_text_message(event: MessageEvent, line_bot_api: MessagingApi):
    user_id = event.source.user_id
    text = event.message.text.strip()
    reply_token = event.reply_token

    # คำสั่งพิเศษ: ดู LINE User ID ของตัวเอง (สำหรับตั้งค่า Admin)
    if text.lower() in ("myid", "my id", "ไอดี"):
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=reply_token,
                messages=[TextMessage(text=f"LINE User ID ของคุณ:\n{user_id}")],
            )
        )
        return

    # หา intent จาก keyword
    intent = _detect_intent(text)

    try:
        if intent == "REGISTER":
            _handle_register_check(user_id, reply_token, line_bot_api)
        elif intent == "MENU_BOOKING":
            _handle_booking_menu(user_id, reply_token, line_bot_api)
        elif intent == "MENU_POINTS":
            _handle_points(user_id, reply_token, line_bot_api)
        elif intent == "MENU_ECO":
            _handle_eco(user_id, reply_token, line_bot_api)
        elif intent == "MENU_PROJECT":
            _handle_project(reply_token, line_bot_api)
        elif intent == "MENU_RETURN":
            _handle_return(reply_token, line_bot_api)
        elif intent == "MENU_REWARD":
            _handle_reward(reply_token, line_bot_api)
        elif intent == "GREETING":
            _handle_greeting(user_id, reply_token, line_bot_api)
        else:
            _handle_help(reply_token, line_bot_api)
    except Exception as e:
        logger.error(f"handle_text_message error: {e}")
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=reply_token,
                messages=[TextMessage(text="ขออภัย เกิดข้อผิดพลาด กรุณาลองใหม่อีกครั้ง 🙏")],
            )
        )


def _detect_intent(text: str) -> str:
    text_lower = text.lower()
    for keyword, intent in KEYWORDS.items():
        if keyword in text_lower:
            return intent
    return "HELP"


def _handle_register_check(user_id, reply_token, line_bot_api):
    member = get_member(user_id)
    if member:
        msg = f"คุณเป็นสมาชิก BoonLoop แล้ว ✅\nรหัส: {member.get('member_id')}\nคะแนนบุญ: {member.get('boon_points', 0)} คะแนน"
    else:
        msg = "กรุณา Follow LINE OA ของเราเพื่อสมัครสมาชิกอัตโนมัติ 🌿"
    line_bot_api.reply_message(
        ReplyMessageRequest(reply_token=reply_token, messages=[TextMessage(text=msg)])
    )


def _handle_booking_menu(user_id, reply_token, line_bot_api):
    # เริ่มระบบจอง 7 ขั้นตอน
    start_booking(user_id, reply_token, line_bot_api)


def _handle_points(user_id, reply_token, line_bot_api):
    summary = get_points_summary(user_id)
    flex = build_points_flex(summary)
    line_bot_api.reply_message(
        ReplyMessageRequest(reply_token=reply_token, messages=[flex])
    )


def _handle_eco(user_id, reply_token, line_bot_api):
    summary = get_points_summary(user_id)
    eco = summary.get("eco_score", 0)
    bookings = summary.get("total_bookings", 0)
    waste_reduced = bookings * 0.5  # ประมาณ 0.5 kg ต่อครั้ง
    msg = (
        f"♻️ Eco Dashboard ของคุณ\n\n"
        f"🌿 Eco Score: {eco} คะแนน\n"
        f"📦 ร่วมกิจกรรม: {bookings} ครั้ง\n"
        f"🗑️ ขยะที่ลดได้: {waste_reduced:.1f} kg\n"
        f"♻️ วัสดุหมุนเวียน: {bookings} ชุด\n\n"
        f"ขอบคุณที่ร่วมดูแลโลก 🌍"
    )
    line_bot_api.reply_message(
        ReplyMessageRequest(reply_token=reply_token, messages=[TextMessage(text=msg)])
    )


def _handle_project(reply_token, line_bot_api):
    flex = build_project_info_flex()
    line_bot_api.reply_message(
        ReplyMessageRequest(reply_token=reply_token, messages=[flex])
    )


def _handle_return(reply_token, line_bot_api):
    flex = build_return_equipment_flex()
    line_bot_api.reply_message(
        ReplyMessageRequest(reply_token=reply_token, messages=[flex])
    )


def _handle_reward(reply_token, line_bot_api):
    msg = (
        "🎁 แลกรางวัล BoonLoop\n\n"
        "50 คะแนน → ส่วนลด 5%\n"
        "100 คะแนน → ส่วนลด 10%\n"
        "200 คะแนน → ชุดบุญฟรี 1 ชุด\n"
        "500 คะแนน → ของที่ระลึกพิเศษ\n\n"
        "พิมพ์ 'คะแนน' เพื่อดูคะแนนของคุณ 🏆"
    )
    line_bot_api.reply_message(
        ReplyMessageRequest(reply_token=reply_token, messages=[TextMessage(text=msg)])
    )


def _handle_greeting(user_id, reply_token, line_bot_api):
    member = get_member(user_id)
    name = member.get("display_name", "สมาชิก") if member else "คุณ"
    msg = f"สวัสดีคะ {name}! 🙏\nยินดีต้อนรับสู่ BoonLoop\nแพลตฟอร์มบุญรักษ์โลก 🌿"
    line_bot_api.reply_message(
        ReplyMessageRequest(reply_token=reply_token, messages=[TextMessage(text=msg)])
    )


def _handle_help(reply_token, line_bot_api):
    flex = build_help_flex()
    line_bot_api.reply_message(
        ReplyMessageRequest(reply_token=reply_token, messages=[flex])
    )
