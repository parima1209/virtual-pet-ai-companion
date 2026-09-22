# แบบรายงานผลการดำเนินงาน Sprint 3

- **ชื่อโปรเจกต์:** Virtual Pet (AI Companion)
- **สัปดาห์ที่:** 3 (Sprint 3: Full-Stack App Dev)
- **สมาชิกในทีม:** แคร์, ปริม, อาอิง, ยีนส์ — _(ยังไม่ได้ตกลงหมุนเวียนบทบาทรอบนี้ รอทีมคุยกันแล้วกรอกในตาราง
  "บทบาทในทีม — Sprint 3" ใน `PLAN.md`)_

## 1. สรุปความก้าวหน้าของงาน (Sprint Progress Summary)
- [x] ทุกปุ่ม (Feed / Play / Rest / Interact) เรียก REST API ของ Flask แล้วอัปเดตหน้าจอแบบเรียลไทม์อยู่แล้ว
      ตั้งแต่ Sprint 2 (ยืนยันซ้ำด้วย manual test รอบนี้ — ดูหัวข้อ 2.2)
- [x] สถานะสัตว์เลี้ยงไม่หายเมื่อรีเฟรชหน้า — `/api/state` โหลดจาก `data/pet_state.json` เสมอ (ยืนยันด้วย
      manual test จริง)
- [x] **เพิ่มระบบ Neglect Decay** — ถ้าปล่อยสัตว์เลี้ยงไว้นานโดยไม่กดอะไรเลย hunger จะค่อยๆ เพิ่มขึ้น
      (+1 ทุก 5 นาทีจริง) และ energy จะค่อยๆ ลดลง (-1 ทุก 10 นาทีจริง) โดยอิงเวลาจริงจาก `last_updated`
      ที่บันทึกไว้ใน `data/pet_state.json` — จำกัดเพดานไว้ที่ 24 ชม. กันค่าพังถ้าปล่อยไว้นานเป็นวันๆ
- [x] เพิ่มข้อความ/แบนเนอร์เตือนบนหน้าเว็บเมื่อ hunger ≥ 90 หรือ energy ≤ 10 (`neglected`/`warning`
      ใน response ของ `/api/state`, `/api/action`, `/api/interact`)
- [x] ป้องกันการกดปุ่มรัวๆ ระหว่างรอ API ตอบกลับ (`setButtonsDisabled` ใน `main.js` — ทำไว้ตั้งแต่ Sprint 2 แล้ว)
- [x] CSS รองรับจอมือถือด้วย responsive layout (การ์ดกว้าง 100% สูงสุด 420px + media query) — **ทดสอบจริง
      ด้วย Chrome DevTools responsive mode (iPhone SE) แล้ว ทุกอย่างปกติดี**
- [x] เพิ่ม unit test ใหม่ 15 เคส ครอบคลุม decay logic, `/api/action` ผ่าน HTTP จริง, และ Data Access Layer
      (`save_pet`/`load_pet` roundtrip)

## 2. ผลการทดสอบระบบ (Quality Assurance & Debugging Report)

### 2.1 Unit Tests (`pytest`)
รันคำสั่ง `pytest -v` — ผลลัพธ์: **46 passed in 0.77s** (เพิ่มจาก 31 ใน Sprint 2 เป็น 46)

| กลุ่มไฟล์ทดสอบ | จำนวนเทส | ครอบคลุม |
|---|---|---|
| `tests/test_pet.py` | 7 | คลาส `Pet` (Sprint 1 เดิม) |
| `tests/test_history.py` | 13 | `web/history.py` (Sprint 2 เดิม) |
| `tests/test_web_app.py` | 26 | สไปรต์, `/api/interact` (mock API), `/api/history`, **ใหม่:** neglect decay (4 เคส),
  `/api/action` ผ่าน HTTP จริง (feed/play/rest/invalid — 4 เคส), `/api/state` (2 เคส), `save_pet`/`load_pet`
  roundtrip + ไฟล์เสีย/ไม่มี (3 เคส) |

### 2.2 Manual / Integration Testing แบบครบวงจร (Observation / Expected / Actual)
รันเซิร์ฟเวอร์จริงด้วย `python web/app.py` แล้วยิง `curl` ตรงไปที่ทุก endpoint (ไม่ใช่แค่ unit test แบบ mock)

| รายการทดสอบ | อินพุตที่ใช้ | ผลลัพธ์ที่คาดหวัง (Expected) | ผลการทดสอบจริง (Actual) | สถานะ |
|---|---|---|---|---|
| เปิดหน้าเว็บ | `GET /` | ตอบ 200 พร้อม HTML | HTTP 200 | PASSED |
| Feed | `POST /api/action {"action":"feed"}` | hunger ลดลง 20 | hunger 15→0 (ชนขอบล่างพอดี ไม่ติดลบ) | PASSED |
| Play | `POST /api/action {"action":"play"}` | energy ลด, mood เพิ่ม | energy 40→25, mood คงที่ 100 (ชนเพดานอยู่แล้ว) | PASSED |
| Rest | `POST /api/action {"action":"rest"}` | energy เพิ่มขึ้น (ไม่เกิน 100) | energy 25→50 | PASSED |
| คำสั่งไม่รู้จัก | `POST /api/action {"action":"nonsense"}` | ตอบ error, ไม่ crash | HTTP 400 พร้อมข้อความ "ไม่รู้จักคำสั่ง 'nonsense'" | PASSED |
| ดูประวัติ | `GET /api/history` | คืนประวัติที่มีอยู่จริง | ได้ 13 รายการจริงจาก Dog API/Cat Facts API (ของ Sprint 2) | PASSED |
| รีเฟรชหน้า (จำลองด้วยการเรียก `/api/state` ซ้ำ) | เรียก `/api/state` หลัง feed/play/rest | ค่าต้องตรงกับที่บันทึกไว้ล่าสุด | hunger=5, energy=50, mood=100 ตรงกับใน `data/pet_state.json` ทุกตัว | PASSED |
| จำลองปล่อยสัตว์เลี้ยงไว้นาน | แก้ `last_updated` ในไฟล์ให้เป็นเมื่อ 500 นาทีก่อน แล้วรีสตาร์ตเซิร์ฟเวอร์ | hunger/energy เปลี่ยนตามเวลาที่ผ่านไป, ขึ้นเตือนเมื่อวิกฤต | hunger 5→100, energy 50→0, mood ลดจากบทลงโทษ, `neglected: true` พร้อมข้อความเตือนครบทั้ง 2 กรณี (หิวมาก + หมดแรง) | PASSED |

## 3. สรุปบทเรียนประจำสัปดาห์ (Retrospective: Wow! & Whoops!)
- **Wow!** (ส่วนที่ทำได้ดี): ออกแบบ decay ให้อิงเวลาจริง (`last_updated` เทียบกับเวลาปัจจุบัน) แทนที่จะเป็น
  ตัวนับรอบ ทำให้ทดสอบง่ายด้วยการ mock เวลา (`monkeypatch` ค่า `now`) ได้ครบทุก edge case โดยไม่ต้องรอเวลาจริง
  ผ่านไปตอนรัน test; การเพิ่มเพดาน 24 ชม. กันไม่ให้ค่าพังหรือคำนวณเพี้ยนถ้ามีคนลืมเปิดโปรเจคไว้หลายวัน
- **Whoops!** (ปัญหาที่พบและแนวทางแก้ไข): ยังไม่ได้ตกลงบทบาททีมสำหรับ Sprint นี้ (ตาราง "บทบาทในทีม — Sprint 3"
  ใน `PLAN.md` ยังว่างอยู่) — ต้องให้ทีมช่วยปิดให้ครบก่อนส่งงานจริง (responsive mode ทดสอบแล้วผ่าน ปิดจุดนี้ได้แล้ว)
- **ลิงก์ Repository / Pull Request:** https://github.com/parima1209/virtual-pet-ai-companion

## 4. สิ่งที่ต้องทำต่อก่อนส่งงาน Sprint 3 (2/10/69)
- [x] เปิดเบราว์เซอร์จริง (responsive mode ใน DevTools) ทดสอบหน้าเว็บบนขนาดจอมือถือจริงๆ — ผ่าน ปกติดี
- [ ] ทีมตกลงบทบาทหมุนเวียน Sprint 3 แล้วกรอกตาราง "บทบาทในทีม — Sprint 3" ใน `PLAN.md`
- [ ] Push โค้ดชุดนี้ขึ้น GitHub (`web/app.py`, `main.js`, `style.css`, `index.html`, เทสใหม่, PLAN.md/CHANGELOG
      ที่อัปเดต, ไฟล์นี้)
- [ ] คุยกันในทีมแล้วกรอกตาราง Group/Individual Self-Assessment ของ Sprint 3 ใน `PLAN.md`
