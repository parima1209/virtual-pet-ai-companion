# แบบรายงานผลการดำเนินงาน Sprint 2

- **ชื่อโปรเจกต์:** Virtual Pet (AI Companion)
- **สัปดาห์ที่:** 2 (Sprint 2: Back-End App Dev)
- **สมาชิกในทีม:**
  - Team Leader: ยีนส์
  - Planner: อาอิง
  - Coder: แคร์
  - Debugger / QA: ปริม

## 1. สรุปความก้าวหน้าของงาน (Sprint Progress Summary)
- [x] เชื่อมต่อ Dog API และ Cat Facts API ผ่าน `requests` แบบสุ่มเลือกเมื่อกด "Interact" (ทำไว้ล่วงหน้าตอน pivot)
- [x] จัดการ Exception ครบทุกกรณี: timeout, connection error, bad response, payload ผิดรูปแบบ
- [x] บันทึก/โหลดสถานะ Pet เป็นไฟล์ JSON (`data/pet_state.json`) พร้อม fallback เมื่อไฟล์เสีย/ไม่มี
- [x] สร้างโมดูลใหม่ `web/history.py` — Data Access Layer สำหรับ "ประวัติการโต้ตอบ"
      (บันทึกทุกครั้งที่ Interact สำเร็จลง `data/interaction_history.json`)
- [x] เขียนฟังก์ชัน **Searching** (`search_history`) — ค้นคำในเนื้อหาแบบไม่สนตัวพิมพ์เล็ก-ใหญ่
- [x] เขียนฟังก์ชัน **Filtering** (`filter_history`) — กรองตามแหล่งที่มา (source) และ/หรือประเภท (kind)
- [x] เขียนฟังก์ชัน **Sorting** (`sort_history`) — เรียงตามเวลา ทั้งทิศทาง desc (ใหม่→เก่า) และ asc (เก่า→ใหม่)
- [x] เปิด endpoint `/api/history` ให้เรียกดูผลลัพธ์ search/filter/sort ผ่าน query string (`q`, `source`, `kind`, `order`)
- [x] เพิ่ม UI "📜 ประวัติการโต้ตอบ" ในหน้าเว็บ — ช่องค้นหา, ตัวกรอง 2 ตัว, ตัวเลือกเรียงลำดับ อัปเดตผลแบบเรียลไทม์
- [x] เขียน unit test แบบ **mock** การเรียก API (`tests/test_web_app.py`) ครอบคลุมทั้งกรณีสำเร็จและ error
      (timeout, connection error, bad payload) โดยไม่ต้องพึ่งอินเทอร์เน็ตจริงตอนรัน test
- [x] เขียน unit test สำหรับ `web/history.py` ครบทุกฟังก์ชัน (`tests/test_history.py`)
- [x] ทดสอบเรียก API จริงบนเครื่องที่มีอินเทอร์เน็ต (นอก sandbox พัฒนา) — **ทำแล้ว ผ่านทุกกรณี**
      ได้รูปสุนัขจริงจาก Dog API และ cat fact จริงจาก Cat Facts API แสดงผลถูกต้อง

## 2. ผลการทดสอบระบบ (Quality Assurance & Debugging Report)

### 2.1 Unit Tests (`pytest`)
รันคำสั่ง `pytest -v` — ผลลัพธ์: **31 passed in 0.20s** (เพิ่มจาก 7 ใน Sprint 1 เป็น 31)

| กลุ่มไฟล์ทดสอบ | จำนวนเทส | ครอบคลุม |
|---|---|---|
| `tests/test_pet.py` | 7 | คลาส `Pet` (Sprint 1 เดิม) |
| `tests/test_web_app.py` | 10 | logic เลือกสไปรต์ + `/api/interact` แบบ mock API (สำเร็จ/timeout/connection error/bad payload) + `/api/history` |
| `tests/test_history.py` | 13 | `load_history`, `save_history`, `add_entry`, `search_history`, `filter_history`, `sort_history` |

### 2.2 Manual / Edge Case Testing (Observation / Expected / Actual)

| รายการทดสอบ | อินพุตที่ใช้ | ผลลัพธ์ที่คาดหวัง (Expected) | ผลการทดสอบจริง (Actual) | สถานะ |
|---|---|---|---|---|
| ค้นหาประวัติแบบสด (ผ่านหน้าเว็บ) | พิมพ์ "sleep" ในช่องค้นหา | รายการที่ไม่มีคำนี้ในเนื้อหาต้องหายไปทันที | เหลือแค่ 1 รายการที่มีคำว่า "sleep" ในเนื้อหา | PASSED |
| กรองตามแหล่งที่มา | เลือก "Dog API" ใน dropdown | เห็นเฉพาะรายการจาก Dog API | ผลลัพธ์ถูกต้องตามที่กรอง | PASSED |
| เรียงลำดับ | สลับ "ใหม่→เก่า" / "เก่า→ใหม่" | ลำดับรายการสลับทิศทางตาม timestamp | ลำดับถูกต้องทั้ง 2 ทิศทาง | PASSED |
| ไฟล์ประวัติเสีย/ไม่มี | ลบ/ทำให้ `interaction_history.json` เสีย | ระบบสร้างประวัติเปล่าใหม่ ไม่ crash | คืนค่า `[]` ตามที่ออกแบบ | PASSED |
| เรียก API จริงใน sandbox พัฒนา | กด Interact ในสภาพแวดล้อมพัฒนา (ไม่มีอินเทอร์เน็ตออกนอก) | ต้องไม่ crash แสดงข้อความ error สุภาพแทน | ได้ error 502/504 พร้อมข้อความภาษาไทยที่เข้าใจง่าย ระบบไม่ล่ม | PASSED (ยืนยันว่า error handling ทำงานถูกต้อง) |
| เรียก API จริงบนเครื่องจริงที่มีอินเทอร์เน็ต | กด Interact หลายครั้งบนเครื่องของทีม (นอก sandbox) | ต้องได้รูปสุนัข/cat fact จริงจาก API และบันทึกลงประวัติถูกต้อง | ได้รูปสุนัขจริงและ cat fact จริงสลับกันตามที่ออกแบบ ประวัติบันทึกครบทุกครั้ง | PASSED |

## 3. สรุปบทเรียนประจำสัปดาห์ (Retrospective: Wow! & Whoops!)
- **Wow!** (ส่วนที่ทำได้ดี): แยก `web/history.py` เป็นโมดูลเดี่ยวจาก `web/app.py` ทำให้ทดสอบฟังก์ชัน
  search/filter/sort ได้ตรงๆ โดยไม่ต้องพึ่ง Flask test client เลย (unit test เร็วและอ่านง่าย);
  ออกแบบ endpoint `/api/history` ให้รับ query string ทำให้ทั้ง search, filter, sort ทำงานร่วมกันได้ในคำขอเดียว
  โดยไม่ต้องเขียน endpoint แยกสามตัว
- **Whoops!** (ปัญหาที่พบและแนวทางแก้ไข): สภาพแวดล้อมที่ใช้พัฒนา (sandbox) บล็อคการเชื่อมต่อออกไปยัง
  dog.ceo/catfact.ninja โดยตรง ทำให้ทดสอบ "เรียก API จริงสำเร็จ" แบบ end-to-end ไม่ได้ในเครื่องพัฒนา —
  แก้ปัญหาด้วยการเขียน unit test แบบ mock (`unittest.mock`) แทน ซึ่งครอบคลุม logic การจัดการ error ได้ครบ
  จากนั้นทีมได้ทดสอบยิง API จริงอีกครั้งบนเครื่องที่มีอินเทอร์เน็ตปกติแล้ว ผลผ่านทุกกรณี ปิด Sprint นี้ได้เต็มรูปแบบ
- **ลิงก์ Repository / Pull Request:** https://github.com/parima1209/virtual-pet-ai-companion

## 4. สิ่งที่ต้องทำต่อก่อนส่งงาน Sprint 2 (25/9/69)
- [x] ทดสอบกด Interact บนเครื่องจริงที่มีอินเทอร์เน็ต ยืนยันว่าได้รูปสุนัข/ข้อความแมวจริงและประวัติถูกบันทึก
- [ ] Push โค้ดชุดนี้ขึ้น GitHub (`web/history.py`, เทสใหม่, PLAN.md/README.md ที่อัปเดต, ไฟล์นี้)
- [ ] (ถ้ามีเวลา) ทดสอบเพิ่มเติม: กด Interact รัวๆ หลายครั้งติดกัน แล้วเช็คว่าประวัติไม่ตกหล่น/ไม่ซ้ำ
