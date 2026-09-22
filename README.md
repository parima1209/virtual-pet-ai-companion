# Virtual Pet (AI Companion)

![CI](https://github.com/parima1209/virtual-pet-ai-companion/actions/workflows/ci.yml/badge.svg)

โปรเจค Final Project วิชา **Script Programming (CP352301)** — แอปพลิเคชัน Python
จำลองการเลี้ยงสัตว์เลี้ยงเสมือน มี 2 หน้าตาให้ใช้งาน โดยใช้ Business Logic (`src/pet.py`) ร่วมกัน:
- **CLI** (`app.py`) — เวอร์ชันดั้งเดิมของ Sprint 1
- **เว็บสไตล์ Pixel Art Game** (`web/app.py`, ใช้ Flask) — เวอร์ชันใหม่ที่ต่อยอดจาก Sprint 1
  พร้อม Data Persistence (JSON), Data API Integration (Dog API / Cat Facts API), ระบบ Neglect Decay
  (ปล่อยไว้นานแล้วหิว/หมดแรงเอง), และ AI Advisor แบบ rule-based ที่แนะนำว่าควรทำอะไรต่อ

## สถานะโปรเจค
- [x] **Sprint 1** — Front-End App Dev (CLI + Pet class เบื้องต้น) — ส่งงาน 18/9/69
- [x] **Sprint 2** — Back-End App Dev (API integration, JSON persistence, ประวัติการโต้ตอบ +
  search/filter/sort) — ส่งงาน 25/9/69 (ทดสอบ API จริงบนเครื่องที่มีอินเทอร์เน็ตแล้ว ผ่านทุกกรณี)
- [~] **Sprint 3** — Full-Stack App Dev — ส่งงาน 2/10/69 — โค้ดหลักเสร็จแล้ว (neglect decay, ยืนยันด้วย
  manual test จริง + responsive mode ผ่าน Chrome DevTools แล้ว ปกติดี) เหลือแค่ตกลงบทบาท/คะแนนทีม + push
- [~] **Final Sprint** — DevOps, CI/CD & AI Integration — ส่งงาน 16/10/69 — GitHub Actions CI, unit test
  ครบ 58 เคส, และ AI Advisor เสร็จแล้ว เหลือ reports/final_report.md + ตกลงคะแนนทีม + push

รายละเอียดแผนงานแต่ละ Sprint ดูที่ [`PLAN.md`](./PLAN.md)
รายงานผล Sprint 1 ดูที่ [`reports/sprint1_report.md`](./reports/sprint1_report.md)
รายงานผล Sprint 2 ดูที่ [`reports/sprint2_report.md`](./reports/sprint2_report.md)
รายงานผล Sprint 3 ดูที่ [`reports/sprint3_report.md`](./reports/sprint3_report.md)

## วิธีติดตั้งและใช้งาน
```bash
# 1. สร้าง virtual environment (แนะนำ)
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# 2. ติดตั้ง dependencies
pip install -r requirements.txt

# 3a. รันเวอร์ชัน CLI (Sprint 1)
python app.py

# 3b. หรือรันเวอร์ชันเว็บ Pixel Art Game
python web/app.py
# แล้วเปิดเบราว์เซอร์ที่ http://127.0.0.1:5000

# 4. รัน unit tests (ครอบคลุมทั้ง CLI และเว็บ) — ควรได้ 58 passed
pytest

# 5. (ถ้าอยากเช็คแบบเดียวกับ CI) รัน lint ด้วย
flake8 --max-line-length=110 src/ web/ tests/ app.py
```
GitHub Actions (`.github/workflows/ci.yml`) จะรันทั้งสองคำสั่งนี้อัตโนมัติทุกครั้งที่ push หรือเปิด PR เข้า `main`

## การพัฒนา (Development)
รันคำสั่งนี้ครั้งเดียวต่อเครื่อง (ทุกคนในทีมที่ clone repo นี้) เพื่อเปิดใช้ git hook ที่จะเตือน
(ไม่บล็อก commit) เวลาแก้โค้ดแล้วลืมอัปเดต `CHANGELOG.md`:
```bash
git config core.hooksPath .githooks
```
กติกาโปรเจค: ทุกคอมมิตที่แก้ฟีเจอร์/โค้ดจริง ต้องอัปเดตหัวข้อ `[Unreleased]` ใน `CHANGELOG.md`
ไปพร้อมกันในคอมมิตเดียวกันเสมอ ห้ามเขียนสรุปย้อนหลังทีเดียวตอนจบ Sprint

## วิธีเล่น
**CLI:** ตั้งชื่อสัตว์เลี้ยง แล้วเลือกคำสั่งจากเมนู: `feed` (ให้อาหาร), `play` (เล่นด้วย),
`rest` (พักผ่อน), `status` (เช็คสถานะ), `quit` (ออก)

**เว็บ (Pixel Art):** เปิดหน้าเว็บแล้วกดปุ่ม Feed / Play / Rest เพื่อดูแลสัตว์เลี้ยง
สไปรต์และแถบสถานะ (หิว/อารมณ์/พลังงาน) จะอัปเดตแบบเรียลไทม์ และกดปุ่ม **Interact**
เพื่อสุ่มดึงรูปสุนัขหรือ fact แมวจาก API ภายนอก (ได้รางวัลเป็นอารมณ์ที่เพิ่มขึ้นด้วย)

กดปุ่ม **📜 ประวัติการโต้ตอบ** เพื่อดูรายการ Interact ทั้งหมดที่เคยกด พร้อมช่องค้นหา
(ค้นข้อความในเนื้อหา), ตัวกรอง (ตามแหล่งที่มา/ประเภท), และตัวเลือกเรียงลำดับ (ใหม่→เก่า / เก่า→ใหม่)

กดปุ่ม **🔮 คำแนะนำจาก AI** เพื่อดูคำทำนายแนวโน้มอารมณ์สัตว์เลี้ยง (คะแนนความเป็นอยู่ 0-100) และ
คำแนะนำว่าควรกด Feed/Play/Rest/Interact อะไรต่อไป — วิเคราะห์แบบ rule-based จากสถานะปัจจุบันและ
ความถี่การ Interact ใน 30 นาทีล่าสุด (`web/advisor.py`)

ถ้าปล่อยสัตว์เลี้ยงไว้นานโดยไม่กดอะไรเลย (เวลาจริงผ่านไปหลายสิบนาที) hunger จะค่อยๆ เพิ่มขึ้นและ
energy จะค่อยๆ ลดลงเอง พร้อมแบนเนอร์เตือนสีส้มขึ้นเมื่อหิวมาก/หมดแรง

ทั้งสองเวอร์ชันดูแลให้ความหิว ความสุข และพลังงานของสัตว์เลี้ยงอยู่ในระดับที่ดี

## โครงสร้างโปรเจค
```
virtual-pet-ai-companion/
├── .github/workflows/ci.yml    # GitHub Actions: flake8 + pytest อัตโนมัติทุก push/PR เข้า main
├── app.py                     # entry point ของเวอร์ชัน CLI
├── src/
│   ├── pet.py                  # คลาส Pet (โมเดลข้อมูล / Business Logic) — ใช้ร่วมกันทั้ง CLI และเว็บ
│   └── cli.py                  # ส่วน CLI (Presentation Layer)
├── web/                        # เวอร์ชันเว็บ Pixel Art Game (Flask)
│   ├── app.py                   # Flask app + Data Access Layer (JSON) + Data API Integration + neglect decay
│   ├── history.py                # ประวัติการโต้ตอบ + ฟังก์ชัน search/filter/sort (Sprint 2)
│   ├── advisor.py                # AI Advisor แบบ rule-based (Final Sprint) — /api/advice
│   ├── generate_sprites.py      # สคริปต์สร้างสไปรต์ Pixel Art (placeholder) ด้วย Pillow
│   ├── templates/
│   │   └── index.html           # หน้าเว็บเกม
│   └── static/
│       ├── css/style.css        # สไตล์ Pixel Art
│       ├── js/main.js           # เรียก REST API ของ Flask ฝั่ง client
│       └── sprites/             # ไฟล์ .png สไปรต์ 4 สถานะ (idle/happy/hungry/sleepy)
├── tests/
│   ├── test_pet.py             # unit test สำหรับคลาส Pet
│   ├── test_web_app.py         # unit test สำหรับเว็บแอป (routes, decay, mock API, /api/advice)
│   ├── test_history.py         # unit test สำหรับ search/filter/sort ของประวัติการโต้ตอบ
│   └── test_advisor.py         # unit test สำหรับ AI Advisor
├── data/                        # เก็บ pet_state.json, interaction_history.json (สร้างอัตโนมัติตอนรันเว็บแอป)
├── reports/
│   ├── sprint1_report.md       # รายงานผล Sprint 1
│   ├── sprint2_report.md       # รายงานผล Sprint 2
│   └── sprint3_report.md       # รายงานผล Sprint 3
├── .githooks/pre-commit         # เตือนเมื่อ commit โค้ดแล้วลืมอัปเดต CHANGELOG.md
├── PLAN.md                      # แผนงานและ Definition of Done ราย Sprint
├── CHANGELOG.md                  # บันทึกการเปลี่ยนแปลงราย version
├── requirements.txt
└── README.md
```

## Stack เทคโนโลยี
- Python 3.x
- Framework Style: Object-Oriented Programming (OOP)
- Web Framework: Flask (เวอร์ชันเว็บ Pixel Art Game)
- Pixel Art: Pillow (PIL) สำหรับสร้างสไปรต์
- Testing: pytest (58 เคส) + flake8 (lint)
- CI/CD: GitHub Actions (`.github/workflows/ci.yml`)
- API: Dog API (dog.ceo) และ Cat Facts API (catfact.ninja) ผ่าน `requests`
- Data Persistence: ไฟล์ JSON (`data/pet_state.json`, `data/interaction_history.json`)
- AI/Automation: AI Advisor แบบ rule-based (`web/advisor.py`) — ไม่พึ่ง AI API ภายนอก

## ทีมพัฒนา
สมาชิก 4 คน: แคร์, ปริม, อาอิง, ยีนส์ — บทบาทหมุนเวียนกันทุก Sprint (ดูรายละเอียดที่ [`PLAN.md`](./PLAN.md))

| Sprint | Team Leader | Planner | Coder | Debugger / QA |
|---|---|---|---|---|
| Sprint 1 | ยีนส์ | อาอิง | แคร์ | ปริม |
| Sprint 2 | แคร์ | ปริม | อาอิง | ยีนส์ |
| Sprint 3 | _(รอทีมตกลง)_ | _(รอทีมตกลง)_ | _(รอทีมตกลง)_ | _(รอทีมตกลง)_ |
| Final Sprint | _(รอทีมตกลง)_ | _(รอทีมตกลง)_ | _(รอทีมตกลง)_ | _(รอทีมตกลง)_ |

**Repository:** https://github.com/parima1209/virtual-pet-ai-companion
