import logging
from urllib.parse import parse_qs
from linebot.v3.messaging import MessagingApi
from linebot.v3.webhooks import PostbackEvent

from handlers.booking_handler import handle_booking_postback
from handlers.phase3_handler import handle_cancel, handle_return

logger = logging.getLogger(__name__)


def handle_postback(event: PostbackEvent, line_bot_api: MessagingApi):
    user_id = event.source.user_id
    reply_token = event.reply_token
    data_str = event.postback.data

    parsed = parse_qs(data_str)
    data = {k: v[0] for k, v in parsed.items()}

    # ถ้าผู้ใช้เลือกวันจากปฏิทิน LINE จะส่งวันมาแยกใน params
    params = getattr(event.postback, "params", None)
    if params:
        picked = params.get("date") if isinstance(params, dict) else getattr(params, "date", None)
        if picked:
            data["picked_date"] = picked

    action = data.get("action")

    if action == "booking":
        handle_booking_postback(user_id, data, reply_token, line_bot_api)
    elif action == "cancel":
        handle_cancel(user_id, data.get("value", ""), reply_token, line_bot_api)
    elif action == "return":
        donate = data.get("donate", "0") == "1"
        handle_return(user_id, data.get("value", ""), donate, reply_token, line_bot_api)
    else:
        logger.warning(f"Unknown postback action: {action}")
