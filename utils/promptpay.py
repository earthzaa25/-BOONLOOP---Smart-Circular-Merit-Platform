import os

# เลขพร้อมเพย์ที่รับเงิน (เก็บใน env เพื่อความปลอดภัย)
PROMPTPAY_ID = os.environ.get("PROMPTPAY_ID", "2083479305")


def get_qr_url(amount: float) -> str:
    """สร้าง URL รูป QR PromptPay พร้อมยอดเงิน

    ใช้บริการ promptpay.io (ฟรี) — คืน URL รูปภาพ .png
    ใช้ส่งเป็น ImageMessage ใน LINE ได้เลย
    """
    return f"https://promptpay.io/{PROMPTPAY_ID}/{amount:.2f}.png"
