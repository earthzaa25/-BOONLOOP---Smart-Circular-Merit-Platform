import logging
from linebot.v3.messaging import (
    MessagingApi,
    RichMenuRequest,
    RichMenuArea,
    RichMenuBounds,
    RichMenuSize,
    MessageAction,
    URIAction,
    PostbackAction,
)

logger = logging.getLogger(__name__)

RICH_MENU_AREAS = [
    # แถวบน: 3 ปุ่ม
    RichMenuArea(
        bounds=RichMenuBounds(x=0, y=0, width=833, height=270),
        action=MessageAction(label="🌿 ทำบุญ", text="ทำบุญ"),
    ),
    RichMenuArea(
        bounds=RichMenuBounds(x=833, y=0, width=833, height=270),
        action=MessageAction(label="♻️ ผลกระทบ", text="ผลกระทบ"),
    ),
    RichMenuArea(
        bounds=RichMenuBounds(x=1666, y=0, width=834, height=270),
        action=MessageAction(label="🏆 คะแนนบุญ", text="คะแนน"),
    ),
    # แถวล่าง: 3 ปุ่ม
    RichMenuArea(
        bounds=RichMenuBounds(x=0, y=270, width=833, height=270),
        action=MessageAction(label="🛕 โครงการ", text="โครงการ"),
    ),
    RichMenuArea(
        bounds=RichMenuBounds(x=833, y=270, width=833, height=270),
        action=MessageAction(label="🎁 แลกรางวัล", text="แลกรางวัล"),
    ),
    RichMenuArea(
        bounds=RichMenuBounds(x=1666, y=270, width=834, height=270),
        action=MessageAction(label="♻️ คืนอุปกรณ์", text="คืนอุปกรณ์"),
    ),
]


def setup_rich_menu(line_bot_api: MessagingApi):
    """สร้าง Rich Menu และตั้งเป็น default"""
    try:
        rich_menu_request = RichMenuRequest(
            size=RichMenuSize(width=2500, height=540),
            selected=True,
            name="BoonLoop Main Menu",
            chat_bar_text="เมนู BoonLoop 🌿",
            areas=RICH_MENU_AREAS,
        )
        rich_menu_id = line_bot_api.create_rich_menu(
            rich_menu_request=rich_menu_request
        ).rich_menu_id

        line_bot_api.set_default_rich_menu(rich_menu_id)
        logger.info(f"Rich Menu created: {rich_menu_id}")
        return rich_menu_id
    except Exception as e:
        logger.error(f"setup_rich_menu error: {e}")
