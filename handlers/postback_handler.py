import logging
from urllib.parse import parse_qs
from linebot.v3.messaging import MessagingApi
from linebot.v3.webhooks import PostbackEvent

from handlers.booking_handler import handle_booking_postback

logger = logging.getLogger(__name__)


def handle_postback(event: PostbackEvent, line_bot_api: MessagingApi):
    user_id = event.source.user_id
    reply_token = event.reply_token
    data_str = event.postback.data

    # parse "action=booking&step=type&value=khao_phansa"
    parsed = parse_qs(data_str)
    data = {k: v[0] for k, v in parsed.items()}

    action = data.get("action")

    if action == "booking":
        handle_booking_postback(user_id, data, reply_token, line_bot_api)
    else:
        logger.warning(f"Unknown postback action: {action}")
