import os
import logging
from linebot.v3.messaging import MessagingApi, PushMessageRequest, TextMessage

logger = logging.getLogger(__name__)

# LINE User ID ของ Admin (คั่นด้วย comma ถ้ามีหลายคน)
ADMIN_USER_IDS = [
    uid.strip()
    for uid in os.environ.get("ADMIN_USER_IDS", "").split(",")
    if uid.strip()
]


def notify_admins(line_bot_api: MessagingApi, message: str):
    """ส่งข้อความแจ้งเตือน Admin ทุกคนผ่าน LINE Push"""
    if not ADMIN_USER_IDS:
        logger.warning("ADMIN_USER_IDS not set — ไม่มี admin ให้แจ้งเตือน")
        return
    for admin_id in ADMIN_USER_IDS:
        try:
            line_bot_api.push_message(
                PushMessageRequest(
                    to=admin_id,
                    messages=[TextMessage(text=message)],
                )
            )
        except Exception as e:
            logger.error(f"notify_admins error ({admin_id}): {e}")
