# Changelog

บันทึกการเปลี่ยนแปลงที่สำคัญของโปรเจค Virtual Pet (AI Companion) เรียงจากใหม่ล่าสุดไปเก่าสุด
รูปแบบอ้างอิงจาก [Keep a Changelog](https://keepachangelog.com/) — เลขเวอร์ชันอิงตาม [Semantic Versioning](https://semver.org/)
(อยู่ระหว่าง 0.x.0 เพราะยังไม่ถึง Final Sprint — จะขึ้น 1.0.0 เมื่อส่งงานฉบับสมบูรณ์)

> **กติกาการอัปเดตไฟล์นี้ (ตั้งแต่ Sprint 3):** ทุกครั้งที่ commit โค้ด/ฟีเจอร์จริง ต้องเพิ่มบรรทัดใต้หัวข้อ
> `[Unreleased]` ในคอมมิตเดียวกันทันที ห้ามเขียนสรุปย้อนหลังทีเดียวตอนจบ Sprint — มี git hook เตือนอัตโนมัติ
> (`.githooks/pre-commit`, เปิดใช้ด้วย `git config core.hooksPath .githooks`)

## [Unreleased] — Final Sprint

กำหนดส่ง 16/10/69 (จะขึ้นเป็น v1.0.0) — กำลังดำเนินการ:

### Added
- **AI Advisor แบบ rule-based** (`web/advisor.py`, endpoint `/api/advice`) — วิเคราะห์สถานะปัจจุบัน
  (คิดคะแนนความเป็นอยู่ `wellbeing_score` ถ่วงน้ำหนัก mood/hunger/energy) + ความถี่การ Interact ใน 30 นาที
  ล่าสุดจากประวัติ แล้วทำนายแนวโน้มอารมณ์และแนะนำ action ที่ควรทำต่อไป — ไม่พึ่ง AI API ภายนอก/ไม่ต้องใช้
  internet เทสได้ deterministic 100% — เพิ่ม UI ปุ่ม "🔮 คำแนะนำจาก AI" ในหน้าเว็บ
- unit test ใหม่ 11 เคสสำหรับ AI Advisor (`tests/test_advisor.py` 10 เคส + `/api/advice` HTTP 1 เคส)
  — รวมทั้งโปรเจคเป็น 57 เคส (จาก 46)

### Verified
- ทดสอบ `/api/advice` จริงบนเซิร์ฟเวอร์ที่รันจริง 2 รอบ (สถานะปกติ แนะนำ feed ถูกต้องตามคะแนน 89/100 และ
  70/100 ตามลำดับ เมื่อ hunger สูงขึ้น) ตรงกับผลลัพธ์ที่คำนวณจาก `wellbeing_score` ทุกครั้ง

### Added
- `.github/workflows/ci.yml` — GitHub Actions รัน `flake8` + `pytest` อัตโนมัติทุกครั้งที่ push/เปิด PR
  เข้า `main` (ยังไม่เคยเห็นสถานะจริงบน GitHub เพราะรอ push ครั้งถัดไป)
- unit test เพิ่มอีก 1 เคส (`/` index route) — รวมทั้งโปรเจคเป็น 58 เคส (จาก 57)

### Fixed
- แก้บรรทัดยาวเกิน 110 ตัวอักษรใน `web/advisor.py` ที่ทำให้ `flake8` ไม่ผ่าน

ยังเหลือ: README ฉบับสมบูรณ์, reports/final_report.md, ทดสอบ responsive mode จริงบนเบราว์เซอร์

## [0.4.0] — Sprint 3 — 22/9/69 (กำหนดส่งจริง 2/10/69)

### Added
- ระบบ **Neglect Decay** (`web/app.py`) — ถ้าปล่อยสัตว์เลี้ยงไว้นานโดยไม่กดอะไรเลย hunger จะค่อยๆ เพิ่มขึ้น
  (+1 ทุก 5 นาทีจริง) และ energy จะค่อยๆ ลดลง (-1 ทุก 10 นาทีจริง) โดยอิงจาก `last_updated` ที่บันทึกไว้ใน
  `data/pet_state.json` — จำกัดเพดานไว้ที่ 24 ชม. กันค่าพังถ้าปล่อยไว้นานเป็นวันๆ
- ข้อความเตือน (`neglected`/`warning` ใน response ของ `/api/state`, `/api/action`, `/api/interact`) และแบนเนอร์
  เตือนบนหน้าเว็บ เมื่อ hunger ≥ 90 หรือ energy ≤ 10
- unit test ใหม่ 15 เคสสำหรับ Sprint 3/Final Sprint (decay logic 4 เคส, HTTP `/api/action` 4 เคส,
  `/api/state` 1 เคส, Data Access Layer `save_pet`/`load_pet` roundtrip 3 เคส) — รวมทั้งโปรเจคเป็น 46 เคส (จาก 31)

### Verified
- ทดสอบ manual แบบครบวงจรจริงผ่าน curl บนเซิร์ฟเวอร์ที่รันจริง (ไม่ใช่แค่ unit test): `/`, `/api/state`,
  `/api/action` (feed/play/rest/คำสั่งไม่รู้จัก), `/api/history` — ทุก endpoint ตอบถูกต้องตามที่ออกแบบ
- จำลองปล่อยสัตว์เลี้ยงไว้ 500 นาที (แก้ `last_updated` ในไฟล์ตรงๆ แล้วรีสตาร์ตเซิร์ฟเวอร์) — hunger ขึ้นไปที่ 100,
  energy ลงไปที่ 0, mood ลดลงจากบทลงโทษ, `neglected: true` พร้อมข้อความเตือนถูกต้องครบทั้งสองกรณี

### Known gaps
- ยังไม่ได้เปิดเบราว์เซอร์จริงทดสอบ responsive mode บนมือถือ (CSS มี media query รองรับแล้ว แต่รอทีมเช็คด้วยตา)

## [0.3.0] — Sprint 2 — 16/9/69 (กำหนดส่งจริง 25/9/69)

### Added
- เชื่อมต่อ Dog API (`dog.ceo`) และ Cat Facts API (`catfact.ninja`) ผ่านปุ่ม "Interact" แบบสุ่มเลือก พร้อม timeout และจัดการ error ครบทุกกรณี (timeout, connection error, bad response, payload ผิดรูปแบบ)
- ระบบบันทึก/โหลดสถานะ Pet ลงไฟล์ `data/pet_state.json` — ถ้าไฟล์ไม่มีหรือเสีย สร้างค่าเริ่มต้นแทนโดยไม่ crash
- โมดูลใหม่ `web/history.py` — "ประวัติการโต้ตอบ" (Interaction History) พร้อมฟังก์ชัน `search_history` (ค้นหา), `filter_history` (กรองตามแหล่งที่มา/ประเภท), `sort_history` (เรียงลำดับตามเวลา)
- endpoint ใหม่ `/api/history` — เปิดให้ค้นหา/กรอง/เรียงลำดับประวัติผ่าน query string (`q`, `source`, `kind`, `order`)
- UI แผงประวัติการโต้ตอบในหน้าเว็บ ("📜 ประวัติการโต้ตอบ") — ช่องค้นหา ตัวกรอง 2 ตัว ตัวเลือกเรียงลำดับ อัปเดตผลแบบเรียลไทม์
- unit test ใหม่ 24 เคส: `tests/test_history.py` (13 เคส) และเพิ่มใน `tests/test_web_app.py` (mock การเรียก API + ทดสอบ `/api/history`) — รวมทั้งโปรเจคเป็น 31 เคส (จาก 7 ใน Sprint 1)
- รายงานผล `reports/sprint2_report.md`

### Changed
- อัปเดตบทบาททีมตามการหมุนเวียนของ Sprint 2 (Team Leader: แคร์, Planner: ปริม, Coder: อาอิง, Debugger/QA: ยีนส์)
- อัปเดต `PLAN.md` และ `README.md` ให้ตรงกับความคืบหน้าจริง

### Verified
- ทดสอบเรียก Dog API / Cat Facts API จริงบนเครื่องที่มีอินเทอร์เน็ต (นอก sandbox พัฒนา) — ผ่านทุกกรณี ได้รูปสุนัขและ cat fact จริง บันทึกประวัติถูกต้อง

## [0.2.0] — Pivot — 14/9/69

### Changed
- เปลี่ยนหน้าตาโปรเจคจาก CLI อย่างเดียว เป็นเว็บสไตล์ Pixel Art Game (Flask) เพิ่มเติม เพื่อให้ตรงกับธีมที่ต้องการมากขึ้น
- **ไม่ลบ/ไม่แก้ไฟล์ CLI เดิม** (`app.py`, `src/cli.py`) — ของที่ส่งไป Sprint 1 ยังอยู่ครบและรันได้เหมือนเดิม

### Added
- โฟลเดอร์ `web/` (app.py, templates, static) — หน้าตาใหม่ที่เรียกใช้คลาส `Pet` เดิม
- สคริปต์ `web/generate_sprites.py` สร้างสไปรต์ Pixel Art (4 สถานะ: idle/happy/hungry/sleepy) ด้วย Pillow

## [0.1.0] — Sprint 1 — 14/9/69 (กำหนดส่งจริง 18/9/69)

### Added
- คลาส `Pet` (`src/pet.py`) จัดการสถานะ hunger, mood, energy (จำกัดค่าให้อยู่ระหว่าง 0-100 เสมอ)
- CLI (`src/cli.py`, `app.py`) พร้อมเมนูหลัก 5 คำสั่ง: `feed`, `play`, `rest`, `status`, `quit`
- ตรวจสอบคำสั่งที่ไม่ถูกต้อง (invalid input) โดยไม่ทำให้โปรแกรมพัง
- ออกจากโปรแกรมด้วยคำสั่ง `quit` โดยไม่สนใจตัวพิมพ์เล็ก-ใหญ่
- unit test เบื้องต้น `tests/test_pet.py` (7 เคส)
- รายงานผล `reports/sprint1_report.md`
