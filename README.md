# 🌿 BoonLoop — Smart Circular Merit Platform

LINE OA Bot สำหรับจัดการชุดบุญและชุดไหว้ครูแบบรักษ์โลก

---

## 📁 โครงสร้างโปรเจกต์

```
boonloop/
├── app.py                  # Entry point (Flask + Webhook)
├── requirements.txt
├── Procfile                # Railway deploy
├── .env.example
├── config/
│   └── constants.py        # ค่าคงที่, ชุดบุญ, คะแนน
├── handlers/
│   ├── follow_handler.py   # จัดการ Follow event
│   └── message_handler.py  # จัดการ Text message + routing
├── services/
│   ├── sheets_service.py   # Google Sheets via Web App URL
│   └── rich_menu_service.py
└── utils/
    └── flex_messages.py    # Flex Message templates
```

---

## ⚙️ ขั้นตอนติดตั้ง

### Railway Environment Variables
```
LINE_CHANNEL_ACCESS_TOKEN=xxxx
LINE_CHANNEL_SECRET=xxxx
SHEETS_WEBAPP_URL=https://script.google.com/macros/s/AKfycbxlEf9TdN0qPD_L8z-O-IMaT8BPPNJhbuZRGx0ktUFtZkdBZicFIYLGWJfEeLSWBdlc/exec
```

### Webhook URL ใน LINE Developers
```
https://your-app.railway.app/webhook
```

---

## 🤖 คำสั่งที่รองรับ (Phase 1)

| คำสั่ง | ฟังก์ชัน |
|--------|---------|
| ทำบุญ / จองชุด | เมนูเลือกชุดบุญ |
| คะแนน / บุญ | ดูคะแนนบุญ + Eco Score |
| ผลกระทบ / eco | Eco Dashboard |
| โครงการ / ข่าวสาร | ข้อมูลโครงการ |
| คืนอุปกรณ์ | คืน/บริจาคอุปกรณ์ |
| แลกรางวัล | Reward Center |
| สมัคร / ลงทะเบียน | ตรวจสอบสมาชิก |

**Follow OA** → สมัครสมาชิกอัตโนมัติ + รับ 50 คะแนน

---

## 🚀 Roadmap

- **Phase 1** ✅ Webhook + สมาชิก + Rich Menu + Google Sheets
- **Phase 2** 🔜 ระบบจอง Step-by-step + QR Payment
- **Phase 3** 🔜 Eco Dashboard Infographic + Admin Panel
