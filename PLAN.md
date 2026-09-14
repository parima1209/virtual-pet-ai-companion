# PLAN.md — Virtual Pet (AI Companion)

## ภาพรวมโปรเจค
Virtual Pet (AI Companion) คือแอปพลิเคชัน Python แบบ CLI ที่จำลองการเลี้ยงสัตว์เลี้ยงเสมือน
ผู้ใช้สามารถให้อาหาร เล่นด้วย ให้พักผ่อน และเช็คสถานะ (ความหิว/ความสุข/พลังงาน) ของสัตว์เลี้ยงได้
ในสปรินต์ถัดไปจะต่อยอดให้ดึงข้อมูลจาก Dog API / Cat Facts API (เป็น "interaction") และบันทึกสถานะ
แบบถาวรด้วยไฟล์ JSON ตามข้อกำหนดของวิชา (Data API Integration + Data Persistence)

**รหัสวิชา:** CP352301 Script Programming
**Domain:** Pet Apps (Virtual Pet)
**Framework Style:** Object-Oriented Programming (OOP)

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

### สถาปัตยกรรม (Layer Separation)
| Layer | ไฟล์ | สถานะ Sprint 1 |
|---|---|---|
| Presentation Layer (CLI) | `src/cli.py` | ทำแล้ว |
| Business Logic Layer | `src/pet.py` (คลาส `Pet`) | ทำโครงสร้างพื้นฐานแล้ว — ตรรกะเพิ่มเติม/AI interaction เพิ่มใน Sprint 2-3 |
| Data Access Layer | ยังไม่เริ่ม | วางแผนใช้ไฟล์ JSON (`data/pet_state.json`) ใน Sprint 2 |

---

## บทบาทในทีม (หมุนเวียนตาม Sprint)
| บทบาท | สมาชิก | หน้าที่ Sprint 1 |
|---|---|---|
| Planner / Team Leader | _[ใส่ชื่อสมาชิก]_ | เขียนสเปก, กำหนด DoD, จัดทำ PLAN.md |
| Coder | _[ใส่ชื่อสมาชิก]_ | เขียนโค้ด `cli.py`, `pet.py`, `app.py` |
| Debugger / QA | _[ใส่ชื่อสมาชิก]_ | ทดสอบ edge case, เขียนรายงานผลใน `reports/sprint1_report.md` |

> **หมายเหตุ:** กรุณาใส่ชื่อสมาชิกในทีมแทนช่องว่างด้านบน แล้วหมุนเวียนบทบาทกันใน Sprint ถัดไปตามคำแนะนำของวิชา

---

## แผน Sprint ถัดไป (ภาพรวม)
- **Sprint 2 (Back-End App Dev, ส่ง 25/9/69):** เขียน Business Logic เพิ่มเติม, เชื่อมต่อ Dog API หรือ Cat Facts API (`requests`), บันทึก/โหลดสถานะ Pet เป็น JSON (File I/O), จัดการ Exception จาก API/ไฟล์
- **Sprint 3 (Full-Stack App Dev, ส่ง 2/10/69):** เชื่อม Front-End กับ Back-End ให้สมบูรณ์, จัดการ State ระหว่าง session, รับมือ Edge Cases
- **Final Sprint (DevOps/CI/CD/AI, ส่ง 16/10/69):** Unit test อัตโนมัติ (pytest) ครบทุกฟังก์ชัน, ตั้งค่า CI/CD (GitHub Actions: lint + test), เชื่อมฟีเจอร์ AI/Automation, จัดทำ README และเตรียมนำเสนอ
