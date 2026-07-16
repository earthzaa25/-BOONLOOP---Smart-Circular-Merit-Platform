from datetime import datetime, timedelta
from linebot.v3.messaging import FlexMessage, FlexContainer

# LINE จำกัดความยาว label ของปุ่มไว้ที่ 40 ตัวอักษร
# ถ้าเกิน LINE จะปฏิเสธทั้งข้อความ (ผู้ใช้จะไม่เห็นอะไรเลย)
LABEL_MAX = 40


def _fit(text, limit=LABEL_MAX):
    """ตัดข้อความให้พอดีกับลิมิตของ LINE"""
    text = str(text or "")
    if len(text) <= limit:
        return text
    return text[: limit - 1] + "…"


def _flex(alt_text, contents):
    return FlexMessage(alt_text=alt_text, contents=FlexContainer.from_dict(contents))


def _pb(label, step, value, color="#2E7D32"):
    """สร้างปุ่ม postback"""
    return {
        "type": "button",
        "action": {
            "type": "postback",
            "label": _fit(label),
            "data": f"action=booking&step={step}&value={value}",
            "displayText": _fit(label, 300),
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


# วนสีปุ่มให้ดูมีชีวิตชีวา
_PALETTE = ["#FF8F00", "#1565C0", "#6A1B9A", "#2E7D32", "#C62828", "#00838F"]


# ─── Step 1: ประเภทชุด (จาก Sheet) ─────────────
def build_package_type_flex(packages):
    buttons = []
    for i, cat in enumerate(packages):
        label = f"{cat.get('emoji', '')} {cat.get('name', '')}".strip()
        buttons.append(_pb(label, "type", cat["category"], _PALETTE[i % len(_PALETTE)]))
    buttons.append(_cancel_button())
    contents = {
        "type": "bubble",
        "header": _header("เลือกประเภทชุดบุญ", 1, "#2E7D32"),
        "body": {"type": "box", "layout": "vertical", "spacing": "sm", "contents": buttons},
    }
    return _flex("เลือกประเภทชุดบุญ", contents)


# ─── Step 2: เลือกชุด (จาก Sheet, ใช้ index) ────
def build_package_items_flex(cat):
    """การ์ดเลื่อน — แต่ละชุดแสดงรายละเอียดครบ (รูป/ของในชุด/Eco Score)"""
    bubbles = []
    for idx, item in enumerate(cat["items"][:11]):  # LINE จำกัด 12 การ์ด เผื่อการ์ดยกเลิก 1
        bubbles.append(_package_bubble(cat, item, idx))
    bubbles.append(_cancel_bubble())
    return _flex("เลือกชุดบุญ", {"type": "carousel", "contents": bubbles})


def _package_bubble(cat, item, idx):
    body = [
        {"type": "text", "text": _fit(item["name"], 60), "weight": "bold", "size": "lg", "wrap": True, "color": "#1B5E20"},
        {
            "type": "box", "layout": "baseline", "margin": "xs",
            "contents": [
                {"type": "text", "text": f"{item['price']}", "size": "xxl", "weight": "bold", "color": "#C8862C", "flex": 0},
                {"type": "text", "text": " บาท", "size": "sm", "color": "#888888", "flex": 0, "margin": "xs"},
            ],
        },
    ]

    # คำอธิบายสั้น
    desc = (item.get("description") or "").strip()
    if desc:
        body.append({"type": "separator", "margin": "md"})
        body.append({"type": "text", "text": _fit(desc, 120), "size": "xs", "color": "#666666",
                     "wrap": True, "margin": "md"})

    # รายการของในชุด (คั่นด้วย |)
    raw = (item.get("items_list") or "").strip()
    parts = [p.strip() for p in raw.split("|") if p.strip()]
    if parts:
        body.append({"type": "separator", "margin": "md"})
        body.append({"type": "text", "text": "ในชุดประกอบด้วย", "size": "xs",
                     "weight": "bold", "color": "#2E7D32", "margin": "md"})
        for p in parts[:6]:
            body.append({
                "type": "box", "layout": "baseline", "spacing": "sm", "margin": "xs",
                "contents": [
                    {"type": "text", "text": "•", "size": "xs", "color": "#2E7D32", "flex": 0},
                    {"type": "text", "text": _fit(p, 40), "size": "xs", "color": "#555555", "wrap": True},
                ],
            })
        if len(parts) > 6:
            body.append({"type": "text", "text": f"และอีก {len(parts) - 6} รายการ",
                         "size": "xxs", "color": "#AAAAAA", "margin": "xs"})

    # Eco Score
    body.append({"type": "separator", "margin": "md"})
    body.append({
        "type": "box", "layout": "baseline", "margin": "md",
        "contents": [
            {"type": "text", "text": "♻️", "size": "sm", "flex": 0},
            {"type": "text", "text": f" Eco Score {item.get('eco_score', 0)}",
             "size": "xs", "color": "#2E7D32", "weight": "bold"},
        ],
    })

    bubble = {
        "type": "bubble",
        "size": "kilo",
        "body": {"type": "box", "layout": "vertical", "spacing": "none", "contents": body},
        "footer": {
            "type": "box", "layout": "vertical",
            "contents": [{
                "type": "button", "style": "primary", "color": "#2E7D32", "height": "sm",
                "action": {
                    "type": "postback",
                    "label": "เลือกชุดนี้",
                    "data": f"action=booking&step=item&value={idx}",
                    "displayText": _fit(f"เลือก {item['name']}", 300),
                },
            }],
        },
    }

    # ใส่รูปถ้ามี (ต้องเป็น https)
    img = (item.get("image_url") or "").strip()
    if img.startswith("https://"):
        bubble["hero"] = {
            "type": "image", "url": img, "size": "full",
            "aspectRatio": "20:13", "aspectMode": "cover",
        }
    return bubble


def _cancel_bubble():
    return {
        "type": "bubble",
        "size": "kilo",
        "body": {
            "type": "box", "layout": "vertical", "spacing": "md",
            "justifyContent": "center",
            "contents": [
                {"type": "text", "text": "🙏", "size": "xxl", "align": "center"},
                {"type": "text", "text": "ยังไม่เลือกตอนนี้", "size": "sm",
                 "color": "#888888", "align": "center", "wrap": True},
            ],
        },
        "footer": {
            "type": "box", "layout": "vertical",
            "contents": [{
                "type": "button", "style": "secondary", "height": "sm",
                "action": {
                    "type": "postback", "label": "❌ ยกเลิก",
                    "data": "action=booking&step=cancel&value=cancel",
                    "displayText": "ยกเลิกการจอง",
                },
            }],
        },
    }


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


# ─── Step 6: รูปแบบพิธี (จาก Sheet) ────────────
def build_ceremony_flex(ceremonies):
    buttons = []
    icons = ["🙏", "🤝", "📿", "🏮"]
    colors = ["#C62828", "#AD1457", "#6A1B9A", "#00838F"]
    for idx, c in enumerate(ceremonies):
        buttons.append(_pb(f"{icons[idx % len(icons)]} {c}", "ceremony", str(idx), colors[idx % len(colors)]))
    buttons.append(_cancel_button())
    contents = {
        "type": "bubble",
        "header": _header("เลือกรูปแบบการร่วมพิธี", 6, "#C62828"),
        "body": {"type": "box", "layout": "vertical", "spacing": "sm", "contents": buttons},
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
