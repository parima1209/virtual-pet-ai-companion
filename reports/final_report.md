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
- [x] (เพิ่มเติมนอกเหนือ DoD) เชื่อมต่อ **Gemini API ภายนอกจริง** (`web/gemini_client.py`, endpoint
      `/api/chat`) ให้สัตว์เลี้ยงคุยตอบกลับผู้ใช้ได้ตามอารมณ์ปัจจุบัน มี fallback อัตโนมัติเมื่อไม่มี
      API key หรือเรียกไม่สำเร็จ ไม่ทำให้แอป crash
- [x] จัดทำ README ฉบับสมบูรณ์ ครอบคลุมทั้งเวอร์ชัน CLI และเว็บ พร้อมฟีเจอร์ใหม่ทั้งหมด
- [x] เตรียม Project Pitch (เอกสาร + slide) สำหรับนำเสนอเรียบร้อยแล้ว (ทำไปก่อนหน้านี้)
- [ ] ยังไม่เคยเห็นสถานะ GitHub Actions รันจริงบน GitHub (รอ push ครั้งถัดไป)
- [ ] ทีมยังไม่ได้ตกลงบทบาทหมุนเวียนและคะแนน Self-Assessment ของ Final Sprint

## 2. ผลการทดสอบระบบ (Quality Assurance & Debugging Report)

### 2.1 Unit Tests (`pytest`)
รันคำสั่ง `pytest -v` — ผลลัพธ์: **87 passed in 0.7s** (เพิ่มจาก 46 ใน Sprint 3 เป็น 58 ตอน DoD ของ Final Sprint และเพิ่มอีกเป็น 87 หลังทำฟีเจอร์เสริม lifelike pet เพิ่มเติม)

| กลุ่มไฟล์ทดสอบ | จำนวนเทส | ครอบคลุม |
|---|---|---|
| `tests/test_pet.py` | 7 | คลาส `Pet` |
| `tests/test_history.py` | 13 | `web/history.py` |
| `tests/test_advisor.py` | 10 | `web/advisor.py` — AI Advisor แบบ rule-based |
| `tests/test_web_app.py` | 47 | สไปรต์, `/api/interact`, `/api/history`, neglect decay, `/api/action`,
  `/api/state`, `save_pet`/`load_pet`, `/api/advice`, `/` index route, ฟีเจอร์เสริม (cleanliness/aging/
  night/rename/chat) |
| `tests/test_gemini_client.py` | 10 | `web/gemini_client.py` — mock การเรียก Gemini API ทั้งหมด |

### 2.2 Lint (`flake8`)
รันคำสั่ง `flake8 --max-line-length=110 src/ web/ tests/ app.py` — **ไม่มี error** (เจอ 1 บรรทัดยาวเกิน
ใน `web/advisor.py` ระหว่างพัฒนา แก้เรียบร้อยแล้วก่อน commit)

### 2.3 Manual / Integration Testing (Observation / Expected / Actual)

| รายการทดสอบ | อินพุตที่ใช้ | ผลลัพธ์ที่คาดหวัง (Expected) | ผลการทดสอบจริง (Actual) | สถานะ |
|---|---|---|---|---|
| `GET /api/advice` (สถานะปกติ) | สถานะเริ่มต้นจาก `data/pet_state.json` | คำนวณคะแนน + แนะนำ action ตรงกับสูตร | ได้คะแนน 89/100 แนะนำ feed ตรงกับที่คำนวณมือ | PASSED |
| `GET /api/advice` (หิวมาก) | ตั้ง hunger = 92 แล้วรีสตาร์ตเซิร์ฟเวอร์ | คะแนนลดลง แนะนำ feed | ได้คะแนน 70/100 แนะนำ feed ตรงกับสูตร | PASSED |
| `pytest -v` เต็มชุด | รันทั้งโปรเจค | ผ่านทั้งหมดไม่มี error | 87 passed | PASSED |
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

## 5. ปัญหาทางเทคนิคที่เจอและวิธีแก้ไข (Technical Issues & Fixes)

| ปัญหาที่เจอ | อาการที่พบ | สาเหตุ | วิธีแก้ไข |
|---|---|---|---|
| แอนิเมชันสัตว์เลี้ยงไม่ขยับ | เพิ่มโค้ด idle animation (`@keyframes idle-bob`) แล้ว แต่เปิดเว็บมาสไปรต์นิ่งสนิท ไม่ขยับเลย | เครื่องทดสอบตั้งค่า accessibility "Animation effects" ของ Windows ไว้ปิด เบราว์เซอร์เลยเคารพ `prefers-reduced-motion` แล้วไม่เล่นแอนิเมชันให้ — ไม่ใช่บั๊กโค้ด | ยืนยันว่า CSS ถูกต้องแล้วโดยเปิดค่า accessibility เครื่องทดสอบดู พร้อมคง fallback `prefers-reduced-motion` ไว้ตามหลัก accessibility |
| ฟีเจอร์คุยกับสัตว์เลี้ยง (Gemini) ไม่ทำงาน ได้แต่ข้อความสำรองตลอด | เรียก `/api/chat` แล้วได้คำตอบสำรอง (fallback) ทุกครั้ง ทั้งที่ตั้งค่า API key ใน `.env` ไว้แล้ว | ยังไม่ได้ติดตั้ง package `python-dotenv` ทำให้ `.env` ไม่ถูกโหลดเข้าโปรแกรม (โค้ดมี `try/except ImportError: pass` ดักไว้เงียบๆ) | รัน `pip install -r requirements.txt` ให้ครบ หลังจากนั้น `.env` ถูกโหลดถูกต้อง |
| โมเดล Gemini ที่ใช้ถูกเลิกใช้กลางทาง | เรียก Gemini API แล้วได้ error 404 | Google เลิกใช้โมเดล `gemini-2.0-flash` ไปแล้ว | ทดสอบเปลี่ยนโมเดลจริง 2 รอบ (`gemini-3.8-flash` แล้ว `gemini-flash-latest` เจอ `503 UNAVAILABLE` ทั้งคู่เพราะโมเดลแน่น) จนได้ `gemini-flash-lite-latest` ที่เสถียรจริง เลือกใช้ alias `-latest` แทนเลขเวอร์ชันตรงๆ เพื่อลดปัญหาซ้ำในอนาคต |
| ผลเทสไม่นิ่ง (ได้ผลไม่เหมือนกันทุกรอบที่รัน) | เทสที่เกี่ยวกับ cleanliness บางครั้งผ่านบางครั้งไม่ผ่าน | เทสอ่านค่า cleanliness จากไฟล์ `data/pet_state.json` จริงบนเครื่องตอน import แทนที่จะเป็นค่าที่ mock ไว้ ทำให้ผลไม่ deterministic ข้ามเครื่อง/ข้ามรอบรัน | pin ค่า cleanliness ที่รู้ค่าแน่นอนใน 3 เทสเดิมที่เกี่ยวข้อง (`tests/test_web_app.py`) |
| ตัวหนังสือมองไม่เห็นตอนเข้าโหมดกลางคืน | พื้นหลังเปลี่ยนเป็นสีเข้มตอนกลางคืนอัตโนมัติ แต่บางตัวหนังสือ (หัวข้อ, ชื่อสัตว์เลี้ยง, ค่าตัวเลขสถานะ) ยังเป็นสีเข้มเหมือนเดิม อ่านไม่ออก | สีตัวหนังสือของส่วนนี้ถูกกำหนดตายตัวไว้ ไม่ได้ override ให้เปลี่ยนตามธีมกลางคืน | เพิ่ม CSS override เฉพาะจุดให้ตัวหนังสือกลุ่มนี้เปลี่ยนเป็นสีสว่างตอนกลางคืน โดยไม่กระทบปุ่ม/ป้าย/ช่องกรอกที่ยังคงสว่างเหมือนเดิม |
| โค้ดไม่ผ่านมาตรฐาน lint ตอนจะ commit | รัน `flake8` แล้วไม่ผ่าน | มีบรรทัดหนึ่งใน `web/advisor.py` ยาวเกิน 110 ตัวอักษรตามมาตรฐานที่ทีมตั้งไว้ | แก้บรรทัดให้สั้นลงจนผ่าน `flake8` ก่อน commit |
