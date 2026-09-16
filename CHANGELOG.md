# Changelog

บันทึกการเปลี่ยนแปลงที่สำคัญของโปรเจค Virtual Pet (AI Companion) เรียงจากใหม่ล่าสุดไปเก่าสุด
รูปแบบอ้างอิงจาก [Keep a Changelog](https://keepachangelog.com/) — เลขเวอร์ชันอิงตาม [Semantic Versioning](https://semver.org/)
(อยู่ระหว่าง 0.x.0 เพราะยังไม่ถึง Final Sprint — จะขึ้น 1.0.0 เมื่อส่งงานฉบับสมบูรณ์)

## [Unreleased] — Sprint 3 & Final Sprint

วางแผนไว้ใน `PLAN.md` ยังไม่เริ่มดำเนินการ:
- Sprint 3 (กำหนดส่ง 2/10/69, จะขึ้นเป็น v0.4.0): เชื่อม Front-End กับ Back-End แบบ end-to-end, จัดการ state ระหว่าง session, รองรับหน้าจอมือถือ
- Final Sprint (กำหนดส่ง 16/10/69, จะขึ้นเป็น v1.0.0): GitHub Actions (CI/CD), unit test ครอบคลุมทุกฟังก์ชันหลัก, ฟีเจอร์ AI/Automation เพิ่มเติม

## [0.3.0] — Sprint 2 — 25/9/69

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

## [0.2.0] — Pivot — หลังส่ง Sprint 1

### Changed
- เปลี่ยนหน้าตาโปรเจคจาก CLI อย่างเดียว เป็นเว็บสไตล์ Pixel Art Game (Flask) เพิ่มเติม เพื่อให้ตรงกับธีมที่ต้องการมากขึ้น
- **ไม่ลบ/ไม่แก้ไฟล์ CLI เดิม** (`app.py`, `src/cli.py`) — ของที่ส่งไป Sprint 1 ยังอยู่ครบและรันได้เหมือนเดิม

### Added
- โฟลเดอร์ `web/` (app.py, templates, static) — หน้าตาใหม่ที่เรียกใช้คลาส `Pet` เดิม
- สคริปต์ `web/generate_sprites.py` สร้างสไปรต์ Pixel Art (4 สถานะ: idle/happy/hungry/sleepy) ด้วย Pillow

## [0.1.0] — Sprint 1 — 18/9/69

### Added
- คลาส `Pet` (`src/pet.py`) จัดการสถานะ hunger, mood, energy (จำกัดค่าให้อยู่ระหว่าง 0-100 เสมอ)
- CLI (`src/cli.py`, `app.py`) พร้อมเมนูหลัก 5 คำสั่ง: `feed`, `play`, `rest`, `status`, `quit`
- ตรวจสอบคำสั่งที่ไม่ถูกต้อง (invalid input) โดยไม่ทำให้โปรแกรมพัง
- ออกจากโปรแกรมด้วยคำสั่ง `quit` โดยไม่สนใจตัวพิมพ์เล็ก-ใหญ่
- unit test เบื้องต้น `tests/test_pet.py` (7 เคส)
- รายงานผล `reports/sprint1_report.md`
