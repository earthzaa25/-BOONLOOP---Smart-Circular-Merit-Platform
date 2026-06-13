from datetime import datetime, timedelta
from linebot.v3.messaging import FlexMessage, FlexContainer
from config.constants import MERIT_PACKAGES


def _flex(alt_text, contents):
    return FlexMessage(alt_text=alt_text, contents=FlexContainer.from_dict(contents))


def _pb(label, step, value, color="#2E7D32"):
    """สร้างปุ่ม postback"""
    return {
        "type": "button",
        "action": {
            "type": "postback",
            "label": label,
            "data": f"action=booking&step={step}&value={value}",
            "displayText": label,
        },
        "style": "primary",
        "color": color,
        "margin": "sm",
    }


def _cancel_button():
    return {
        "type": "button",
        "action": {
            "type": "postback",
            "label": "❌ ยกเลิก",
            "data": "action=booking&step=cancel&value=cancel",
            "displayText": "ยกเลิกการจอง",
        },
        "style": "secondary",
        "margin": "sm",
    }


def _header(title, step_no, color):
    return {
        "type": "box",
        "layout": "vertical",
        "backgroundColor": color,
        "paddingAll": "12px",
        "contents": [
            {"type": "text", "text": f"ขั้นตอน {step_no}/7", "size": "xs", "color": "#FFFFFF"},
            {"type": "text", "text": title, "weight": "bold", "size": "lg", "color": "#FFFFFF"},
        ],
    }


# ─── Step 1: ประเภทชุด ─────────────────────────
def build_package_type_flex():
    contents = {
        "type": "bubble",
        "header": _header("เลือกประเภทชุดบุญ", 1, "#2E7D32"),
        "body": {
            "type": "box", "layout": "vertical", "spacing": "sm",
            "contents": [
                _pb("🕯️ ชุดบุญเข้าพรรษา", "type", "khao_phansa", "#FF8F00"),
                _pb("🙏 ชุดไหว้ครูรักษ์โลก", "type", "wai_kru", "#1565C0"),
                _cancel_button(),
            ],
        },
    }
    return _flex("เลือกประเภทชุดบุญ", contents)


# ─── Step 2: เลือกชุด ──────────────────────────
def build_package_items_flex(package_type):
    pkg = MERIT_PACKAGES[package_type]
    buttons = []
    for key, item in pkg["items"].items():
        label = f"{item['name']} - {item['price']} บาท"
        buttons.append(_pb(label, "item", key, "#2E7D32"))
    buttons.append(_cancel_button())
    contents = {
        "type": "bubble",
        "header": _header(f"{pkg['emoji']} {pkg['name']}", 2, "#2E7D32"),
        "body": {"type": "box", "layout": "vertical", "spacing": "sm", "contents": buttons},
    }
    return _flex("เลือกชุดบุญ", contents)


# ─── Step 3: เลือกวันรับ ───────────────────────
def build_date_picker_flex():
    buttons = []
    today = datetime.now()
    for i in range(1, 6):  # 5 วันถัดไป
        d = today + timedelta(days=i)
        thai_date = d.strftime("%d/%m/%Y")
        buttons.append(_pb(f"📅 {thai_date}", "date", thai_date, "#1565C0"))
    buttons.append(_cancel_button())
    contents = {
        "type": "bubble",
        "header": _header("เลือกวันรับชุด", 3, "#1565C0"),
        "body": {"type": "box", "layout": "vertical", "spacing": "sm", "contents": buttons},
    }
    return _flex("เลือกวันรับ", contents)


# ─── Step 4: เลือกสถานที่ ──────────────────────
def build_location_flex(locations):
    buttons = []
    for idx, loc in enumerate(locations):
        buttons.append(_pb(f"📍 {loc}", "location", str(idx), "#6A1B9A"))
    buttons.append(_cancel_button())
    contents = {
        "type": "bubble",
        "header": _header("เลือกสถานที่รับ", 4, "#6A1B9A"),
        "body": {"type": "box", "layout": "vertical", "spacing": "sm", "contents": buttons},
    }
    return _flex("เลือกสถานที่", contents)


# ─── Step 5: เลือกเวลา ─────────────────────────
def build_time_flex(time_slots):
    buttons = []
    for idx, t in enumerate(time_slots):
        buttons.append(_pb(f"🕐 {t}", "time", str(idx), "#00838F"))
    buttons.append(_cancel_button())
    contents = {
        "type": "bubble",
        "header": _header("เลือกเวลารับ", 5, "#00838F"),
        "body": {"type": "box", "layout": "vertical", "spacing": "sm", "contents": buttons},
    }
    return _flex("เลือกเวลา", contents)


# ─── Step 6: รูปแบบพิธี ────────────────────────
def build_ceremony_flex():
    contents = {
        "type": "bubble",
        "header": _header("เลือกรูปแบบการร่วมพิธี", 6, "#C62828"),
        "body": {
            "type": "box", "layout": "vertical", "spacing": "sm",
            "contents": [
                _pb("🙏 เข้าร่วมพิธีด้วยตนเอง", "ceremony", "self", "#C62828"),
                _pb("🤝 มอบหมายให้ชุมชนดำเนินการ", "ceremony", "community", "#AD1457"),
                _cancel_button(),
            ],
        },
    }
    return _flex("รูปแบบพิธี", contents)


# ─── Step 7: ชำระเงิน ──────────────────────────
def build_payment_flex():
    contents = {
        "type": "bubble",
        "header": _header("เลือกวิธีชำระเงิน", 7, "#2E7D32"),
        "body": {
            "type": "box", "layout": "vertical", "spacing": "sm",
            "contents": [
                _pb("📱 QR Payment", "payment", "qr", "#2E7D32"),
                _pb("💸 PromptPay", "payment", "promptpay", "#1565C0"),
                _pb("💵 เงินสด (มัดจำ)", "payment", "cash", "#FF8F00"),
                _cancel_button(),
            ],
        },
    }
    return _flex("ชำระเงิน", contents)


# ─── สรุป + ยืนยัน ─────────────────────────────
def build_confirm_flex(s):
    def row(label, value):
        return {
            "type": "box", "layout": "horizontal",
            "contents": [
                {"type": "text", "text": label, "flex": 2, "size": "sm", "color": "#888888"},
                {"type": "text", "text": str(value), "flex": 3, "size": "sm", "weight": "bold", "wrap": True},
            ],
        }
    contents = {
        "type": "bubble",
        "header": {
            "type": "box", "layout": "vertical", "backgroundColor": "#2E7D32", "paddingAll": "12px",
            "contents": [{"type": "text", "text": "📋 ยืนยันการจอง", "weight": "bold", "size": "lg", "color": "#FFFFFF"}],
        },
        "body": {
            "type": "box", "layout": "vertical", "spacing": "sm",
            "contents": [
                row("ชุดบุญ", s.get("package_name", "-")),
                row("ราคา", f"{s.get('price', 0)} บาท"),
                row("วันรับ", s.get("pickup_date", "-")),
                row("เวลา", s.get("pickup_time", "-")),
                row("สถานที่", s.get("location", "-")),
                row("รูปแบบพิธี", s.get("ceremony_type", "-")),
                row("ชำระเงิน", s.get("payment_method", "-")),
            ],
        },
        "footer": {
            "type": "box", "layout": "vertical", "spacing": "sm",
            "contents": [
                {
                    "type": "button",
                    "action": {"type": "postback", "label": "✅ ยืนยันการจอง",
                               "data": "action=booking&step=confirm&value=yes", "displayText": "ยืนยันการจอง"},
                    "style": "primary", "color": "#2E7D32",
                },
                {
                    "type": "button",
                    "action": {"type": "postback", "label": "❌ ยกเลิก",
                               "data": "action=booking&step=confirm&value=no", "displayText": "ยกเลิก"},
                    "style": "secondary",
                },
            ],
        },
    }
    return _flex("ยืนยันการจอง", contents)


# ─── สำเร็จ ────────────────────────────────────
def build_booking_success_flex(booking_id, s):
    contents = {
        "type": "bubble",
        "header": {
            "type": "box", "layout": "vertical", "backgroundColor": "#2E7D32", "paddingAll": "16px",
            "contents": [
                {"type": "text", "text": "✅ จองสำเร็จ!", "weight": "bold", "size": "xl", "color": "#FFFFFF"},
            ],
        },
        "body": {
            "type": "box", "layout": "vertical", "spacing": "md",
            "contents": [
                {"type": "text", "text": f"รหัสจอง: {booking_id}", "weight": "bold", "size": "md", "color": "#2E7D32"},
                {"type": "separator"},
                {"type": "text", "text": f"🕯️ {s.get('package_name', '')}", "size": "sm", "wrap": True},
                {"type": "text", "text": f"📅 {s.get('pickup_date', '')} {s.get('pickup_time', '')}", "size": "sm"},
                {"type": "text", "text": f"📍 {s.get('location', '')}", "size": "sm", "wrap": True},
                {"type": "separator"},
                {"type": "text", "text": "🏆 ได้รับ 20 คะแนนบุญ!", "size": "sm", "color": "#F57F17", "weight": "bold"},
                {"type": "text", "text": "เราจะแจ้งเตือนก่อนวันรับชุด 🙏", "size": "xs", "color": "#888888", "wrap": True},
            ],
        },
    }
    return _flex(f"จองสำเร็จ {booking_id}", contents)
