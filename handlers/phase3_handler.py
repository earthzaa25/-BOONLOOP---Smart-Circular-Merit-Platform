import logging
from linebot.v3.messaging import MessagingApi, ReplyMessageRequest, TextMessage

from services.sheets_service import (
    get_my_bookings, cancel_booking, get_returnable, return_equipment, get_eco_stats,
)
from utils.phase3_flex import (
    build_my_bookings_flex, build_returnable_flex, build_eco_flex,
)

logger = logging.getLogger(__name__)


def show_my_bookings(user_id, reply_token, line_bot_api):
    bookings = get_my_bookings(user_id)
    flex = build_my_bookings_flex(bookings)
    line_bot_api.reply_message(
        ReplyMessageRequest(reply_token=reply_token, messages=[flex])
    )


def show_returnable(user_id, reply_token, line_bot_api):
    items = get_returnable(user_id)
    flex = build_returnable_flex(items)
    line_bot_api.reply_message(
        ReplyMessageRequest(reply_token=reply_token, messages=[flex])
    )


def show_eco(user_id, reply_token, line_bot_api):
    stats = get_eco_stats(user_id)
    flex = build_eco_flex(stats)
    line_bot_api.reply_message(
        ReplyMessageRequest(reply_token=reply_token, messages=[flex])
    )


# ─── Postback handlers ──────────────────────────
def handle_cancel(user_id, booking_id, reply_token, line_bot_api):
    result = cancel_booking(booking_id, user_id)
    if result.get("success"):
        msg = f"ยกเลิกการจอง #{booking_id} เรียบร้อยแล้ว 🙏"
    else:
        msg = f"ยกเลิกไม่สำเร็จ: {result.get('error', 'กรุณาลองใหม่')}"
    line_bot_api.reply_message(
        ReplyMessageRequest(reply_token=reply_token, messages=[TextMessage(text=msg)])
    )


def handle_return(user_id, booking_id, donate, reply_token, line_bot_api):
    result = return_equipment(booking_id, user_id, donate)
    if result.get("success"):
        action = "บริจาค" if donate else "คืน"
        msg = (
            f"✅ {action}อุปกรณ์เรียบร้อย!\n"
            f"#{booking_id}\n\n"
            f"🏆 ได้รับ 30 คะแนนบุญ + 5 Eco Score\n"
            f"ขอบคุณที่ร่วมรักษ์โลก 🌍🙏"
        )
    else:
        msg = f"ดำเนินการไม่สำเร็จ: {result.get('error', 'กรุณาลองใหม่')}"
    line_bot_api.reply_message(
        ReplyMessageRequest(reply_token=reply_token, messages=[TextMessage(text=msg)])
    )
