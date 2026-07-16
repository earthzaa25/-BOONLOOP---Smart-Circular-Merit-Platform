import os
import logging
from flask import Flask, request, abort, send_file
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import Configuration, ApiClient, MessagingApi, MessagingApiBlob, ShowLoadingAnimationRequest
from linebot.v3.webhooks import (
    MessageEvent, TextMessageContent, ImageMessageContent, FollowEvent, PostbackEvent,
)

from handlers.message_handler import handle_text_message
from handlers.follow_handler import handle_follow
from handlers.postback_handler import handle_postback
from handlers.image_handler import handle_image_message
from services.rich_menu_service import setup_rich_menu

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

configuration = Configuration(access_token=os.environ.get("LINE_CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.environ.get("LINE_CHANNEL_SECRET"))


@app.route("/webhook", methods=["POST"])
def webhook():
    signature = request.headers.get("X-Line-Signature", "")
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        logger.error("Invalid signature")
        abort(400)
    return "OK"


@app.route("/health", methods=["GET"])
def health():
    # ตรวจว่า Railway รันโค้ดเวอร์ชันไหน (ไว้เช็คว่า deploy ใหม่ขึ้นจริงไหม)
    import importlib.util
    return {
        "status": "ok",
        "project": "BoonLoop",
        "version": "2026-07-08-fix-postback",
        "has_reply_helper": importlib.util.find_spec("utils.reply") is not None,
        "has_session_store": importlib.util.find_spec("services.session_store") is not None,
    }


@app.route("/qr", methods=["GET"])
def qr_image():
    """เสิร์ฟรูป QR PromptPay ด้วย content-type ที่ถูกต้อง (LINE ต้องการ)"""
    qr_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "promptpay-qr.jpg")
    if not os.path.exists(qr_path):
        abort(404)
    return send_file(qr_path, mimetype="image/jpeg")


@app.route("/setup-richmenu", methods=["GET"])
def setup_richmenu_route():
    """เรียกครั้งเดียวเพื่อสร้าง Rich Menu พร้อมรูป (เปิด URL นี้ในเบราว์เซอร์)"""
    try:
        with ApiClient(configuration) as api_client:
            line_bot_api = MessagingApi(api_client)
            blob_api = MessagingApiBlob(api_client)
            rid = setup_rich_menu(line_bot_api, blob_api)
        return {"status": "ok", "rich_menu_id": rid}
    except Exception as e:
        logger.error(f"setup richmenu route error: {e}")
        return {"status": "error", "message": str(e)}, 500


def _show_loading(line_bot_api, event, seconds=15):
    """แสดงจุดกำลังพิมพ์ (loading) ให้ผู้ใช้รู้ว่าระบบกำลังทำงาน"""
    try:
        user_id = getattr(event.source, "user_id", None)
        if user_id:
            line_bot_api.show_loading_animation(
                ShowLoadingAnimationRequest(chat_id=user_id, loading_seconds=seconds)
            )
    except Exception:
        pass  # ถ้าแสดง loading ไม่ได้ ไม่ต้องหยุดการทำงาน


@handler.add(FollowEvent)
def on_follow(event):
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        handle_follow(event, line_bot_api)


@handler.add(MessageEvent, message=TextMessageContent)
def on_message(event):
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        _show_loading(line_bot_api, event)
        handle_text_message(event, line_bot_api)


@handler.add(PostbackEvent)
def on_postback(event):
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        _show_loading(line_bot_api, event)
        handle_postback(event, line_bot_api)


@handler.add(MessageEvent, message=ImageMessageContent)
def on_image(event):
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        blob_api = MessagingApiBlob(api_client)
        _show_loading(line_bot_api, event, seconds=20)  # อ่านสลิปใช้เวลานานกว่า
        handle_image_message(event, line_bot_api, blob_api)


if __name__ == "__main__":
    # สร้าง Rich Menu เมื่อรัน server ครั้งแรก
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        blob_api = MessagingApiBlob(api_client)
        setup_rich_menu(line_bot_api, blob_api)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
