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
import time
from datetime import datetime, timezone

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
HISTORY_FILE = os.path.join(DATA_DIR, "interaction_history.json")


class _FileLock:
    """ล็อกไฟล์แบบง่าย ไม่พึ่งไลบรารีภายนอก ใช้ os.open(..., O_CREAT | O_EXCL) ซึ่ง
    รับประกันความ atomic ทั้งบน Windows และ Linux (สร้างไฟล์ได้สำเร็จแค่ฝั่งเดียวถ้ามีคน
    แย่งกันสร้างพร้อมกัน) กันไม่ให้ 2 request/โปรเซส อ่าน-แก้-เขียนไฟล์ประวัติชนกัน
    (race condition ที่เจอจากการทดสอบยิง request พร้อมกันจริง — ดู reports/sprint2_report.md หัวข้อ 4.1)
    """

    def __init__(self, lock_path: str, timeout: float = 5.0, poll_interval: float = 0.02):
        self.lock_path = lock_path
        self.timeout = timeout
        self.poll_interval = poll_interval
        self._fd = None

    def __enter__(self):
        start = time.monotonic()
        while True:
            try:
                self._fd = os.open(self.lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                return self
            except FileExistsError:
                if time.monotonic() - start > self.timeout:
                    # กันเดดล็อกค้างถาวรถ้าไฟล์ล็อกเหลือจากโปรเซสที่ถูกปิดกะทันหัน (crash/kill)
                    try:
                        os.remove(self.lock_path)
                    except OSError:
                        pass
                    continue
                time.sleep(self.poll_interval)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._fd is not None:
            os.close(self._fd)
        try:
            os.remove(self.lock_path)
        except OSError:
            pass


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
    """บันทึก list ประวัติการโต้ตอบทั้งหมดลงไฟล์ JSON แบบ atomic (เขียนลงไฟล์ชั่วคราวก่อน
    แล้วค่อยเปลี่ยนชื่อทับไฟล์จริงด้วย os.replace ซึ่งเป็น atomic operation ทั้งบน Windows/Linux)
    กันไฟล์เพี้ยนครึ่งๆกลางๆถ้าโดนขัดจังหวะระหว่างเขียน (เทียบกับของเดิมที่เขียนทับไฟล์จริงตรงๆ)"""
    os.makedirs(DATA_DIR, exist_ok=True)
    tmp_path = HISTORY_FILE + ".tmp"
    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, HISTORY_FILE)
    except OSError as exc:
        print(f"[warn] บันทึกไฟล์ประวัติไม่สำเร็จ: {exc}")
        try:
            os.remove(tmp_path)
        except OSError:
            pass


def add_entry(source: str, kind: str, content: str) -> dict:
    """เพิ่มรายการใหม่ต่อท้ายประวัติ พร้อม timestamp ปัจจุบัน (UTC) แล้วบันทึกลงไฟล์ทันที

    ใช้ file lock (_FileLock) ครอบทั้งขั้นตอนอ่าน-แก้-เขียน (read-modify-write) กันไม่ให้
    2 request ที่เข้ามาพร้อมกันจริง (เช่น กด Interact รัวๆ) อ่าน-เขียนไฟล์ชนกันจนข้อมูลหาย/ไฟล์เพี้ยน
    """
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source": source,
        "kind": kind,
        "content": content,
    }
    os.makedirs(DATA_DIR, exist_ok=True)
    lock_path = HISTORY_FILE + ".lock"
    with _FileLock(lock_path):
        history = load_history()
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
