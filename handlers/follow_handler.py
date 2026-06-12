import logging
from linebot.v3.messaging import (
    MessagingApi,
    ReplyMessageRequest,
    TextMessage,
    FlexMessage,
    FlexContainer,
)
from linebot.v3.webhooks import FollowEvent

from services.sheets_service import get_member, register_member, add_points
from config.constants import BOON_POINTS
from utils.flex_messages import build_welcome_flex

logger = logging.getLogger(__name__)


def handle_follow(event: FollowEvent, line_bot_api: MessagingApi):
    """เมื่อผู้ใช้ follow LINE OA — สมัครสมาชิกอัตโนมัติ"""
    user_id = event.source.user_id
    reply_token = event.reply_token

    try:
        # ดึงชื่อจาก LINE profile
        profile = line_bot_api.get_profile(user_id)
        display_name = profile.display_name
    except Exception:
        display_name = "สมาชิกใหม่"

    try:
        existing = get_member(user_id)
        if existing:
            # สมาชิกเก่า — แค่ทักทาย
            reply_text = f"ยินดีต้อนรับกลับ {display_name}! 🙏\nคะแนนบุญของคุณ: {existing.get('boon_points', 0)} คะแนน"
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=reply_token,
                    messages=[TextMessage(text=reply_text)],
                )
            )
        else:
            # สมาชิกใหม่ — บันทึกและให้คะแนน
            member = register_member(user_id, display_name)
            add_points(user_id, BOON_POINTS["register"], 0, "สมัครสมาชิกใหม่")

            flex = build_welcome_flex(display_name, member["member_id"])
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=reply_token,
                    messages=[flex],
                )
            )
    except Exception as e:
        logger.error(f"handle_follow error: {e}")
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=reply_token,
                messages=[TextMessage(text="ยินดีต้อนรับสู่ BoonLoop 🌿")],
            )
        )
