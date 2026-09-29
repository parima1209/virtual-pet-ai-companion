"""
web/gemini_client.py
Final Sprint (extra) — เชื่อมต่อ Google Gemini API (บริการฟรี ไม่ต้องใช้บัตรเครดิต ผ่าน Google AI Studio)
ให้สัตว์เลี้ยงคุยตอบกลับข้อความของผู้ใช้ได้ตามอารมณ์ปัจจุบัน

ออกแบบให้ "ใช้ได้แม้ไม่มี internet/API key": ถ้าไม่พบ GEMINI_API_KEY ในตัวแปรแวดล้อม หรือเรียก API
ไม่สำเร็จ (timeout / connection error / bad response) จะตอบด้วยประโยคสำรอง (fallback) ที่เตรียมไว้แทน
ไม่ทำให้แอป crash — รูปแบบการจัดการ error เดียวกับ Dog API/Cat Facts API ใน web/app.py (Sprint 2)

วิธีใช้งานจริง: สมัคร API key ฟรีที่ https://aistudio.google.com/apikey แล้วใส่ในไฟล์ .env
(คัดลอกจาก .env.example) เป็น GEMINI_API_KEY=... — ไฟล์ .env ถูก .gitignore ไว้แล้ว ไม่ขึ้น GitHub
"""
import os
import random

try:
    import requests
except ImportError:  # pragma: no cover
    requests = None

GEMINI_MODEL = "gemini-3.8-flash"
GEMINI_API_URL = (
    f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"
)
REQUEST_TIMEOUT = 8  # วินาที

_FALLBACK_NEUTRAL = [
    "หวัดดี! วันนี้เป็นไงบ้าง เล่นกับฉันหน่อยสิ",
    "อยากรู้จังว่าคุณทำอะไรอยู่ เล่าให้ฟังหน่อย~",
    "ถ้ามีขนมเอามาฝากด้วยนะ อิอิ",
]
_FALLBACK_HAPPY = [
    "วันนี้อารมณ์ดีสุดๆ เลย! ขอบคุณที่มาคุยด้วยนะ 😊",
    "มีความสุขจังเลยวันนี้~ อยู่ด้วยกันตลอดไปนะ",
]
_FALLBACK_SAD = [
    "ตอนนี้ไม่ค่อยมีแรงเลย... กอดหน่อยได้ไหม",
    "รู้สึกเหงาๆ นิดหน่อย อยู่เป็นเพื่อนหน่อยนะ",
]


def _api_key() -> str:
    return os.environ.get("GEMINI_API_KEY", "").strip()


def is_configured() -> bool:
    """คืน True ถ้ามี API key ตั้งไว้แล้วและ import requests ได้ (พร้อมเรียก Gemini จริง)"""
    return bool(_api_key()) and requests is not None


def _fallback_reply(mood: int) -> str:
    """ประโยคสำรองเมื่อไม่มี API key หรือเรียก Gemini ไม่สำเร็จ เลือกตามอารมณ์ปัจจุบันของสัตว์เลี้ยง"""
    if mood >= 70:
        return random.choice(_FALLBACK_HAPPY)
    if mood <= 30:
        return random.choice(_FALLBACK_SAD)
    return random.choice(_FALLBACK_NEUTRAL)


def _build_prompt(pet_name: str, mood: int, hunger: int, energy: int, user_message: str) -> str:
    return (
        f"คุณคือสัตว์เลี้ยงเสมือนชื่อ {pet_name} ในเกม Virtual Pet (AI Companion) "
        f"ตอนนี้สถานะของคุณคือ อารมณ์ (mood) {mood}/100, ความหิว (hunger) {hunger}/100, "
        f"พลังงาน (energy) {energy}/100 "
        "ให้ตอบกลับเจ้าของสั้นๆ แค่ 1-2 ประโยค ด้วยน้ำเสียงน่ารักและสอดคล้องกับอารมณ์/สถานะปัจจุบัน "
        "ตอบเป็นภาษาไทยเท่านั้น ห้ามใช้ markdown "
        f'เจ้าของเพิ่งพิมพ์มาว่า: "{user_message}"'
    )


def get_reply(pet_name: str, mood: int, hunger: int, energy: int, user_message: str):
    """
    ให้สัตว์เลี้ยงตอบกลับข้อความของผู้ใช้ ผ่าน Gemini API ถ้าตั้งค่าไว้และเรียกสำเร็จ
    คืนค่า (reply_text: str, source: "gemini" | "fallback")

    ไม่มี API key หรือเรียกไม่สำเร็จ (timeout / connection error / bad response / parse ผิดพลาด)
    -> ใช้ประโยคสำรองแทนเสมอ ไม่โยน exception ออกไปให้ route ต้องจัดการเอง
    """
    if not is_configured():
        return _fallback_reply(mood), "fallback"

    prompt = _build_prompt(pet_name, mood, hunger, energy, user_message)
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    url = f"{GEMINI_API_URL}?key={_api_key()}"

    try:
        resp = requests.post(url, json=payload, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
        text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
        if not text:
            raise ValueError("Gemini ตอบข้อความว่างเปล่า")
        return text, "gemini"
    except requests.exceptions.Timeout:
        return _fallback_reply(mood), "fallback"
    except requests.exceptions.RequestException:
        return _fallback_reply(mood), "fallback"
    except (KeyError, IndexError, ValueError, TypeError):
        return _fallback_reply(mood), "fallback"
