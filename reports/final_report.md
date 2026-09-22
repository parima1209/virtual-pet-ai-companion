# แบบรายงานผลการดำเนินงาน Final Sprint

- **ชื่อโปรเจกต์:** Virtual Pet (AI Companion)
- **สัปดาห์ที่:** 4 (Final Sprint: DevOps, CI/CD & AI Integration)
- **สมาชิกในทีม:** แคร์, ปริม, อาอิง, ยีนส์ — _(ยังไม่ได้ตกลงหมุนเวียนบทบาทรอบนี้ รอทีมคุยกันแล้วกรอกในตาราง
  "บทบาทในทีม — Final Sprint" ใน `PLAN.md`)_

## 1. สรุปความก้าวหน้าของงาน (Sprint Progress Summary)
- [x] ตั้งค่า GitHub Actions (`.github/workflows/ci.yml`) ให้รัน `flake8` + `pytest` อัตโนมัติทุกครั้งที่
      push หรือเปิด Pull Request เข้า `main`
- [x] เพิ่ม unit test ให้ครอบคลุมทุกฟังก์ชันหลัก: Business Logic (`src/pet.py`), Data Access Layer
      (`save_pet`/`load_pet`), Data API Integration (mock), Neglect Decay, และ AI Advisor
- [x] เพิ่มฟีเจอร์ **AI/Automation** — AI Advisor แบบ rule-based (`web/advisor.py`, endpoint `/api/advice`)
      วิเคราะห์คะแนนความเป็นอยู่ + ความถี่การโต้ตอบ แล้วแนะนำ action ที่ควรทำต่อไป
- [x] จัดทำ README ฉบับสมบูรณ์ ครอบคลุมทั้งเวอร์ชัน CLI และเว็บ พร้อมฟีเจอร์ใหม่ทั้งหมด
- [x] เตรียม Project Pitch (เอกสาร + slide) สำหรับนำเสนอเรียบร้อยแล้ว (ทำไปก่อนหน้านี้)
- [ ] ยังไม่เคยเห็นสถานะ GitHub Actions รันจริงบน GitHub (รอ push ครั้งถัดไป)
- [ ] ทีมยังไม่ได้ตกลงบทบาทหมุนเวียนและคะแนน Self-Assessment ของ Final Sprint

## 2. ผลการทดสอบระบบ (Quality Assurance & Debugging Report)

### 2.1 Unit Tests (`pytest`)
รันคำสั่ง `pytest -v` — ผลลัพธ์: **58 passed in 0.46s** (เพิ่มจาก 46 ใน Sprint 3 เป็น 58)

| กลุ่มไฟล์ทดสอบ | จำนวนเทส | ครอบคลุม |
|---|---|---|
| `tests/test_pet.py` | 7 | คลาส `Pet` |
| `tests/test_history.py` | 13 | `web/history.py` |
| `tests/test_advisor.py` | 10 | `web/advisor.py` — AI Advisor แบบ rule-based |
| `tests/test_web_app.py` | 28 | สไปรต์, `/api/interact`, `/api/history`, neglect decay, `/api/action`,
  `/api/state`, `save_pet`/`load_pet`, `/api/advice`, `/` index route |

### 2.2 Lint (`flake8`)
รันคำสั่ง `flake8 --max-line-length=110 src/ web/ tests/ app.py` — **ไม่มี error** (เจอ 1 บรรทัดยาวเกิน
ใน `web/advisor.py` ระหว่างพัฒนา แก้เรียบร้อยแล้วก่อน commit)

### 2.3 Manual / Integration Testing (Observation / Expected / Actual)

| รายการทดสอบ | อินพุตที่ใช้ | ผลลัพธ์ที่คาดหวัง (Expected) | ผลการทดสอบจริง (Actual) | สถานะ |
|---|---|---|---|---|
| `GET /api/advice` (สถานะปกติ) | สถานะเริ่มต้นจาก `data/pet_state.json` | คำนวณคะแนน + แนะนำ action ตรงกับสูตร | ได้คะแนน 89/100 แนะนำ feed ตรงกับที่คำนวณมือ | PASSED |
| `GET /api/advice` (หิวมาก) | ตั้ง hunger = 92 แล้วรีสตาร์ตเซิร์ฟเวอร์ | คะแนนลดลง แนะนำ feed | ได้คะแนน 70/100 แนะนำ feed ตรงกับสูตร | PASSED |
| `pytest -v` เต็มชุด | รันทั้งโปรเจค | ผ่านทั้งหมดไม่มี error | 58 passed | PASSED |
| `flake8` เต็มโปรเจค | รันทั้ง `src/`, `web/`, `tests/`, `app.py` | ไม่มี lint error | ไม่มี error (หลังแก้ 1 จุด) | PASSED |

## 3. สรุปบทเรียนประจำสัปดาห์ (Retrospective: Wow! & Whoops!)
- **Wow!** (ส่วนที่ทำได้ดี): ออกแบบ AI Advisor แบบ rule-based ล้วน (ไม่พึ่ง API ภายนอก) ทำให้ผลลัพธ์
  deterministic ทดสอบได้ 100% โดยไม่ต้องกังวลเรื่อง API key/ค่าใช้จ่าย/อินเทอร์เน็ตหลุด — ยังคงตอบโจทย์
  "ทำนายอารมณ์สัตว์เลี้ยงที่ฉลาดขึ้น" ตามที่ PLAN.md เสนอไว้ตั้งแต่แรก
- **Whoops!** (ปัญหาที่พบและแนวทางแก้ไข): ยังไม่เคย push ขึ้น GitHub เลยตั้งแต่เริ่ม Sprint 3 ทำให้ยังไม่เห็น
  สถานะ GitHub Actions รันจริงสักครั้ง — ต้อง push แล้วเช็คสถานะ CI ให้ผ่านจริงก่อนวัน Live Demo ไม่ใช่แค่
  เชื่อผลจากการรันคำสั่งเดียวกันในเครื่อง
- **ลิงก์ Repository / Pull Request:** https://github.com/parima1209/virtual-pet-ai-companion

## 4. สิ่งที่ต้องทำต่อก่อนส่งงาน Final Sprint (16/10/69)
- [x] เปิดเบราว์เซอร์จริงทดสอบ responsive mode บนขนาดจอมือถือจริงๆ (ค้างมาจาก Sprint 3) — ผ่าน ปกติดี
- [ ] Push โค้ดทั้งหมดขึ้น GitHub แล้วเช็คว่า GitHub Actions ขึ้นสถานะ pass สีเขียวจริง
- [ ] ทีมตกลงบทบาทหมุนเวียน Sprint 3 และ Final Sprint แล้วกรอกตาราง "บทบาทในทีม" ที่เกี่ยวข้องใน `PLAN.md`
- [ ] คุยกันในทีมแล้วกรอกตาราง Group/Individual Self-Assessment ของ Sprint 3 และ Final Sprint ใน `PLAN.md`
- [ ] ซ้อม Live Demo ให้ครบทุกฟีเจอร์ (feed/play/rest/interact, ประวัติ, AI Advisor, neglect decay)
