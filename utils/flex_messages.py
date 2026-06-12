import json
from linebot.v3.messaging import FlexMessage, FlexContainer


def _flex(alt_text: str, contents: dict) -> FlexMessage:
    return FlexMessage(
        alt_text=alt_text,
        contents=FlexContainer.from_dict(contents),
    )


def build_welcome_flex(display_name: str, member_id: str) -> FlexMessage:
    contents = {
        "type": "bubble",
        "header": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {"type": "text", "text": "🌿 BoonLoop", "weight": "bold", "size": "xl", "color": "#2E7D32"},
                {"type": "text", "text": "Smart Circular Merit Platform", "size": "sm", "color": "#666666"},
            ],
            "backgroundColor": "#E8F5E9",
            "paddingAll": "16px",
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "spacing": "md",
            "contents": [
                {"type": "text", "text": f"ยินดีต้อนรับ {display_name}! 🙏", "weight": "bold", "size": "lg", "wrap": True},
                {"type": "text", "text": f"รหัสสมาชิก: {member_id}", "size": "sm", "color": "#888888"},
                {"type": "separator"},
                {"type": "text", "text": "คุณได้รับ 50 คะแนนบุญเริ่มต้น 🏆", "size": "sm", "color": "#2E7D32", "weight": "bold"},
                {"type": "text", "text": "ร่วมสร้างบุญรักษ์โลกไปด้วยกัน 🌍", "size": "sm", "wrap": True, "color": "#555555"},
            ],
        },
        "footer": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "button",
                    "action": {"type": "message", "label": "🌿 เริ่มทำบุญ", "text": "ทำบุญ"},
                    "style": "primary",
                    "color": "#2E7D32",
                }
            ],
        },
    }
    return _flex(f"ยินดีต้อนรับ {display_name}", contents)


def build_booking_menu_flex() -> FlexMessage:
    contents = {
        "type": "bubble",
        "header": {
            "type": "box",
            "layout": "vertical",
            "backgroundColor": "#E8F5E9",
            "paddingAll": "12px",
            "contents": [
                {"type": "text", "text": "🌿 เลือกชุดบุญ", "weight": "bold", "size": "lg", "color": "#2E7D32"},
            ],
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "spacing": "sm",
            "contents": [
                {
                    "type": "button",
                    "action": {"type": "message", "label": "🕯️ ชุดบุญเข้าพรรษา", "text": "ชุดบุญเข้าพรรษา"},
                    "style": "primary",
                    "color": "#FF8F00",
                    "margin": "sm",
                },
                {
                    "type": "button",
                    "action": {"type": "message", "label": "🙏 ชุดไหว้ครูรักษ์โลก", "text": "ชุดไหว้ครู"},
                    "style": "primary",
                    "color": "#1565C0",
                    "margin": "sm",
                },
                {
                    "type": "button",
                    "action": {"type": "message", "label": "🎋 ชุดบุญเทศกาลต่างๆ", "text": "ชุดบุญเทศกาล"},
                    "style": "primary",
                    "color": "#6A1B9A",
                    "margin": "sm",
                },
            ],
        },
    }
    return _flex("เลือกชุดบุญ BoonLoop", contents)


def build_points_flex(summary: dict) -> FlexMessage:
    boon = summary.get("boon_points", 0)
    eco = summary.get("eco_score", 0)
    bookings = summary.get("total_bookings", 0)

    contents = {
        "type": "bubble",
        "header": {
            "type": "box",
            "layout": "vertical",
            "backgroundColor": "#FFF8E1",
            "paddingAll": "12px",
            "contents": [
                {"type": "text", "text": "🏆 คะแนนบุญของคุณ", "weight": "bold", "size": "lg", "color": "#F57F17"},
            ],
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "spacing": "md",
            "contents": [
                {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                        {"type": "text", "text": "คะแนนบุญ", "flex": 2, "size": "sm", "color": "#888888"},
                        {"type": "text", "text": f"{boon} คะแนน", "flex": 3, "weight": "bold", "color": "#F57F17"},
                    ],
                },
                {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                        {"type": "text", "text": "Eco Score", "flex": 2, "size": "sm", "color": "#888888"},
                        {"type": "text", "text": f"{eco} คะแนน", "flex": 3, "weight": "bold", "color": "#2E7D32"},
                    ],
                },
                {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                        {"type": "text", "text": "ร่วมกิจกรรม", "flex": 2, "size": "sm", "color": "#888888"},
                        {"type": "text", "text": f"{bookings} ครั้ง", "flex": 3, "weight": "bold", "color": "#1565C0"},
                    ],
                },
                {"type": "separator"},
                {"type": "text", "text": "200 คะแนน = ชุดบุญฟรี 1 ชุด 🎁", "size": "xs", "color": "#888888", "wrap": True},
            ],
        },
        "footer": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "button",
                    "action": {"type": "message", "label": "🎁 แลกรางวัล", "text": "แลกรางวัล"},
                    "style": "secondary",
                }
            ],
        },
    }
    return _flex("คะแนนบุญ BoonLoop", contents)


def build_project_info_flex() -> FlexMessage:
    contents = {
        "type": "bubble",
        "header": {
            "type": "box",
            "layout": "vertical",
            "backgroundColor": "#E3F2FD",
            "paddingAll": "12px",
            "contents": [
                {"type": "text", "text": "🛕 BoonLoop โครงการ", "weight": "bold", "size": "lg", "color": "#1565C0"},
            ],
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "spacing": "sm",
            "contents": [
                {"type": "text", "text": "Smart Circular Merit Platform", "weight": "bold", "size": "md", "wrap": True},
                {"type": "separator"},
                {"type": "text", "text": "🌿 ลดขยะจากพิธีกรรม", "size": "sm"},
                {"type": "text", "text": "♻️ วัสดุหมุนเวียนรักษ์โลก", "size": "sm"},
                {"type": "text", "text": "🤝 เชื่อมชุมชน วัด ศาลเจ้า", "size": "sm"},
                {"type": "text", "text": "📊 ติดตาม Eco Impact", "size": "sm"},
                {"type": "separator"},
                {"type": "text", "text": "ร่วมสร้างบุญรักษ์โลกไปด้วยกัน 🙏", "size": "sm", "color": "#2E7D32", "wrap": True},
            ],
        },
    }
    return _flex("BoonLoop โครงการ", contents)


def build_return_equipment_flex() -> FlexMessage:
    contents = {
        "type": "bubble",
        "header": {
            "type": "box",
            "layout": "vertical",
            "backgroundColor": "#E8F5E9",
            "paddingAll": "12px",
            "contents": [
                {"type": "text", "text": "♻️ คืนอุปกรณ์", "weight": "bold", "size": "lg", "color": "#2E7D32"},
            ],
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "spacing": "sm",
            "contents": [
                {"type": "text", "text": "เลือกการดำเนินการ", "size": "md", "weight": "bold"},
                {"type": "text", "text": "การคืนอุปกรณ์ได้รับ 30 คะแนนบุญ 🏆", "size": "sm", "color": "#2E7D32", "wrap": True},
            ],
        },
        "footer": {
            "type": "box",
            "layout": "vertical",
            "spacing": "sm",
            "contents": [
                {
                    "type": "button",
                    "action": {"type": "message", "label": "✅ คืนอุปกรณ์", "text": "ยืนยันคืนอุปกรณ์"},
                    "style": "primary",
                    "color": "#2E7D32",
                },
                {
                    "type": "button",
                    "action": {"type": "message", "label": "🎁 บริจาคให้โครงการ", "text": "บริจาคอุปกรณ์"},
                    "style": "secondary",
                },
            ],
        },
    }
    return _flex("คืนอุปกรณ์ BoonLoop", contents)


def build_help_flex() -> FlexMessage:
    contents = {
        "type": "bubble",
        "header": {
            "type": "box",
            "layout": "vertical",
            "backgroundColor": "#F3E5F5",
            "paddingAll": "12px",
            "contents": [
                {"type": "text", "text": "💬 วิธีใช้งาน BoonLoop", "weight": "bold", "size": "lg", "color": "#6A1B9A"},
            ],
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "spacing": "sm",
            "contents": [
                {"type": "text", "text": "พิมพ์คำเหล่านี้ได้เลย:", "weight": "bold", "size": "sm"},
                {"type": "text", "text": "🌿 'ทำบุญ' — จองชุดบุญ", "size": "sm"},
                {"type": "text", "text": "🏆 'คะแนน' — ดูคะแนนบุญ", "size": "sm"},
                {"type": "text", "text": "♻️ 'ผลกระทบ' — Eco Dashboard", "size": "sm"},
                {"type": "text", "text": "🛕 'โครงการ' — ข่าวสาร", "size": "sm"},
                {"type": "text", "text": "🎁 'แลกรางวัล' — Reward Center", "size": "sm"},
                {"type": "text", "text": "♻️ 'คืนอุปกรณ์' — คืนชุด", "size": "sm"},
            ],
        },
    }
    return _flex("วิธีใช้งาน BoonLoop", contents)
