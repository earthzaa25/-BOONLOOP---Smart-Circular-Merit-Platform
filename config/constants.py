# ชุดบุญที่มีให้เลือก
MERIT_PACKAGES = {
    "khao_phansa": {
        "name": "ชุดบุญเข้าพรรษา",
        "emoji": "🕯️",
        "items": {
            "1": {"name": "ชุดรักษ์โลก", "price": 99, "eco_score": 10},
            "2": {"name": "ชุดรักษ์ชุมชน", "price": 119, "eco_score": 15},
            "3": {"name": "ชุดรักษ์โลกยั่งยืน", "price": 149, "eco_score": 20},
        },
    },
    "wai_kru": {
        "name": "ชุดไหว้ครูรักษ์โลก",
        "emoji": "🙏",
        "items": {
            "1": {"name": "ชุดศรัทธาไหว้ครู", "price": 10, "eco_score": 5},
            "2": {"name": "ชุดกตัญญูไหว้ครู", "price": 20, "eco_score": 8},
            "3": {"name": "ชุดปัญญาไหว้ครู", "price": 30, "eco_score": 12},
        },
    },
}

# คะแนนบุญที่ได้รับจากแต่ละกิจกรรม
BOON_POINTS = {
    "register": 50,
    "booking": 20,
    "return_equipment": 30,
    "join_event": 15,
    "invite_member": 25,
}

# Keyword สำหรับ Rich Menu
KEYWORDS = {
    "ทำบุญ": "MENU_BOOKING",
    "จองชุด": "MENU_BOOKING",
    "eco": "MENU_ECO",
    "ผลกระทบ": "MENU_ECO",
    "dashboard": "MENU_ECO",
    "คะแนน": "MENU_POINTS",
    "บุญ": "MENU_POINTS",
    "โครงการ": "MENU_PROJECT",
    "ข่าวสาร": "MENU_PROJECT",
    "แลก": "MENU_REWARD",
    "รางวัล": "MENU_REWARD",
    "คืน": "MENU_RETURN",
    "อุปกรณ์": "MENU_RETURN",
    "สมัคร": "REGISTER",
    "ลงทะเบียน": "REGISTER",
    "สวัสดี": "GREETING",
    "help": "HELP",
    "ช่วย": "HELP",
    "เมนู": "HELP",
}

# Google Sheets — ชื่อ sheet tabs
SHEET_MEMBERS = "Members"
SHEET_BOOKINGS = "Bookings"
SHEET_POINTS = "Points"
