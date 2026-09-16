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

from flask import Flask, jsonify, render_template, request

# ทำให้ import "src.pet" ได้ไม่ว่าจะรันจากที่ไหน
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.pet import Pet  # noqa: E402
import history  # noqa: E402

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


# ---------------------------------------------------------------------------
# Data Access Layer: บันทึก / โหลดสถานะ Pet จากไฟล์ JSON
# ---------------------------------------------------------------------------
def load_pet() -> Pet:
    """โหลดสถานะ Pet จากไฟล์ JSON ถ้ามี มิฉะนั้นสร้างตัวใหม่"""
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            return Pet(
                name=data.get("name", "Buddy"),
                hunger=data.get("hunger", 50),
                mood=data.get("mood", 50),
                energy=data.get("energy", 100),
            )
        except (json.JSONDecodeError, OSError) as exc:
            print(f"[warn] อ่านไฟล์สถานะไม่สำเร็จ ({exc}) จะสร้างสัตว์เลี้ยงใหม่")
    return Pet(name="Buddy")


def save_pet(pet: Pet) -> None:
    """บันทึกสถานะ Pet ปัจจุบันลงไฟล์ JSON"""
    os.makedirs(DATA_DIR, exist_ok=True)
    try:
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(pet.to_dict(), f, ensure_ascii=False, indent=2)
    except OSError as exc:
        print(f"[warn] บันทึกไฟล์สถานะไม่สำเร็จ: {exc}")


pet = load_pet()


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
    return {
        "name": pet.name,
        "hunger": pet.hunger,
        "mood": pet.mood,
        "energy": pet.energy,
        "sprite": sprite_for(pet),
        "message": message,
    }


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    return render_template("index.html", pet_name=pet.name)


@app.route("/api/state")
def api_state():
    return jsonify(state_payload())


@app.route("/api/action", methods=["POST"])
def api_action():
    data = request.get_json(silent=True) or {}
    action = str(data.get("action", "")).strip().lower()

    if action == "feed":
        message = pet.feed()
    elif action == "play":
        message = pet.play()
    elif action == "rest":
        message = pet.rest()
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


if __name__ == "__main__":
    app.run(debug=True, port=5000)
