# PLAN.md — Virtual Pet (AI Companion)

## ภาพรวมโปรเจค
Virtual Pet (AI Companion) คือแอปพลิเคชัน Python ที่จำลองการเลี้ยงสัตว์เลี้ยงเสมือน
ผู้ใช้สามารถให้อาหาร เล่นด้วย ให้พักผ่อน และเช็คสถานะ (ความหิว/ความสุข/พลังงาน) ของสัตว์เลี้ยงได้
โดยมี 2 หน้าตา (Presentation Layer) ที่ใช้ Business Logic เดียวกัน (`src/pet.py`):
- **CLI** (`app.py`, `src/cli.py`) — เวอร์ชันดั้งเดิมของ Sprint 1
- **เว็บ Pixel Art Game** (`web/`, ใช้ Flask) — เวอร์ชันที่ปรับหลัง Sprint 1 (ดูหัวข้อ "การปรับทิศทางหลัง Sprint 1" ด้านล่าง)
  รวม Data API Integration (Dog API / Cat Facts API ผ่านปุ่ม "Interact") และ Data Persistence (JSON) ไว้แล้ว

**รหัสวิชา:** CP352301 Script Programming
**Domain:** Pet Apps (Virtual Pet)
**Framework Style:** Object-Oriented Programming (OOP)

---

## การปรับทิศทางหลัง Sprint 1 (Pivot)
หลังส่ง Sprint 1 แบบ CLI แล้ว ทีมตัดสินใจเปลี่ยนหน้าตาโปรเจคเป็นเว็บสไตล์ **Pixel Art Game**
(ยังใช้คลาส `Pet` เดิมเป็น Business Logic) เพื่อให้ตรงกับธีมที่ต้องการมากขึ้น โดย:
- **ไม่ลบ/ไม่แก้ไฟล์ CLI เดิม** (`app.py`, `src/cli.py`) — ของที่ส่งไป Sprint 1 ยังอยู่ครบและรันได้เหมือนเดิม
- เพิ่มโฟลเดอร์ `web/` เป็นหน้าตาใหม่ (Flask) ที่เรียกใช้คลาส `Pet` เดิม จึงไม่กระทบคะแนน Sprint 1 ที่ส่งไปแล้ว
- สไปรต์ Pixel Art (4 สถานะ: idle/happy/hungry/sleepy) เป็น placeholder ที่สร้างด้วยสคริปต์ Pillow
  (`web/generate_sprites.py`) แก้ไข/เปลี่ยนภาพจริงภายหลังได้โดยไม่กระทบโค้ด

---

## Sprint 1 (สัปดาห์ที่ 12) — Front-End App Dev
กำหนดส่ง: **18/9/69**

**เป้าหมาย:** ออกแบบส่วนปฏิสัมพันธ์กับผู้ใช้ (CLI), จัดการเมนู, ตรวจสอบความถูกต้องของข้อมูลนำเข้า

### ขอบเขตระบบ CLI
- แสดงข้อความต้อนรับ (welcome banner)
- รับชื่อสัตว์เลี้ยงจากผู้ใช้
- เมนูหลัก 5 คำสั่ง: `feed`, `play`, `rest`, `status`, `quit` (พิมพ์เป็นเลข 1-5 ก็ได้)
- ตรวจสอบคำสั่งที่ไม่ถูกต้อง (invalid input) และแจ้งเตือนโดยไม่ทำให้โปรแกรมพัง
- ออกจากโปรแกรมได้ทันทีด้วยคำสั่ง `quit` โดยไม่สนใจตัวพิมพ์เล็ก-ใหญ่ (QUIT / Quit / quit)

### Definition of Done (DoD)
- [x] พิมพ์คำสั่ง `quit` ไม่ว่าตัวพิมพ์เล็กหรือใหญ่ ต้องออกจากโปรแกรมทันที
- [x] พิมพ์คำสั่งที่ไม่รู้จัก โปรแกรมต้องแจ้งเตือนและให้กรอกใหม่ ไม่ crash
- [x] คำสั่ง feed / play / rest / status ทำงานถูกต้องตามที่ออกแบบ และแสดงค่าสถานะล่าสุด
- [x] คลาส `Pet` เก็บสถานะ (hunger, mood, energy) และจำกัดค่าให้อยู่ระหว่าง 0-100 เสมอ
- [x] โค้ดแยกเป็นโมดูลตามหลัก Separation of Concerns (Pet → `src/pet.py`, CLI → `src/cli.py`, entry point → `app.py`)
- [x] มี unit test เบื้องต้นสำหรับคลาส Pet (`tests/test_pet.py`)

### Prompt ที่ใช้ในการพัฒนา (AI Prompt Log)
- **Prompt 1:** "reframe this into github and full function sourcecode for sprint 1"
<!-- TODO (ทีม): เติม prompt จริงที่ใช้กับโปรเจกต์ Virtual Pet นี้ (เช่น ตอน pivot เป็นเว็บ, Sprint 2-3, Final) -
     ลบ prompt เดิมข้อ 1 ออกเมื่อ 4/10/69 เพราะเป็นข้อความของโปรเจกต์อื่น (ทีม 3 คน หัวข้อ Typing Test CLI) -->

### สถาปัตยกรรม (Layer Separation)
| Layer | ไฟล์ | สถานะ |
|---|---|---|
| Presentation Layer (CLI) | `src/cli.py` | ทำแล้ว (Sprint 1) |
| Presentation Layer (เว็บ Pixel Art) | `web/app.py`, `web/templates/`, `web/static/` | ทำแล้ว (หลัง pivot) — ใช้ Flask |
| Business Logic Layer | `src/pet.py` (คลาส `Pet`) | ใช้ร่วมกันทั้ง CLI และเว็บ — ตรรกะเพิ่มเติม/AI interaction เพิ่มใน Sprint 2-3 |
| Data Access Layer | `web/app.py` (`load_pet`/`save_pet`), `web/history.py` | ทำแล้วในเวอร์ชันเว็บ — บันทึก/โหลด `data/pet_state.json` และ `data/interaction_history.json` |
| Data API Integration | `web/app.py` (`/api/interact`) | ทำแล้วในเวอร์ชันเว็บ — สุ่มเรียก Dog API หรือ Cat Facts API พร้อม error handling |
| Algorithm Layer (Search/Filter/Sort) | `web/history.py`, endpoint `/api/history` | ทำแล้ว (Sprint 2) — ค้นหา/กรอง/เรียงลำดับประวัติการโต้ตอบ |

### บทบาทในทีม — Sprint 1
| บทบาท | สมาชิก | หน้าที่ Sprint 1 |
|---|---|---|
| Team Leader | ยีนส์ | ดูแลภาพรวมทีม, ประสานงาน, ติดตามความคืบหน้าและกำหนดส่งงาน |
| Planner | อาอิง | เขียนสเปก, กำหนด DoD, จัดทำ PLAN.md |
| Coder | แคร์ | เขียนโค้ด `cli.py`, `pet.py`, `app.py` |
| Debugger / QA | ปริม | ทดสอบ edge case, เขียนรายงานผลใน `reports/sprint1_report.md` |

> **หมายเหตุ:** หมุนเวียนบทบาทกันทุก Sprint ตามคำแนะนำของวิชา

> **ปัญหาทางเทคนิคที่เจอและวิธีแก้ไขระหว่าง Sprint นี้:** ดูตารางละเอียดได้ในหัวข้อ 5 ของ
> `reports/sprint1_report.md`

### ประเมินผลงาน — Sprint 1
> **ผลการประเมินตนเอง (Self-Assessment) ของ Sprint นี้:** ย้ายไปอยู่ในหัวข้อ 6 ของ
> `reports/sprint1_report.md` แล้ว

---

## Sprint 2 (สัปดาห์ที่ 13) — Back-End App Dev
กำหนดส่ง: **25/9/69**

**เป้าหมาย:** ต่อยอด Business Logic, เชื่อมต่อ Data API (Dog API / Cat Facts API) และทำ Data Persistence
ด้วยไฟล์ JSON พร้อมจัดการ Exception ให้ครบถ้วน

> **หมายเหตุ:** Sprint นี้ทำเสร็จครบแล้วทุกข้อ (API integration, JSON persistence, ประวัติการโต้ตอบ,
> search/filter/sort, unit test แบบ mock API) รวมถึงทดสอบเรียก API จริงบนเครื่องที่มีอินเทอร์เน็ตจริง
> (นอก sandbox พัฒนา) แล้วด้วย — ได้รูปสุนัขและ cat fact จริงจาก Dog API/Cat Facts API ถูกต้อง
> และประวัติการโต้ตอบพร้อม search/filter/sort ทำงานถูกต้องตามที่ออกแบบ

### ขอบเขตระบบ
- เชื่อมต่อ Dog API (`https://dog.ceo/api/breeds/image/random`) และ Cat Facts API
  (`https://catfact.ninja/fact`) ผ่าน `requests` แบบสุ่มเลือก API เมื่อผู้ใช้กด "Interact"
- ตั้งค่า timeout การเรียก API (ไม่ปล่อยให้แอปค้าง) และจัดการ error ทุกกรณี:
  timeout, connection error, HTTP status ผิดพลาด, JSON/field ที่คาดไม่ถึง
- บันทึกสถานะ Pet (name, hunger, mood, energy) ลงไฟล์ `data/pet_state.json` ทุกครั้งที่สถานะเปลี่ยน
- โหลดสถานะจากไฟล์ JSON ตอนเริ่มโปรแกรม ถ้าไม่มีไฟล์หรือไฟล์เสียให้สร้างค่าเริ่มต้นแทน ไม่ crash
- เขียน unit test ที่ **mock** การเรียก API (ไม่พึ่งอินเทอร์เน็ตจริงตอนรัน test/CI)
- **เพิ่มระบบ "ประวัติการโต้ตอบ" (Interaction History)** — ทุกครั้งที่กด "Interact" บันทึกผลลัพธ์
  (timestamp, แหล่งที่มา `Dog API`/`Cat Facts API`, ประเภท `image`/`fact`, เนื้อหา) เป็นรายการ (list)
  ต่อท้ายไฟล์ `data/interaction_history.json` — เพื่อให้มีชุดข้อมูลจริงสำหรับทำ search/filter/sort
- **ฟังก์ชัน Searching** — ค้นหาประวัติการโต้ตอบจากคำค้น (เช่น ค้นข้อความใน cat fact)
- **ฟังก์ชัน Filtering** — กรองประวัติตามแหล่งที่มา (Dog API / Cat Facts API) หรือประเภท (image / fact)
- **ฟังก์ชัน Sorting** — เรียงลำดับประวัติตามเวลา (ใหม่→เก่า หรือ เก่า→ใหม่)
- เพิ่มหน้า/ส่วน UI (หรือ endpoint `/api/history`) ให้ผู้ใช้เรียกดูผลการค้นหา/กรอง/เรียงลำดับได้จริง
  (ไม่ใช่แค่ฟังก์ชันลับหลังบ้านที่ไม่มีใครเห็นผล — เพราะอาจารย์ให้สาธิตสดใน Live Demo)

### Definition of Done (DoD)
- [x] เรียก Dog API / Cat Facts API ได้จริงและนำข้อมูล (รูป/ข้อความ) มาแสดงผลในหน้าเว็บ
- [x] จัดการ timeout / connection error / bad response โดยแสดงข้อความที่เข้าใจง่าย ไม่ crash แอป
- [x] บันทึกสถานะ Pet ลงไฟล์ JSON ได้ และโหลดกลับมาได้ถูกต้องเมื่อเปิดโปรแกรมใหม่
- [x] กรณีไฟล์ JSON ไม่มีหรือเสีย โปรแกรมสร้างสัตว์เลี้ยงใหม่แทนโดยไม่ crash
- [x] มี unit test ที่ mock การเรียก API ครอบคลุมทั้งกรณีสำเร็จและกรณี error (`tests/test_web_app.py`)
- [x] ทดสอบเรียก API จริงบนเครื่องที่มีอินเทอร์เน็ต (นอก sandbox พัฒนา) อย่างน้อย 1 รอบ พร้อมบันทึกผลใน report
  (ทดสอบแล้วบนเครื่องจริงของทีม — ได้รูปสุนัข/cat fact จริงจาก API ถูกต้อง)
- [x] บันทึกประวัติการโต้ตอบทุกครั้งที่กด Interact ลง `data/interaction_history.json` ได้ถูกต้อง (`web/history.py`)
- [x] ฟังก์ชัน search ค้นหาประวัติจากคำค้นได้ถูกต้อง มี unit test รองรับ (`tests/test_history.py`)
- [x] ฟังก์ชัน filter กรองประวัติตามแหล่งที่มา/ประเภทได้ถูกต้อง มี unit test รองรับ (`tests/test_history.py`)
- [x] ฟังก์ชัน sort เรียงลำดับประวัติตามเวลาได้ถูกต้อง (ทั้ง 2 ทิศทาง) มี unit test รองรับ (`tests/test_history.py`)
- [x] มีช่องทางในหน้าเว็บให้สาธิตผลลัพธ์ search/filter/sort ได้จริงตอน Live Demo
  (ปุ่ม "📜 ประวัติการโต้ตอบ" เปิดแผงค้นหา/กรอง/เรียงลำดับ พร้อมอัปเดตผลแบบเรียลไทม์)

### บทบาทในทีม — Sprint 2
| บทบาท | สมาชิก | หน้าที่ Sprint 2 |
|---|---|---|
| Team Leader | แคร์ | ดูแลภาพรวมทีม, ประสานงาน, ติดตามความคืบหน้าและกำหนดส่งงาน |
| Planner | ปริม | เขียนสเปก/ขอบเขต Sprint 2, กำหนด DoD, อัปเดต PLAN.md |
| Coder | อาอิง | เขียนโค้ด `web/app.py`, `web/history.py` |
| Debugger / QA | ยีนส์ | ทดสอบ edge case, เขียนรายงานผลใน `reports/sprint2_report.md` |

> **หมายเหตุ:** หมุนเวียนบทบาทกันทุก Sprint ตามคำแนะนำของวิชา

> **ปัญหาทางเทคนิคที่เจอและวิธีแก้ไขระหว่าง Sprint นี้:** ดูตารางละเอียดได้ในหัวข้อ 5 ของ
> `reports/sprint2_report.md`

### ประเมินผลงาน — Sprint 2
> **ผลการประเมินตนเอง (Self-Assessment) ของ Sprint นี้:** ย้ายไปอยู่ในหัวข้อ 6 ของ
> `reports/sprint2_report.md` แล้ว

---

## Sprint 3 (สัปดาห์ที่ 14) — Full-Stack App Dev
กำหนดส่ง: **2/10/69**

**เป้าหมาย:** เชื่อม Front-End (เว็บ Pixel Art) กับ Back-End (Flask + Pet class) ให้ทำงานสมบูรณ์แบบ end-to-end,
จัดการ State ระหว่าง session, และรับมือ Edge Case ต่างๆ

### ขอบเขตระบบ
- ทุกปุ่มบนหน้าเว็บ (Feed / Play / Rest / Interact) เรียก REST API ของ Flask และอัปเดตหน้าจอ
  (สไปรต์ + แถบสถานะ) แบบเรียลไทม์โดยไม่ต้องรีเฟรชหน้า
- รีเฟรชหน้าเว็บแล้วสถานะสัตว์เลี้ยงต้องไม่หาย (โหลดจาก `data/pet_state.json` เสมอ)
- เพิ่มกลไกรับมือเมื่อผู้ใช้ปล่อยสัตว์เลี้ยงไว้นาน (เช่น หิวมาก/พลังงานหมด → สถานะพิเศษ หรือข้อความเตือน)
- ป้องกันการกดปุ่มรัว ๆ ระหว่างรอ API ตอบกลับ (disable ปุ่มชั่วคราว — ทำไปแล้วบางส่วนใน `main.js`)
- ปรับ UI ให้ใช้งานได้ดีทั้งจอคอมและมือถือ (responsive)

### Definition of Done (DoD)
- [x] กดปุ่มแต่ละปุ่มแล้ว state ฝั่ง client กับฝั่ง server ตรงกันเสมอ (ทุก endpoint คืน state ล่าสุดกลับมาให้ client render ใหม่ทันที)
- [x] รีเฟรชหน้าเว็บกลางคันแล้วสถานะยังอยู่ครบถูกต้อง (ทดสอบจริง: feed→play→rest แล้วเรียก /api/state ซ้ำ ค่าที่ได้ตรงกับที่บันทึกใน data/pet_state.json ทุกครั้ง)
- [x] มีข้อความ/สถานะพิเศษเมื่อสัตว์เลี้ยงถูกละเลยนานเกินไป (เพิ่มระบบ neglect decay ตามเวลาจริงที่ผ่านไปใน `web/app.py`, แจ้งเตือนใน UI — ทดสอบจริงด้วยการจำลองปล่อยไว้ 500 นาที: hunger ขึ้นไป 100, energy ลงไป 0, ขึ้นข้อความเตือนถูกต้อง)
- [x] ทดสอบบนหน้าจอมือถือ (หรือ browser responsive mode) แล้วใช้งานได้ปกติ — ทีมเปิด Chrome DevTools
      responsive mode (iPhone SE, กว้าง < 420px) เช็คด้วยตาแล้ว ทุกอย่างปกติดี (การ์ด/ปุ่ม/แผงประวัติ
      ไม่ล้นจอ ไม่มี scroll แนวนอน)
- [x] ทดสอบ manual แบบครบวงจร (เปิดเกม → feed/play/rest/interact → ปิด/เปิดใหม่) อย่างน้อย 1 รอบ พร้อมบันทึกผล (รันจริงผ่าน curl ครบทุก endpoint รวม /api/history และกรณี invalid action คืน 400 — ดูผลละเอียดใน `reports/sprint3_report.md`)

> **ปัญหาทางเทคนิคที่เจอและวิธีแก้ไขระหว่าง Sprint นี้:** ดูตารางละเอียดได้ในหัวข้อ 5 ของ
> `reports/sprint3_report.md`

### บทบาทในทีม — Sprint 3
| บทบาท | สมาชิก | หน้าที่ Sprint 3 |
|---|---|---|
| Team Leader | ปริม | ดูแลภาพรวมทีม, ประสานงาน, ติดตามความคืบหน้าและกำหนดส่งงาน |
| Planner | แคร์ | เขียนสเปก/ขอบเขต Sprint 3, กำหนด DoD, อัปเดต PLAN.md |
| Coder | ยีนส์ | เขียนโค้ดเชื่อม Front-End กับ Back-End, neglect decay, responsive UI |
| Debugger / QA | อาอิง | ทดสอบ edge case, responsive mode, เขียนรายงานผลใน `reports/sprint3_report.md` |

> **หมายเหตุ:** หมุนเวียนบทบาทกันทุก Sprint ตามคำแนะนำของวิชา

### ประเมินผลงาน — Sprint 3
> **ผลการประเมินตนเอง (Self-Assessment) ของ Sprint นี้:** ย้ายไปอยู่ในหัวข้อ 6 ของ
> `reports/sprint3_report.md` แล้ว

---

## Final Sprint (สัปดาห์ที่ 16) — DevOps, CI/CD & AI Integration
กำหนดส่ง: **16/10/69**

**เป้าหมาย:** ทำ Unit Test ให้ครอบคลุมทุกฟังก์ชันหลัก, ตั้งค่า CI/CD อัตโนมัติ, เพิ่มฟีเจอร์ AI/Automation,
และเตรียมเอกสาร/นำเสนอให้พร้อม

### ขอบเขตระบบ
- ตั้งค่า GitHub Actions ให้รัน `pytest` และ `flake8` อัตโนมัติทุกครั้งที่ push หรือเปิด Pull Request
- เพิ่ม unit test ให้ครอบคลุม `src/pet.py`, `web/app.py` (sprite logic, action handling),
  Data Access Layer (JSON read/write), และ Data API Integration (แบบ mock)
- เพิ่มฟีเจอร์ AI/Automation อย่างน้อย 1 อย่าง (เช่น ข้อความให้กำลังใจ/ทำนายอารมณ์สัตว์เลี้ยงที่ฉลาดขึ้น
  หรือเชื่อมต่อ AI API ภายนอกเพิ่มเติม)
- จัดทำ README ฉบับสมบูรณ์ (ครอบคลุมทั้ง CLI และเว็บ) และเตรียม slide/พิตช์สำหรับนำเสนอ

### Definition of Done (DoD)
- [x] มี GitHub Actions workflow ที่รัน lint + test อัตโนมัติ และขึ้นสถานะ pass/fail บน GitHub ได้จริง
      (`.github/workflows/ci.yml` — รัน flake8 + pytest ทุกครั้งที่ push/เปิด PR เข้า main — ยืนยันแล้วว่า
      ขึ้นสถานะ ✅ เขียวจริงบน GitHub ตอนเปิด Pull Request #1 ก่อน merge เข้า main สำเร็จ)
- [x] Unit test ครอบคลุมทุกฟังก์ชันหลักของโปรเจค (ทั้ง Business Logic, Data Access, API Integration)
      — รวม 104 เคส (ตัวเลข ณ 4/10/69): `test_pet.py` (7, Business Logic คลาส `Pet`), `test_advisor.py`
      (10, Business Logic AI Advisor), `test_history.py` (13, Data Access Layer
      `interaction_history.json`), `test_web_app.py` (64, Data Access Layer `save_pet`/`load_pet`
      + Data API Integration แบบ mock ต่อ Dog API/Cat Facts API + HTTP endpoint ทั้งหมด รวมฟีเจอร์เสริม
      cleanliness/aging/night/rename/chat), `test_gemini_client.py` (10, mock การเรียก Gemini API ทั้งหมด)
      — รัน `pytest -v` แล้วผ่านครบทุกเคส
- [x] มีฟีเจอร์ AI/Automation อย่างน้อย 1 อย่างที่ทำงานได้จริงและสาธิตได้ (AI Advisor แบบ rule-based
      ใน `web/advisor.py`, endpoint `/api/advice`, ปุ่ม "🔮 คำแนะนำจาก AI" บนหน้าเว็บ — ทดสอบจริงบนเซิร์ฟเวอร์
      ที่รันจริง 2 รอบ ผลตรงกับที่คำนวณทุกครั้ง — เพิ่มเติมนอกเหนือ DoD: เชื่อมต่อ Gemini API ภายนอกจริง
      (`web/gemini_client.py`, endpoint `/api/chat`) ให้สัตว์เลี้ยงคุยตอบกลับได้ตามอารมณ์ปัจจุบัน มี fallback
      อัตโนมัติเมื่อไม่มี key/เรียกไม่สำเร็จ ทดสอบเรียก API จริงสำเร็จแล้ว)
- [x] README อธิบายวิธีติดตั้ง/รัน/ใช้งานครบถ้วน ทั้งเวอร์ชัน CLI และเว็บ (อัปเดตครบทุกฟีเจอร์ใหม่:
      neglect decay, AI Advisor, CI badge, โครงสร้างไฟล์ล่าสุด)
- [x] เตรียม Project Pitch (เอกสาร + slide) สำหรับนำเสนอเรียบร้อยแล้ว (ทำไปก่อนหน้านี้)

> **ปัญหาทางเทคนิคที่เจอและวิธีแก้ไขระหว่าง Sprint นี้:** ดูตารางละเอียดได้ในหัวข้อ 5 ของ
> `reports/final_report.md`

### บทบาทในทีม — Final Sprint
| บทบาท | สมาชิก | หน้าที่ Final Sprint |
|---|---|---|
| Team Leader | อาอิง | ดูแลภาพรวมทีม, ประสานงาน, ติดตามความคืบหน้าและกำหนดส่งงาน |
| Planner | ยีนส์ | เขียนสเปก/ขอบเขต Final Sprint, กำหนด DoD, อัปเดต PLAN.md |
| Coder | ปริม | เขียนโค้ด CI/CD, unit test, AI Advisor, Gemini API integration |
| Debugger / QA | แคร์ | ทดสอบ edge case, เขียนรายงานผลใน `reports/final_report.md` |

> **หมายเหตุ:** หมุนเวียนบทบาทกันทุก Sprint ตามคำแนะนำของวิชา

### ประเมินผลงาน — Final Sprint
> **ผลการประเมินตนเอง (Self-Assessment) ของ Sprint นี้:** ย้ายไปอยู่ในหัวข้อ 6 ของ
> `reports/final_report.md` แล้ว

