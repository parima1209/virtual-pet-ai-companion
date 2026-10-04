"""
web/app.py
Flask web front-end (Pixel Art) สำหรับ Virtual Pet (AI Companion)

โครงสร้าง:
- ใช้คลาส Pet เดิมจาก src/pet.py เป็น Business Logic Layer (ไม่แก้ไขไฟล์เดิม)
- เพิ่ม Data Access Layer: บันทึก/โหลดสถานะสัตว์เลี้ยงเป็นไฟล์ JSON (data/pet_state.json)
- เพิ่ม Data API Integration: เรียก Dog API / Cat Facts API แบบสุ่มในปุ่ม "Interact"
- Sprint 2: บันทึก "ประวัติการโต้ตอบ" ทุกครั้งที่ Interact สำเร็จ (web/history.py) และเปิด endpoint
  /api/history ให้ search / filter / sort ประวัตินั้นได้

วิธีรัน (จาก root โปรเจค):
    pip install -r requirements.txt
    python web/app.py
แล้วเปิดเบราว์เซอร์ที่ http://127.0.0.1:5000
"""

import json
import os
import random
import sys
from datetime import datetime, timezone

from flask import Flask, jsonify, render_template, request

try:
    from dotenv import load_dotenv
    load_dotenv()  # โหลดไฟล์ .env (ถ้ามี) เพื่ออ่าน GEMINI_API_KEY -- ไม่มีไฟล์/แพ็กเกจก็ไม่ error
except ImportError:  # pragma: no cover
    pass

# ทำให้ import "src.pet" ได้ไม่ว่าจะรันจากที่ไหน
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.pet import Pet  # noqa: E402
import history  # noqa: E402
import advisor  # noqa: E402
import gemini_client  # noqa: E402

try:
    import requests
except ImportError:  # pragma: no cover
    requests = None

app = Flask(__name__)

DATA_DIR = os.path.join(PROJECT_ROOT, "data")
STATE_FILE = os.path.join(DATA_DIR, "pet_state.json")

DOG_API_URL = "https://dog.ceo/api/breeds/image/random"
CAT_FACT_URL = "https://catfact.ninja/fact"
REQUEST_TIMEOUT = 5  # วินาที

MAX_NAME_LENGTH = 20  # ความยาวชื่อสัตว์เลี้ยงสูงสุดตอนเปลี่ยนชื่อ


# ---------------------------------------------------------------------------
# Data Access Layer: บันทึก / โหลดสถานะ Pet จากไฟล์ JSON
# ---------------------------------------------------------------------------
def _parse_iso(value):
    """แปลง ISO timestamp string เป็น datetime (UTC) ถ้าแปลงไม่ได้คืนค่า None"""
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed
    except (ValueError, TypeError):
        return None


def load_pet():
    """โหลดสถานะ Pet + เวลาที่บันทึกล่าสุด (last_updated) จากไฟล์ JSON ถ้ามี มิฉะนั้นสร้างตัวใหม่
    ผลข้างเคียง (side effect): ตั้งค่า global cleanliness / growth_points / birth_time ตามไฟล์ด้วย"""
    global cleanliness, growth_points, birth_time
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            loaded_pet = Pet(
                name=data.get("name", "Buddy"),
                hunger=data.get("hunger", 50),
                mood=data.get("mood", 50),
                energy=data.get("energy", 100),
            )
            cleanliness = _clamp01(data.get("cleanliness", 100))
            growth_points = float(data.get("growth_points", 0.0))
            birth_time = _parse_iso(data.get("birth_time")) or _parse_iso(data.get("last_updated"))
            return loaded_pet, _parse_iso(data.get("last_updated"))
        except (json.JSONDecodeError, OSError) as exc:
            print(f"[warn] อ่านไฟล์สถานะไม่สำเร็จ ({exc}) จะสร้างสัตว์เลี้ยงใหม่")
    cleanliness = 100
    growth_points = 0.0
    birth_time = None
    return Pet(name="Buddy"), None


def save_pet(pet: Pet, when: datetime = None) -> None:
    """บันทึกสถานะ Pet ปัจจุบัน + เวลาที่บันทึก (last_updated) ลงไฟล์ JSON
    รวมถึงฟิลด์เพิ่มเติมที่ไม่ได้อยู่ใน Pet เดิม (cleanliness / growth_points / birth_time)"""
    os.makedirs(DATA_DIR, exist_ok=True)
    data = pet.to_dict()
    now = when or datetime.now(timezone.utc)
    data["last_updated"] = now.isoformat(timespec="seconds")
    data["cleanliness"] = cleanliness
    data["growth_points"] = growth_points
    data["birth_time"] = (birth_time or now).isoformat(timespec="seconds")
    # เขียนลงไฟล์ชั่วคราวก่อนแล้วค่อย os.replace (atomic) กันไฟล์พังครึ่งๆ กลางๆ
    # ถ้า request มาพร้อมกันหรือโปรแกรมดับระหว่างเขียน
    tmp_path = f"{STATE_FILE}.{os.getpid()}.tmp"
    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, STATE_FILE)
    except OSError as exc:
        print(f"[warn] บันทึกไฟล์สถานะไม่สำเร็จ: {exc}")
        try:
            os.remove(tmp_path)
        except OSError:
            pass


# ---------------------------------------------------------------------------
# Sprint 3 — Neglect: ถ้าปล่อยสัตว์เลี้ยงไว้นาน (เวลาจริงผ่านไป) hunger เพิ่ม/energy ลดลงเอง
# ---------------------------------------------------------------------------
DECAY_HUNGER_PER_MIN = 2 / 5    # หิวขึ้น 1 หน่วย ทุกๆ 2.5 นาที (เร็วขึ้น 2 เท่า เห็นผลชัดขึ้น)
DECAY_ENERGY_PER_MIN = 1 / 10   # พลังงานลด 1 หน่วย ทุกๆ 10 นาทีจริงที่ถูกปล่อยไว้
MAX_DECAY_MINUTES = 24 * 60     # จำกัดเพดานไว้ที่ 24 ชม. กันค่าพังถ้าปล่อยไว้เป็นวันๆ

# ---------------------------------------------------------------------------
# Final Sprint (extra) — ความสะอาด: ต้องอาบน้ำ ไม่งั้นจะสกปรกและอารมณ์เสีย
# ---------------------------------------------------------------------------
DECAY_CLEAN_PER_MIN = 1 / 8   # ความสะอาดลดลง 1 หน่วย ทุกๆ 8 นาทีจริงที่ถูกปล่อยไว้
PLAY_DIRTIES_BY = 10          # เล่นแต่ละครั้งทำให้สกปรกขึ้น 10 หน่วย
BATHE_CLEAN_AMOUNT = 40       # อาบน้ำแต่ละครั้งเพิ่มความสะอาด 40 หน่วย
DIRTY_THRESHOLD = 30          # ต่ำกว่านี้ถือว่า "สกปรก" (ขึ้นฝุ่นในหน้าเว็บ + อารมณ์เสียเล็กน้อย)

# ---------------------------------------------------------------------------
# Final Sprint (extra) — กลางวัน/กลางคืน: ใช้เวลาจริงของเครื่อง (ตามเขตเวลาของเครื่อง)
# ---------------------------------------------------------------------------
NIGHT_START_HOUR = 20   # 20:00 เป็นต้นไปถือว่าเป็นกลางคืน
NIGHT_END_HOUR = 6      # ก่อน 06:00 ยังถือว่าเป็นกลางคืน

# ---------------------------------------------------------------------------
# Final Sprint (extra) — โตขึ้นตามเวลา: ลูกสัตว์ -> วัยรุ่น -> โตเต็มวัย
# ยิ่งดูแลดี (หิวน้อย อารมณ์ดี พลังงานเต็ม สะอาด) ยิ่งโตไว (แต่ไม่หยุดโตแม้ดูแลไม่ดี แค่ช้าลง)
# ---------------------------------------------------------------------------
GROWTH_PER_MINUTE_BASE = 1.0
GROWTH_QUALITY_MIN_MULT = 0.5   # ดูแลแย่สุด -> โตช้าลงครึ่งหนึ่ง (ไม่หยุดโตสนิท)
GROWTH_QUALITY_MAX_MULT = 1.5   # ดูแลดีสุด -> โตเร็วขึ้น 1.5 เท่า
MAX_GROWTH_MINUTES = 60 * 24 * 30  # จำกัดเพดานต่อครั้งไว้ที่ 30 วัน กันค่าพังถ้าปล่อยไฟล์ไว้นานมาก
STAGE_TEEN_POINTS = 60 * 24 * 2    # ประมาณ 2 วัน (ถ้าดูแลระดับกลางๆ)
STAGE_ADULT_POINTS = 60 * 24 * 5   # ประมาณ 5 วัน

_STAGE_LABEL = {
    "baby": "ลูกสัตว์ 🐣",
    "teen": "วัยรุ่น 🐥",
    "adult": "โตเต็มวัย 🐓",
}


def _clamp01(value: int) -> int:
    return max(0, min(100, value))


def is_night_time(now: datetime = None) -> bool:
    """คืน True ถ้าเวลาปัจจุบัน (ตามเขตเวลาท้องถิ่นของเครื่อง) อยู่ในช่วงกลางคืน 20:00-06:00"""
    now = now or datetime.now(timezone.utc)
    local_hour = now.astimezone().hour
    return local_hour >= NIGHT_START_HOUR or local_hour < NIGHT_END_HOUR


def care_quality() -> float:
    """คะแนนคุณภาพการดูแล 0.0-1.0 (หิวน้อย + อารมณ์ดี + พลังงานเต็ม + สะอาด) ใช้เร่ง/ชะลอการเติบโต"""
    return (
        (100 - pet.hunger) / 100
        + pet.mood / 100
        + pet.energy / 100
        + cleanliness / 100
    ) / 4


def life_stage_for(points: float) -> str:
    """แปลงแต้มการเติบโตสะสมเป็นวัย: baby -> teen -> adult"""
    if points < STAGE_TEEN_POINTS:
        return "baby"
    if points < STAGE_ADULT_POINTS:
        return "teen"
    return "adult"


def growth_progress(points: float) -> dict:
    """ความคืบหน้าไปสู่วัยถัดไป (ใช้แสดงแถบ + ตัวเลขบนหน้าเว็บ)
    คืน start/target = แต้มเริ่ม/แต้มเป้าหมายของวัยปัจจุบัน, percent = 0-100,
    next_label = ชื่อวัยถัดไป (None เมื่อโตเต็มวัยแล้ว)"""
    stage = life_stage_for(points)
    if stage == "baby":
        start, target, next_stage = 0, STAGE_TEEN_POINTS, "teen"
    elif stage == "teen":
        start, target, next_stage = STAGE_TEEN_POINTS, STAGE_ADULT_POINTS, "adult"
    else:
        return {"start": STAGE_ADULT_POINTS, "target": None,
                "percent": 100, "next_label": None}
    percent = (points - start) / (target - start) * 100
    return {"start": start, "target": target,
            "percent": round(max(0.0, min(100.0, percent)), 1),
            "next_label": _STAGE_LABEL[next_stage]}


def apply_growth(elapsed_minutes: float) -> None:
    """สะสมแต้มการเติบโตตามเวลาจริงที่ผ่านไป คูณด้วยคุณภาพการดูแล (ยิ่งดูแลดียิ่งโตไว)"""
    global growth_points
    elapsed_minutes = max(0.0, min(elapsed_minutes, MAX_GROWTH_MINUTES))
    if elapsed_minutes <= 0:
        return
    quality = care_quality()
    mult = GROWTH_QUALITY_MIN_MULT + quality * (GROWTH_QUALITY_MAX_MULT - GROWTH_QUALITY_MIN_MULT)
    growth_points += elapsed_minutes * GROWTH_PER_MINUTE_BASE * mult


# เศษของหน่วยที่ยังไม่ครบ 1 หน่วย (เช่น energy ลดทีละ 1 ทุก 10 นาที) ต้องสะสมต่อข้ามคำขอ
# ไม่งั้นการเปิด/รีเฟรช/กดปุ่มถี่กว่ารอบการลดจะปัดเศษทิ้งทุกครั้งจน energy ไม่ลดเลย (บั๊กที่เจอ 4/10/69)
# เศษใช้ได้เฉพาะเมื่อ "anchor" ตรงกับ last_updated ปัจจุบัน — ถ้าแก้เวลาในไฟล์/รีสตาร์ต เศษเก่าจะถูกทิ้ง
_decay_carry = {"anchor": None, "hunger": 0.0, "energy": 0.0, "clean": 0.0}


def _split_whole(total: float):
    """แยกค่าที่สะสมได้เป็น (จำนวนเต็มที่ใช้ได้เลย, เศษที่เก็บไว้ต่อ) — บวก 1e-9 กัน floating-point
    ปัดผิด เช่น 0.9999999999 ที่จริงควรเป็น 1"""
    whole = int(total + 1e-9)
    return whole, max(0.0, total - whole)


def apply_neglect_decay(now: datetime = None) -> None:
    """คำนวณเวลาจริงที่ผ่านไปตั้งแต่บันทึกครั้งล่าสุด แล้วปรับ hunger/energy/mood/cleanliness ตามนั้น
    รวมถึงสะสมแต้มการเติบโต (growth_points) ตามเวลาที่ผ่านไปจริง"""
    global last_updated, cleanliness, birth_time
    now = now or datetime.now(timezone.utc)
    if last_updated is None:
        last_updated = now
        if birth_time is None:
            birth_time = now
        return

    elapsed_minutes_real = max(0.0, (now - last_updated).total_seconds() / 60)
    elapsed_minutes = min(elapsed_minutes_real, MAX_DECAY_MINUTES)

    if _decay_carry["anchor"] == last_updated:
        carry = _decay_carry
    else:
        carry = {"hunger": 0.0, "energy": 0.0, "clean": 0.0}
    hunger_up, carry_hunger = _split_whole(elapsed_minutes * DECAY_HUNGER_PER_MIN + carry["hunger"])
    energy_down, carry_energy = _split_whole(elapsed_minutes * DECAY_ENERGY_PER_MIN + carry["energy"])
    clean_down, carry_clean = _split_whole(elapsed_minutes * DECAY_CLEAN_PER_MIN + carry["clean"])

    if hunger_up or energy_down:
        pet.hunger = _clamp01(pet.hunger + hunger_up)
        pet.energy = _clamp01(pet.energy - energy_down)
        if pet.hunger >= 90 or pet.energy <= 10:
            pet.mood = _clamp01(pet.mood - 5)

    if clean_down:
        cleanliness = _clamp01(cleanliness - clean_down)
        if cleanliness < DIRTY_THRESHOLD:
            pet.mood = _clamp01(pet.mood - 3)

    if birth_time is None:
        birth_time = now
    apply_growth(elapsed_minutes_real)

    last_updated = now
    _decay_carry.update(anchor=now, hunger=carry_hunger, energy=carry_energy, clean=carry_clean)
    if hunger_up or energy_down or clean_down:
        save_pet(pet, when=now)


def neglect_warning():
    """คืนข้อความเตือนถ้าสัตว์เลี้ยงถูกปล่อยไว้จนหิวมาก/พลังงานหมด มิฉะนั้นคืน None"""
    msgs = []
    if pet.hunger >= 90:
        msgs.append(f"{pet.name} หิวมากแล้ว! รีบให้อาหารเร็วๆ นี้นะ")
    if pet.energy <= 10:
        msgs.append(f"{pet.name} หมดแรงมากแล้ว ให้พักผ่อนหน่อยนะ")
    return " ".join(msgs) if msgs else None


def dirty_warning():
    """คืนข้อความเตือนถ้าสัตว์เลี้ยงสกปรกเกินไป มิฉะนั้นคืน None"""
    if cleanliness < DIRTY_THRESHOLD:
        return f"{pet.name} ตัวสกปรกมากแล้ว รีบพาไปอาบน้ำหน่อยนะ"
    return None


cleanliness = 100      # 0-100 ยิ่งเยอะยิ่งสะอาด (ตั้งต้นไว้ก่อน load_pet() จะโหลดค่าจริงทับให้)
growth_points = 0.0    # แต้มการเติบโตสะสม (ใช้คำนวณวัย baby/teen/adult)
birth_time = None      # เวลาที่เริ่มเลี้ยง (ใช้เป็น baseline การเติบโต)

pet, last_updated = load_pet()


# ---------------------------------------------------------------------------
# ตัดสินใจว่าจะใช้สไปรต์ Pixel Art หน้าไหนตามสถานะปัจจุบัน
# ---------------------------------------------------------------------------
def sprite_for(p: Pet) -> str:
    if p.hunger >= 70:
        return "hungry"
    if p.energy <= 20:
        return "sleepy"
    if p.mood >= 70:
        return "happy"
    return "idle"


def state_payload(message: str = "") -> dict:
    warning = neglect_warning()
    stage = life_stage_for(growth_points)
    return {
        "name": pet.name,
        "hunger": pet.hunger,
        "mood": pet.mood,
        "energy": pet.energy,
        "sprite": sprite_for(pet),
        "message": message,
        "neglected": warning is not None,
        "warning": warning,
        "cleanliness": cleanliness,
        "dirty": cleanliness < DIRTY_THRESHOLD,
        "dirty_warning": dirty_warning(),
        "is_night": is_night_time(),
        "life_stage": stage,
        "life_stage_label": _STAGE_LABEL[stage],
        "growth_points": round(growth_points, 1),
        "growth_progress": growth_progress(growth_points),
    }


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    return render_template("index.html", pet_name=pet.name)


@app.route("/api/state")
def api_state():
    apply_neglect_decay()
    return jsonify(state_payload())


@app.route("/api/action", methods=["POST"])
def api_action():
    global cleanliness
    apply_neglect_decay()
    data = request.get_json(silent=True) or {}
    action = str(data.get("action", "")).strip().lower()

    if action == "feed":
        message = pet.feed()
    elif action == "play":
        mood_before = pet.mood
        message = pet.play()
        cleanliness = _clamp01(cleanliness - PLAY_DIRTIES_BY)  # เล่นแล้วตัวจะสกปรกขึ้นนิดหน่อย
        if is_night_time():
            # กลางคืน: ปลุกมาเล่นแล้วง่วง ได้ mood เพิ่มขึ้นแค่ครึ่งเดียวของปกติ
            mood_gain = pet.mood - mood_before
            if mood_gain > 0:
                pet.mood = _clamp01(mood_before + mood_gain // 2)
            message += f" (แต่ดึกแล้วนะ {pet.name} เลยง่วงๆ ไม่ค่อยอินเท่าไหร่)"
    elif action == "rest":
        message = pet.rest()
    elif action == "bathe":
        cleanliness = _clamp01(cleanliness + BATHE_CLEAN_AMOUNT)
        pet.mood = _clamp01(pet.mood + 5)
        message = f"{pet.name} อาบน้ำจนตัวสะอาดสดชื่น! (cleanliness: {cleanliness})"
    else:
        return jsonify({"error": f"ไม่รู้จักคำสั่ง '{action}'"}), 400

    save_pet(pet)
    return jsonify(state_payload(message))


@app.route("/api/interact")
def api_interact():
    """
    ดึง "การโต้ตอบ" แบบสุ่มจาก Dog API หรือ Cat Facts API (Data API Integration)
    ครอบคลุม: GET request, error handling (timeout / connection error / bad status),
    และ JSON parsing
    """
    apply_neglect_decay()
    if requests is None:
        return jsonify({"error": "ไม่พบไลบรารี requests บนเซิร์ฟเวอร์"}), 500

    use_dog = random.choice([True, False])
    api_name = "Dog API" if use_dog else "Cat Facts API"

    try:
        if use_dog:
            resp = requests.get(DOG_API_URL, timeout=REQUEST_TIMEOUT)
            resp.raise_for_status()
            payload = resp.json()
            if payload.get("status") != "success":
                raise ValueError("Dog API ตอบกลับสถานะไม่สำเร็จ")
            content = {"kind": "image", "url": payload["message"]}
            flavor_text = f"{pet.name} ได้เจอเพื่อนใหม่จาก {api_name}!"
        else:
            resp = requests.get(CAT_FACT_URL, timeout=REQUEST_TIMEOUT)
            resp.raise_for_status()
            payload = resp.json()
            fact = payload.get("fact")
            if not fact:
                raise ValueError("Cat Facts API ไม่มีข้อมูล fact กลับมา")
            content = {"kind": "fact", "text": fact}
            flavor_text = f"{pet.name} เล่าเรื่องจาก {api_name} ให้ฟัง!"
    except requests.exceptions.Timeout:
        app.logger.warning("%s timeout", api_name)
        return jsonify({"error": f"เชื่อมต่อ {api_name} หมดเวลา (timeout) ลองใหม่อีกครั้งนะ"}), 504
    except requests.exceptions.RequestException as exc:
        app.logger.warning("%s request failed: %s", api_name, exc)
        msg = f"เชื่อมต่อ {api_name} ไม่สำเร็จ ลองใหม่อีกครั้งนะ (เช็คอินเทอร์เน็ตด้วย)"
        return jsonify({"error": msg}), 502
    except (ValueError, KeyError) as exc:
        app.logger.warning("%s bad payload: %s", api_name, exc)
        msg = f"ข้อมูลจาก {api_name} ไม่ถูกต้อง ลองใหม่อีกครั้งนะ"
        return jsonify({"error": msg}), 502

    # การโต้ตอบสำเร็จ -> ให้รางวัลเล็กน้อยแก่สัตว์เลี้ยง
    pet.mood = min(100, pet.mood + 8)
    save_pet(pet)

    # Sprint 2: บันทึกผลลัพธ์นี้ลง "ประวัติการโต้ตอบ" เพื่อให้ search/filter/sort ได้ทีหลัง
    content_text = content.get("url") or content.get("text") or ""
    history.add_entry(source=api_name, kind=content["kind"], content=content_text)

    result = state_payload(flavor_text)
    result["interaction"] = content
    result["source"] = api_name
    return jsonify(result)


@app.route("/api/advice")
def api_advice():
    """
    Final Sprint — "AI Advisor" (rule-based): คืนคำแนะนำ/ทำนายอารมณ์สัตว์เลี้ยง
    วิเคราะห์จากสถานะปัจจุบันของ pet และความถี่การ Interact ใน 30 นาทีล่าสุด (web/advisor.py)
    """
    apply_neglect_decay()
    items = history.load_history()
    return jsonify(advisor.generate_advice(pet, items))


@app.route("/api/history")
def api_history():
    """
    Sprint 2 — ค้นหา (Searching) / กรอง (Filtering) / เรียงลำดับ (Sorting) ประวัติการโต้ตอบ
    Query params:
      q      = คำค้นหา (ค้นในเนื้อหา content)
      source = กรองตามแหล่งที่มา เช่น "Dog API" หรือ "Cat Facts API"
      kind   = กรองตามประเภท "image" หรือ "fact"
      order  = "desc" (ใหม่->เก่า, ค่าเริ่มต้น) หรือ "asc" (เก่า->ใหม่)
    """
    query = request.args.get("q", "").strip()
    source = request.args.get("source", "").strip()
    kind = request.args.get("kind", "").strip()
    order = request.args.get("order", "desc").strip()

    items = history.load_history()
    items = history.search_history(items, query)
    items = history.filter_history(items, source=source or None, kind=kind or None)
    items = history.sort_history(items, order=order)

    return jsonify({"count": len(items), "results": items})


@app.route("/api/rename", methods=["POST"])
def api_rename():
    """Final Sprint (extra) — เปลี่ยนชื่อสัตว์เลี้ยง (ตั้งชื่อได้) แล้วบันทึกถาวรลง JSON"""
    apply_neglect_decay()
    data = request.get_json(silent=True) or {}
    new_name = str(data.get("name", "")).strip()

    if not new_name:
        return jsonify({"error": "กรุณาใส่ชื่อใหม่"}), 400
    if len(new_name) > MAX_NAME_LENGTH:
        return jsonify({"error": f"ชื่อยาวเกินไป (ไม่เกิน {MAX_NAME_LENGTH} ตัวอักษร)"}), 400

    pet.name = new_name
    save_pet(pet)
    return jsonify(state_payload(f"เปลี่ยนชื่อเป็น {pet.name} แล้ว!"))


@app.route("/api/chat", methods=["POST"])
def api_chat():
    """
    Final Sprint (extra) — คุยกับสัตว์เลี้ยงได้ (ผ่าน Gemini API ถ้าตั้งค่า GEMINI_API_KEY ไว้)
    ไม่มี API key หรือเรียกไม่สำเร็จ -> ตอบด้วยประโยคสำรอง (web/gemini_client.py) ไม่ crash แอป
    """
    apply_neglect_decay()
    data = request.get_json(silent=True) or {}
    user_message = str(data.get("message", "")).strip()

    if not user_message:
        return jsonify({"error": "พิมพ์อะไรสักหน่อยสิ"}), 400
    if len(user_message) > 300:
        return jsonify({"error": "ข้อความยาวเกินไป (ไม่เกิน 300 ตัวอักษร)"}), 400

    reply, source = gemini_client.get_reply(
        pet.name, pet.mood, pet.hunger, pet.energy, user_message
    )
    return jsonify({"reply": reply, "source": source})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
