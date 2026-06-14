from linebot.v3.messaging import FlexMessage, FlexContainer


def _flex(alt, contents):
    return FlexMessage(alt_text=alt, contents=FlexContainer.from_dict(contents))


STATUS_TH = {
    "pending": "รอดำเนินการ",
    "confirmed": "ยืนยันแล้ว",
    "completed": "เสร็จสิ้น",
    "cancelled": "ยกเลิกแล้ว",
}
PAY_TH = {
    "pending_payment": "รอชำระเงิน",
    "paid": "ชำระแล้ว",
    "refunded": "คืนเงินแล้ว",
}


# ─── รายการจองของฉัน ───────────────────────────
def build_my_bookings_flex(bookings: list) -> FlexMessage:
    if not bookings:
        contents = {
            "type": "bubble",
            "body": {
                "type": "box", "layout": "vertical", "spacing": "md",
                "contents": [
                    {"type": "text", "text": "📋 การจองของฉัน", "weight": "bold", "size": "lg"},
                    {"type": "text", "text": "ยังไม่มีรายการจอง\nพิมพ์ 'ทำบุญ' เพื่อเริ่มจอง 🌿", "size": "sm", "color": "#888888", "wrap": True},
                ],
            },
        }
        return _flex("การจองของฉัน", contents)

    bubbles = []
    for b in bookings[:10]:
        status = b.get("status", "")
        pay = b.get("payment_status", "")
        can_cancel = status in ("pending",) and pay != "paid"
        body_contents = [
            {"type": "text", "text": b.get("package_name", "-"), "weight": "bold", "size": "md", "wrap": True},
            {"type": "text", "text": f"#{b.get('booking_id','')}", "size": "xs", "color": "#AAAAAA"},
            {"type": "separator", "margin": "sm"},
            _row("วันรับ", f"{b.get('pickup_date','-')} {b.get('pickup_time','')}"),
            _row("สถานที่", b.get("location", "-")),
            _row("ราคา", f"{b.get('price',0)} บาท"),
            _row("สถานะ", STATUS_TH.get(status, status)),
            _row("ชำระเงิน", PAY_TH.get(pay, pay)),
        ]
        footer = None
        if can_cancel:
            footer = {
                "type": "box", "layout": "vertical",
                "contents": [{
                    "type": "button",
                    "action": {"type": "postback", "label": "❌ ยกเลิกการจองนี้",
                               "data": f"action=cancel&value={b.get('booking_id','')}",
                               "displayText": "ยกเลิกการจอง"},
                    "style": "secondary",
                }],
            }
        bubble = {
            "type": "bubble", "size": "kilo",
            "header": {
                "type": "box", "layout": "vertical", "backgroundColor": _status_color(status),
                "paddingAll": "10px",
                "contents": [{"type": "text", "text": STATUS_TH.get(status, status), "color": "#FFFFFF", "weight": "bold", "size": "sm"}],
            },
            "body": {"type": "box", "layout": "vertical", "spacing": "sm", "contents": body_contents},
        }
        if footer:
            bubble["footer"] = footer
        bubbles.append(bubble)

    return _flex("การจองของฉัน", {"type": "carousel", "contents": bubbles})


def _status_color(status):
    return {
        "pending": "#FF8F00", "confirmed": "#1565C0",
        "completed": "#2E7D32", "cancelled": "#9E9E9E",
    }.get(status, "#6B7B6E")


def _row(label, value):
    return {
        "type": "box", "layout": "horizontal",
        "contents": [
            {"type": "text", "text": label, "flex": 2, "size": "xs", "color": "#888888"},
            {"type": "text", "text": str(value), "flex": 3, "size": "xs", "weight": "bold", "wrap": True},
        ],
    }


# ─── คืนอุปกรณ์ — เลือกรายการ ───────────────────
def build_returnable_flex(items: list) -> FlexMessage:
    if not items:
        contents = {
            "type": "bubble",
            "body": {
                "type": "box", "layout": "vertical", "spacing": "md",
                "contents": [
                    {"type": "text", "text": "♻️ คืนอุปกรณ์", "weight": "bold", "size": "lg"},
                    {"type": "text", "text": "ยังไม่มีอุปกรณ์ที่ต้องคืน\n(ต้องเป็นรายการที่ยืนยันแล้ว)", "size": "sm", "color": "#888888", "wrap": True},
                ],
            },
        }
        return _flex("คืนอุปกรณ์", contents)

    bubbles = []
    for b in items[:10]:
        bid = b.get("booking_id", "")
        bubbles.append({
            "type": "bubble", "size": "kilo",
            "header": {
                "type": "box", "layout": "vertical", "backgroundColor": "#2E7D32", "paddingAll": "10px",
                "contents": [{"type": "text", "text": "♻️ คืนอุปกรณ์", "color": "#FFFFFF", "weight": "bold", "size": "sm"}],
            },
            "body": {
                "type": "box", "layout": "vertical", "spacing": "sm",
                "contents": [
                    {"type": "text", "text": b.get("package_name", "-"), "weight": "bold", "wrap": True},
                    {"type": "text", "text": f"#{bid}", "size": "xs", "color": "#AAAAAA"},
                    {"type": "text", "text": "คืนอุปกรณ์ได้รับ 30 คะแนนบุญ 🏆", "size": "xs", "color": "#2E7D32", "wrap": True},
                ],
            },
            "footer": {
                "type": "box", "layout": "vertical", "spacing": "sm",
                "contents": [
                    {"type": "button", "style": "primary", "color": "#2E7D32",
                     "action": {"type": "postback", "label": "✅ คืนอุปกรณ์",
                                "data": f"action=return&value={bid}&donate=0", "displayText": "คืนอุปกรณ์"}},
                    {"type": "button", "style": "secondary",
                     "action": {"type": "postback", "label": "🎁 บริจาคให้โครงการ",
                                "data": f"action=return&value={bid}&donate=1", "displayText": "บริจาคอุปกรณ์"}},
                ],
            },
        })
    return _flex("คืนอุปกรณ์", {"type": "carousel", "contents": bubbles})


# ─── Eco Dashboard ─────────────────────────────
def build_eco_flex(stats: dict) -> FlexMessage:
    def stat_box(label, value, unit, color):
        return {
            "type": "box", "layout": "vertical", "flex": 1,
            "contents": [
                {"type": "text", "text": str(value), "size": "xl", "weight": "bold", "color": color, "align": "center"},
                {"type": "text", "text": unit, "size": "xxs", "color": "#888888", "align": "center"},
                {"type": "text", "text": label, "size": "xxs", "color": "#666666", "align": "center", "wrap": True},
            ],
        }
    contents = {
        "type": "bubble",
        "header": {
            "type": "box", "layout": "vertical",
            "background": {"type": "linearGradient", "angle": "135deg", "startColor": "#1B5E20", "endColor": "#2E7D32"},
            "paddingAll": "16px",
            "contents": [
                {"type": "text", "text": "♻️ Eco Dashboard", "color": "#FFFFFF", "weight": "bold", "size": "lg"},
                {"type": "text", "text": "ผลกระทบเชิงบวกของคุณ 🌍", "color": "#E8F5E9", "size": "xs"},
            ],
        },
        "body": {
            "type": "box", "layout": "vertical", "spacing": "lg",
            "contents": [
                {
                    "type": "box", "layout": "horizontal",
                    "contents": [
                        stat_box("ขยะที่ลดได้", stats.get("waste_reduced", 0), "กก.", "#2E7D32"),
                        stat_box("ลดคาร์บอน", stats.get("co2_reduced", 0), "กก.CO₂", "#1565C0"),
                        stat_box("คะแนนบุญ", stats.get("boon_points", 0), "คะแนน", "#F57F17"),
                    ],
                },
                {"type": "separator"},
                {
                    "type": "box", "layout": "horizontal",
                    "contents": [
                        stat_box("Eco Score", stats.get("eco_score", 0), "คะแนน", "#2E7D32"),
                        stat_box("ร่วมกิจกรรม", stats.get("total_bookings", 0), "ครั้ง", "#6A1B9A"),
                        stat_box("วัสดุหมุนเวียน", stats.get("reused_items", 0), "ชุด", "#00838F"),
                    ],
                },
                {"type": "separator"},
                {"type": "text", "text": "ทุกการทำบุญของคุณช่วยโลกได้จริง 🙏", "size": "xs", "color": "#666666", "align": "center", "wrap": True},
            ],
        },
    }
    return _flex("Eco Dashboard", contents)
