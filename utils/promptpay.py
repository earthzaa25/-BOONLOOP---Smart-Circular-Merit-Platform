import os

# เลขพร้อมเพย์ (สำหรับสร้าง QR แบบมียอดอัตโนมัติ — ใช้เมื่อไม่มีรูป static)
PROMPTPAY_ID = os.environ.get("PROMPTPAY_ID", "")

# URL รูป QR แบบ static (ถ้าตั้งไว้ จะใช้รูปนี้แทน และลูกค้ากรอกยอดเอง)
PROMPTPAY_QR_URL = os.environ.get("PROMPTPAY_QR_URL", "")


def is_static_qr() -> bool:
    """ใช้รูป QR static หรือไม่"""
    return bool(PROMPTPAY_QR_URL)


def get_static_qr_url() -> str:
    """URL รูป QR static"""
    return PROMPTPAY_QR_URL


def get_qr_url(amount: float) -> str:
    """สร้าง URL รูป QR PromptPay พร้อมยอดเงิน (ผ่าน promptpay.io)
    ใช้ได้เฉพาะเมื่อ PROMPTPAY_ID เป็นเบอร์โทร/เลขบัตรประชาชน
    """
    return f"https://promptpay.io/{PROMPTPAY_ID}/{amount:.2f}.png"
