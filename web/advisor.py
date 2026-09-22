"""
web/advisor.py
Final Sprint — "AI Advisor" (rule-based): วิเคราะห์สถานะปัจจุบันของ Pet + แนวโน้มจากประวัติการโต้ตอบ
แล้วให้คำแนะนำ/ทำนายอารมณ์สัตว์เลี้ยงแบบฉลาดขึ้น

หมายเหตุ: นี่คือ AI/Automation ตามขอบเขตของ Final Sprint ใน PLAN.md ("ทำนายอารมณ์สัตว์เลี้ยงที่ฉลาดขึ้น")
เป็น **rule-based** ล้วน ไม่เชื่อมต่อ AI API ภายนอก (ไม่ต้องพึ่ง API key/อินเทอร์เน็ต ทดสอบได้ deterministic
100%) แต่ใช้หลักการวิเคราะห์แนวโน้มจากข้อมูลจริง (สถานะปัจจุบัน + ความถี่การโต้ตอบล่าสุด) เพื่อให้คำแนะนำ
"""
from datetime import datetime, timedelta, timezone


def wellbeing_score(pet) -> int:
    """คะแนนความเป็นอยู่โดยรวม 0-100: mood มีน้ำหนักมากสุด, ตามด้วยความไม่หิวและพลังงาน"""
    score = pet.mood * 0.5 + (100 - pet.hunger) * 0.3 + pet.energy * 0.2
    return max(0, min(100, round(score)))


def mood_forecast(pet) -> str:
    """ทำนายแนวโน้มอารมณ์สัตว์เลี้ยงแบบ rule-based จากคะแนนความเป็นอยู่โดยรวม"""
    score = wellbeing_score(pet)
    if score >= 75:
        return "แนวโน้มดีมาก"
    if score >= 50:
        return "แนวโน้มปกติ"
    if score >= 25:
        return "แนวโน้มเริ่มแย่ลง"
    return "แนวโน้มวิกฤต"


_ACTION_LABELS = {
    "feed": "🍖 Feed (ให้อาหาร)",
    "play": "🎾 Play (เล่นด้วยกัน)",
    "rest": "💤 Rest (พักผ่อน)",
    "interact": "✨ Interact (โต้ตอบพิเศษ)",
}


def recommend_action(pet) -> str:
    """แนะนำ action ที่ควรทำต่อไป โดยเทียบว่าสถานะไหน 'ต้องการความช่วยเหลือ' มากที่สุด"""
    needs = {
        "feed": pet.hunger,
        "rest": 100 - pet.energy,
        "play": 100 - pet.mood,
    }
    action = max(needs, key=needs.get)
    if needs[action] < 20:
        # ทุกสถานะโอเคดี ไม่มีอะไรต้องรีบ -> แนะนำให้ลองโต้ตอบพิเศษแทน
        return "interact"
    return action


def recent_interaction_count(history_items, minutes: int = 30, now: datetime = None) -> int:
    """นับจำนวนการ Interact ในช่วง `minutes` นาทีล่าสุด จากประวัติที่ส่งมา"""
    if not history_items:
        return 0
    now = now or datetime.now(timezone.utc)
    cutoff = now - timedelta(minutes=minutes)
    count = 0
    for item in history_items:
        ts = item.get("timestamp")
        if not ts:
            continue
        try:
            parsed = datetime.fromisoformat(ts)
        except ValueError:
            continue
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        if parsed >= cutoff:
            count += 1
    return count


def generate_advice(pet, history_items=None, now: datetime = None) -> dict:
    """
    รวมทุกฟังก์ชันข้างบนเป็นคำแนะนำก้อนเดียว สำหรับส่งกลับให้หน้าเว็บแสดงผล

    คืนค่า dict: {score, forecast, recommended_action, recommended_label, headline}
    """
    history_items = history_items or []
    score = wellbeing_score(pet)
    forecast = mood_forecast(pet)
    action = recommend_action(pet)
    recent = recent_interaction_count(history_items, minutes=30, now=now)

    if action == "interact" and recent == 0:
        headline = f"{pet.name} สบายดี แต่ยังไม่ได้เจอเพื่อนใหม่เลยช่วงนี้ ลองกด Interact ดูไหม?"
    elif action == "interact":
        headline = f"{pet.name} สบายดีทุกอย่าง! ({forecast}, คะแนนความเป็นอยู่ {score}/100)"
    else:
        headline = (
            f"{pet.name} {forecast.lower()} (คะแนนความเป็นอยู่ {score}/100) "
            f"แนะนำให้ {_ACTION_LABELS[action]}"
        )

    return {
        "score": score,
        "forecast": forecast,
        "recommended_action": action,
        "recommended_label": _ACTION_LABELS[action],
        "recent_interactions_30min": recent,
        "headline": headline,
    }
