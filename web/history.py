"""
web/history.py
"ประวัติการโต้ตอบ" (Interaction History) — Data Access Layer + Algorithm Layer สำหรับ Sprint 2

ทุกครั้งที่ผู้ใช้กด "Interact" บนหน้าเว็บ จะมีการบันทึกผลลัพธ์ (timestamp, แหล่งที่มา,
ประเภท, เนื้อหา) ต่อท้ายไฟล์ data/interaction_history.json เป็น list
โมดูลนี้ยังมีฟังก์ชัน search / filter / sort ตามขอบเขตของ Sprint 2 (Rubric หมวด
"การประมวลผลข้อมูลและ Logic")
"""
import json
import os
from datetime import datetime, timezone

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
HISTORY_FILE = os.path.join(DATA_DIR, "interaction_history.json")


def load_history() -> list:
    """โหลดประวัติการโต้ตอบจากไฟล์ JSON ถ้าไม่มีไฟล์หรือไฟล์เสีย คืนค่า list ว่าง (ไม่ crash)"""
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                return data
        except (json.JSONDecodeError, OSError) as exc:
            print(f"[warn] อ่านไฟล์ประวัติไม่สำเร็จ ({exc}) จะเริ่มประวัติใหม่")
    return []


def save_history(history: list) -> None:
    """บันทึก list ประวัติการโต้ตอบทั้งหมดลงไฟล์ JSON"""
    os.makedirs(DATA_DIR, exist_ok=True)
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    except OSError as exc:
        print(f"[warn] บันทึกไฟล์ประวัติไม่สำเร็จ: {exc}")


def add_entry(source: str, kind: str, content: str) -> dict:
    """เพิ่มรายการใหม่ต่อท้ายประวัติ พร้อม timestamp ปัจจุบัน (UTC) แล้วบันทึกลงไฟล์ทันที"""
    history = load_history()
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source": source,
        "kind": kind,
        "content": content,
    }
    history.append(entry)
    save_history(history)
    return entry


def search_history(history: list, query: str) -> list:
    """ค้นหา (Searching): คืนเฉพาะรายการที่มีคำค้นอยู่ในเนื้อหา (content) ไม่สนตัวพิมพ์เล็ก-ใหญ่"""
    if not query:
        return list(history)
    q = query.strip().lower()
    return [item for item in history if q in str(item.get("content", "")).lower()]


def filter_history(history: list, source: str = None, kind: str = None) -> list:
    """กรองข้อมูล (Filtering): กรองตามแหล่งที่มา (source) และ/หรือประเภท (kind)"""
    result = list(history)
    if source:
        result = [item for item in result if str(item.get("source", "")).lower() == source.lower()]
    if kind:
        result = [item for item in result if str(item.get("kind", "")).lower() == kind.lower()]
    return result


def sort_history(history: list, order: str = "desc") -> list:
    """เรียงลำดับข้อมูล (Sorting) ตามเวลา — 'desc' (ค่าเริ่มต้น) = ใหม่→เก่า, 'asc' = เก่า→ใหม่"""
    reverse = str(order).strip().lower() != "asc"
    return sorted(history, key=lambda item: item.get("timestamp", ""), reverse=reverse)
