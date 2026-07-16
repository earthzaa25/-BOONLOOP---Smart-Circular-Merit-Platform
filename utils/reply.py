import logging
from linebot.v3.messaging import (
    ReplyMessageRequest,
    PushMessageRequest,
)

logger = logging.getLogger(__name__)


def safe_reply(line_bot_api, reply_token, messages, user_id=None):
    """ตอบกลับผู้ใช้ พร้อมตาข่ายกันตก

    ถ้า reply ไม่สำเร็จ (เช่น reply token หมดอายุเพราะระบบช้า)
    จะเปลี่ยนไปใช้ push แทน เพื่อให้ผู้ใช้ได้รับข้อความเสมอ
    """
    if not isinstance(messages, list):
        messages = [messages]
    try:
        line_bot_api.reply_message(
            ReplyMessageRequest(reply_token=reply_token, messages=messages)
        )
        return True
    except Exception as e:
        logger.warning(f"reply ไม่สำเร็จ ({e}) — ลองใช้ push แทน")
        if not user_id:
            return False
        try:
            line_bot_api.push_message(
                PushMessageRequest(to=user_id, messages=messages)
            )
            logger.info("ส่งด้วย push สำเร็จ")
            return True
        except Exception as e2:
            logger.error(f"push ก็ไม่สำเร็จ: {e2}")
            return False
