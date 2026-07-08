import os
import logging
import requests
from linebot.v3.messaging import (
    MessagingApi,
    MessagingApiBlob,
    RichMenuRequest,
    RichMenuArea,
    RichMenuBounds,
    RichMenuSize,
    MessageAction,
)

logger = logging.getLogger(__name__)

# รูปพื้นหลัง Rich Menu ขนาด 2500 x 1686 (2 แถว 3 คอลัมน์)
W = 833
H = 843

RICH_MENU_AREAS = [
    # ── แถวบน ──
    RichMenuArea(
        bounds=RichMenuBounds(x=0, y=0, width=W, height=H),
        action=MessageAction(label="ทำบุญ", text="ทำบุญ"),
    ),
    RichMenuArea(
        bounds=RichMenuBounds(x=W, y=0, width=W, height=H),
        action=MessageAction(label="ผลกระทบ", text="ผลกระทบ"),
    ),
    RichMenuArea(
        bounds=RichMenuBounds(x=W * 2, y=0, width=834, height=H),
        action=MessageAction(label="คะแนนบุญ", text="คะแนน"),
    ),
    # ── แถวล่าง ──
    RichMenuArea(
        bounds=RichMenuBounds(x=0, y=H, width=W, height=843),
        action=MessageAction(label="โครงการ", text="โครงการ"),
    ),
    RichMenuArea(
        bounds=RichMenuBounds(x=W, y=H, width=W, height=843),
        action=MessageAction(label="แลกรางวัล", text="แลกรางวัล"),
    ),
    RichMenuArea(
        bounds=RichMenuBounds(x=W * 2, y=H, width=834, height=843),
        action=MessageAction(label="ติดต่อ", text="ช่วยเหลือ"),
    ),
]


def setup_rich_menu(line_bot_api: MessagingApi, blob_api: MessagingApiBlob = None):
    """สร้าง Rich Menu พร้อมรูปพื้นหลัง และตั้งเป็น default"""
    try:
        # ลบ Rich Menu เก่าทั้งหมดก่อน (กันสร้างซ้ำเมื่อเรียกหลายครั้ง)
        try:
            existing = line_bot_api.get_rich_menu_list()
            for rm in existing.richmenus:
                line_bot_api.delete_rich_menu(rich_menu_id=rm.rich_menu_id)
            logger.info(f"ลบ Rich Menu เก่า {len(existing.richmenus)} อัน")
        except Exception as e:
            logger.warning(f"ลบ Rich Menu เก่าไม่สำเร็จ: {e}")

        rich_menu_request = RichMenuRequest(
            size=RichMenuSize(width=2500, height=1686),
            selected=True,
            name="BoonLoop Main Menu",
            chat_bar_text="เมนู BoonLoop",
            areas=RICH_MENU_AREAS,
        )
        rich_menu_id = line_bot_api.create_rich_menu(
            rich_menu_request=rich_menu_request
        ).rich_menu_id

        # อัปโหลดรูปพื้นหลัง — เรียก LINE API ตรงๆ ด้วย requests (SDK มีปัญหากับ bytes)
        img_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "rich_menu_bg.jpg",
        )
        if os.path.exists(img_path):
            token = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")
            with open(img_path, "rb") as f:
                img_bytes = f.read()
            upload_res = requests.post(
                f"https://api-data.line.me/v2/bot/richmenu/{rich_menu_id}/content",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "image/jpeg",
                },
                data=img_bytes,
                timeout=30,
            )
            if upload_res.status_code != 200:
                raise Exception(f"อัปโหลดรูปไม่สำเร็จ ({upload_res.status_code}): {upload_res.text}")
            logger.info("Rich Menu image uploaded")
        else:
            logger.warning(f"Rich Menu image not found at {img_path}")

        line_bot_api.set_default_rich_menu(rich_menu_id)
        logger.info(f"Rich Menu created: {rich_menu_id}")
        return rich_menu_id
    except Exception as e:
        logger.error(f"setup_rich_menu error: {e}")
        raise
