import logging
from linebot.v3.messaging import (
    MessagingApi,
    MessagingApiBlob,
    ReplyMessageRequest,
    TextMessage,
)
from linebot.v3.webhooks import MessageEvent

from services.claude_service import read_slip
from services.sheets_service import (
    get_latest_pending_booking, save_payment, get_member,
)
from services.notify_service import notify_admins

logger = logging.getLogger(__name__)


def handle_image_message(event: MessageEvent, line_bot_api: MessagingApi,
                         blob_api: MessagingApiBlob):
    """รับรูปสลิป → Claude อ่าน → เช็คยอด → บันทึก → แจ้ง Admin"""
    user_id = event.source.user_id
    reply_token = event.reply_token
    message_id = event.message.id

    # หาการจองที่รอชำระเงินล่าสุด
    booking = get_latest_pending_booking(user_id)
    if not booking:
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=reply_token,
                messages=[TextMessage(text="ไม่พบรายการจองที่รอชำระเงิน\nพิมพ์ 'ทำบุญ' เพื่อเริ่มจองใหม่ 🙏")],
            )
        )
        return

    try:
        # ดึงรูปจาก LINE
        image_bytes = blob_api.get_message_content(message_id=message_id)

        # ให้ Claude อ่านสลิป
        slip = read_slip(image_bytes)

        expected = float(booking.get("price", 0))
        slip_amount = float(slip.get("amount", 0) or 0)
        is_slip = slip.get("is_slip", False)
        auto_match = is_slip and abs(slip_amount - expected) < 0.01

        # บันทึกข้อมูลการจ่าย
        save_payment(
            line_user_id=user_id,
            booking_id=booking.get("booking_id", ""),
            amount=expected,
            slip_amount=slip_amount,
            slip_datetime=slip.get("date_time", ""),
            slip_ref=slip.get("ref", ""),
            auto_match=auto_match,
        )

        # ตอบผู้ใช้
        if auto_match:
            user_msg = (
                f"✅ ได้รับสลิปแล้ว!\n\n"
                f"💰 ยอด: {slip_amount} บาท (ตรงกับที่จอง)\n"
                f"📋 รหัสจอง: {booking.get('booking_id')}\n\n"
                f"รอเจ้าหน้าที่ยืนยันขั้นสุดท้าย\nจะแจ้งผลให้ทราบเร็วๆ นี้ 🙏"
            )
        else:
            reason = "ไม่ใช่สลิปโอนเงิน" if not is_slip else f"ยอดไม่ตรง (สลิป {slip_amount} / ต้องจ่าย {expected})"
            user_msg = (
                f"⚠️ ได้รับสลิปแล้ว แต่ต้องตรวจสอบเพิ่มเติม\n"
                f"({reason})\n\n"
                f"เจ้าหน้าที่จะตรวจสอบและแจ้งผลให้ทราบ 🙏"
            )

        line_bot_api.reply_message(
            ReplyMessageRequest(reply_token=reply_token, messages=[TextMessage(text=user_msg)])
        )

        # แจ้ง Admin
        member = get_member(user_id)
        member_name = member.get("display_name", "ไม่ทราบชื่อ") if member else "ไม่ทราบชื่อ"
        status_icon = "✅ ตรงอัตโนมัติ" if auto_match else "⚠️ ต้องตรวจ"
        admin_msg = (
            f"🔔 มีสลิปใหม่ {status_icon}\n\n"
            f"👤 {member_name}\n"
            f"📋 {booking.get('booking_id')}\n"
            f"🕯️ {booking.get('package_name')}\n"
            f"💰 ต้องจ่าย: {expected} บาท\n"
            f"📄 สลิประบุ: {slip_amount} บาท\n"
            f"🕐 {slip.get('date_time', '-')}\n\n"
            f"เปิดเว็บ Admin เพื่อยืนยัน 🙏"
        )
        notify_admins(line_bot_api, admin_msg)

    except Exception as e:
        logger.error(f"handle_image_message error: {e}")
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=reply_token,
                messages=[TextMessage(text="เกิดข้อผิดพลาดในการอ่านสลิป กรุณาส่งใหม่อีกครั้ง 🙏")],
            )
        )
