# Virtual Pet (AI Companion)

โปรเจค Final Project วิชา **Script Programming (CP352301)** — แอปพลิเคชัน Python
จำลองการเลี้ยงสัตว์เลี้ยงเสมือนผ่านหน้าจอ Command Line (CLI)

## สถานะโปรเจค
- [x] **Sprint 1** — Front-End App Dev (CLI + Pet class เบื้องต้น) — ส่งงาน 18/9/69
- [ ] **Sprint 2** — Back-End App Dev (API integration + JSON persistence) — ส่งงาน 25/9/69
- [ ] **Sprint 3** — Full-Stack App Dev — ส่งงาน 2/10/69
- [ ] **Final Sprint** — DevOps, CI/CD & AI Integration — ส่งงาน 16/10/69

รายละเอียดแผนงานแต่ละ Sprint ดูที่ [`PLAN.md`](./PLAN.md)
รายงานผล Sprint 1 ดูที่ [`reports/sprint1_report.md`](./reports/sprint1_report.md)

## วิธีติดตั้งและใช้งาน
```bash
# 1. สร้าง virtual environment (แนะนำ)
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# 2. ติดตั้ง dependencies
pip install -r requirements.txt

# 3. รันโปรแกรม
python app.py

# 4. รัน unit tests
pytest
```

## วิธีเล่น
1. ตั้งชื่อสัตว์เลี้ยงของคุณ
2. เลือกคำสั่งจากเมนู: `feed` (ให้อาหาร), `play` (เล่นด้วย), `rest` (พักผ่อน), `status` (เช็คสถานะ), `quit` (ออก)
3. ดูแลให้ความหิว ความสุข และพลังงานของสัตว์เลี้ยงอยู่ในระดับที่ดี

## โครงสร้างโปรเจค
```
virtual-pet-ai-companion/
├── app.py                   # entry point
├── src/
│   ├── pet.py                # คลาส Pet (โมเดลข้อมูล / Business Logic)
│   └── cli.py                 # ส่วน CLI (Presentation Layer)
├── tests/
│   └── test_pet.py           # unit test เบื้องต้นสำหรับคลาส Pet
├── data/                      # (ใช้ใน Sprint 2 สำหรับเก็บ pet_state.json)
├── reports/
│   └── sprint1_report.md     # รายงานผล Sprint 1
├── PLAN.md                    # แผนงานและ Definition of Done ราย Sprint
├── requirements.txt
└── README.md
```

## Stack เทคโนโลยี
- Python 3.x
- Framework Style: Object-Oriented Programming (OOP)
- Testing: pytest
- (แผน Sprint 2) API: Dog API หรือ Cat Facts API ผ่าน `requests`
- (แผน Sprint 2) Data Persistence: ไฟล์ JSON

## ทีมพัฒนา
| บทบาท | สมาชิก |
|---|---|
| Planner / Team Leader | _[ใส่ชื่อ]_ |
| Coder | _[ใส่ชื่อ]_ |
| Debugger / QA | _[ใส่ชื่อ]_ |

> กรุณาใส่ชื่อสมาชิกในทีมแทนช่องว่างด้านบน (แก้ไขได้ทั้งในไฟล์นี้และใน `PLAN.md`)
