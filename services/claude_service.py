import os
import json
import base64
import logging
import requests

logger = logging.getLogger(__name__)

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"
MODEL = "claude-haiku-4-5-20251001"

SLIP_PROMPT = """คุณคือระบบอ่านสลิปโอนเงินของไทย ดูรูปสลิปนี้แล้วดึงข้อมูลออกมา
ตอบกลับเป็น JSON เท่านั้น ห้ามมีข้อความอื่น รูปแบบ:
{
  "amount": ตัวเลขยอดเงิน (number, ไม่มีคอมมา),
  "date_time": "วันเวลาที่โอน (string)",
  "receiver": "ชื่อผู้รับ (string)",
  "ref": "เลขอ้างอิง/รหัสรายการ (string ถ้ามี)",
  "is_slip": true/false (เป็นสลิปโอนเงินจริงไหม)
}
ถ้าอ่านยอดไม่ได้ ให้ amount เป็น 0"""


def read_slip(image_bytes: bytes, media_type: str = "image/jpeg") -> dict:
    """ส่งรูปสลิปให้ Claude อ่าน คืน dict ข้อมูลสลิป"""
    if not ANTHROPIC_API_KEY:
        raise ValueError("ANTHROPIC_API_KEY not set")

    b64 = base64.standard_b64encode(image_bytes).decode("utf-8")

    payload = {
        "model": MODEL,
        "max_tokens": 512,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {"type": "base64", "media_type": media_type, "data": b64},
                    },
                    {"type": "text", "text": SLIP_PROMPT},
                ],
            }
        ],
    }
    headers = {
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }

    try:
        res = requests.post(ANTHROPIC_URL, json=payload, headers=headers, timeout=30)
        res.raise_for_status()
        data = res.json()
        text = "".join(b.get("text", "") for b in data.get("content", []) if b.get("type") == "text")
        text = text.strip().replace("```json", "").replace("```", "").strip()
        return json.loads(text)
    except Exception as e:
        logger.error(f"read_slip error: {e}")
        return {"amount": 0, "is_slip": False, "error": str(e)}
