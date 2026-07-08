import time
import logging
from services.sheets_service import _call

logger = logging.getLogger(__name__)

# cache แบบง่าย (ลดการเรียก Sheet ระหว่างจอง)
_cache = {}
_CACHE_TTL = 180  # วินาที (3 นาที) — ชุดบุญ/ตัวเลือกไม่ค่อยเปลี่ยนบ่อย


def _cached(key, fetch_fn):
    now = time.time()
    entry = _cache.get(key)
    if entry and now - entry[0] < _CACHE_TTL:
        return entry[1]
    value = fetch_fn()
    _cache[key] = (now, value)
    return value


def _fetch_packages():
    result = _call({"action": "getPackages"})
    return result.get("data", [])


def _fetch_options():
    result = _call({"action": "getOptions"})
    return result.get("data", {"location": [], "time": [], "ceremony": []})


def get_packages() -> list:
    """คืน list ของ category ที่ active พร้อม items
    [{category, name, emoji, items: [{name, price, eco_score}]}]
    """
    return _cached("packages", _fetch_packages)


def get_options() -> dict:
    """คืน {location: [...], time: [...], ceremony: [...]} เฉพาะ active"""
    return _cached("options", _fetch_options)


def find_category(packages: list, category: str) -> dict | None:
    for c in packages:
        if c["category"] == category:
            return c
    return None


def clear_cache():
    _cache.clear()
