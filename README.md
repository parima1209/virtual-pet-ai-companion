# Virtual Pet (AI Companion)

โปรเจค Final Project วิชา **Script Programming (CP352301)** — แอปพลิเคชัน Python
จำลองการเลี้ยงสัตว์เลี้ยงเสมือน มี 2 หน้าตาให้ใช้งาน โดยใช้ Business Logic (`src/pet.py`) ร่วมกัน:
- **CLI** (`app.py`) — เวอร์ชันดั้งเดิมของ Sprint 1
- **เว็บสไตล์ Pixel Art Game** (`web/app.py`, ใช้ Flask) — เวอร์ชันใหม่ที่ต่อยอดจาก Sprint 1
  พร้อม Data Persistence (JSON) และ Data API Integration (Dog API / Cat Facts API) ในตัว

## สถานะโปรเจค
- [x] **Sprint 1** — Front-End App Dev (CLI + Pet class เบื้องต้น) — ส่งงาน 18/9/69
- [x] **Sprint 2** — Back-End App Dev (API integration, JSON persistence, ประวัติการโต้ตอบ +
  search/filter/sort) — ส่งงาน 25/9/69 (ทดสอบ API จริงบนเครื่องที่มีอินเทอร์เน็ตแล้ว ผ่านทุกกรณี)
- [ ] **Sprint 3** — Full-Stack App Dev — ส่งงาน 2/10/69
- [ ] **Final Sprint** — DevOps, CI/CD & AI Integration — ส่งงาน 16/10/69

รายละเอียดแผนงานแต่ละ Sprint ดูที่ [`PLAN.md`](./PLAN.md)
รายงานผล Sprint 1 ดูที่ [`reports/sprint1_report.md`](./reports/sprint1_report.md)
รายงานผล Sprint 2 ดูที่ [`reports/sprint2_report.md`](./reports/sprint2_report.md)

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

# 4. รัน unit tests (ครอบคลุมทั้ง CLI และเว็บ)
pytest
```

## วิธีเล่น
**CLI:** ตั้งชื่อสัตว์เลี้ยง แล้วเลือกคำสั่งจากเมนู: `feed` (ให้อาหาร), `play` (เล่นด้วย),
`rest` (พักผ่อน), `status` (เช็คสถานะ), `quit` (ออก)

**เว็บ (Pixel Art):** เปิดหน้าเว็บแล้วกดปุ่ม Feed / Play / Rest เพื่อดูแลสัตว์เลี้ยง
สไปรต์และแถบสถานะ (หิว/อารมณ์/พลังงาน) จะอัปเดตแบบเรียลไทม์ และกดปุ่ม **Interact**
เพื่อสุ่มดึงรูปสุนัขหรือ fact แมวจาก API ภายนอก (ได้รางวัลเป็นอารมณ์ที่เพิ่มขึ้นด้วย)

กดปุ่ม **📜 ประวัติการโต้ตอบ** เพื่อดูรายการ Interact ทั้งหมดที่เคยกด พร้อมช่องค้นหา
(ค้นข้อความในเนื้อหา), ตัวกรอง (ตามแหล่งที่มา/ประเภท), และตัวเลือกเรียงลำดับ (ใหม่→เก่า / เก่า→ใหม่)

ทั้งสองเวอร์ชันดูแลให้ความหิว ความสุข และพลังงานของสัตว์เลี้ยงอยู่ในระดับที่ดี

## โครงสร้างโปรเจค
```
virtual-pet-ai-companion/
├── app.py                     # entry point ของเวอร์ชัน CLI
├── src/
│   ├── pet.py                  # คลาส Pet (โมเดลข้อมูล / Business Logic) — ใช้ร่วมกันทั้ง CLI และเว็บ
│   └── cli.py                  # ส่วน CLI (Presentation Layer)
├── web/                        # เวอร์ชันเว็บ Pixel Art Game (Flask)
│   ├── app.py                   # Flask app + Data Access Layer (JSON) + Data API Integration
│   ├── history.py                # ประวัติการโต้ตอบ + ฟังก์ชัน search/filter/sort (Sprint 2)
│   ├── generate_sprites.py      # สคริปต์สร้างสไปรต์ Pixel Art (placeholder) ด้วย Pillow
│   ├── templates/
│   │   └── index.html           # หน้าเว็บเกม
│   └── static/
│       ├── css/style.css        # สไตล์ Pixel Art
│       ├── js/main.js           # เรียก REST API ของ Flask ฝั่ง client
│       └── sprites/             # ไฟล์ .png สไปรต์ 4 สถานะ (idle/happy/hungry/sleepy)
├── tests/
│   ├── test_pet.py             # unit test สำหรับคลาส Pet
│   ├── test_web_app.py         # unit test สำหรับเว็บแอป (sprite logic + /api/interact แบบ mock API)
│   └── test_history.py         # unit test สำหรับ search/filter/sort ของประวัติการโต้ตอบ
├── data/                        # เก็บ pet_state.json, interaction_history.json (สร้างอัตโนมัติตอนรันเว็บแอป)
├── reports/
│   ├── sprint1_report.md       # รายงานผล Sprint 1
│   └── sprint2_report.md       # รายงานผล Sprint 2
├── PLAN.md                      # แผนงานและ Definition of Done ราย Sprint
├── requirements.txt
└── README.md
```

## Stack เทคโนโลยี
- Python 3.x
- Framework Style: Object-Oriented Programming (OOP)
- Web Framework: Flask (เวอร์ชันเว็บ Pixel Art Game)
- Pixel Art: Pillow (PIL) สำหรับสร้างสไปรต์
- Testing: pytest
- API: Dog API (dog.ceo) และ Cat Facts API (catfact.ninja) ผ่าน `requests`
- Data Persistence: ไฟล์ JSON (`data/pet_state.json`)

## ทีมพัฒนา
บทบาทหมุนเวียนกันทุก Sprint (ดูรายละเอียดที่ [`PLAN.md`](./PLAN.md)) — ปัจจุบัน (Sprint 2):

| บทบาท | สมาชิก |
|---|---|
| Team Leader | แคร์ |
| Planner | ปริม |
| Coder | อาอิง |
| Debugger / QA | ยีนส์ |

**Repository:** https://github.com/parima1209/virtual-pet-ai-companion
