# แบบรายงานผลการดำเนินงาน Sprint 1

- **ชื่อโปรเจกต์:** Virtual Pet (AI Companion)
- **สัปดาห์ที่:** 1 (Sprint 1: Front-End App Dev)
- **สมาชิกในทีม:**
  - Team Leader: อาอิง
  - Planner: ยีนส์
  - Coder: ปริม
  - Debugger / QA: แคร์

## 1. สรุปความก้าวหน้าของงาน (Sprint Progress Summary)
- [x] ออกแบบโครงสร้างระบบและนิยาม Definition of Done ใน `PLAN.md`
- [x] พัฒนาชุดฟังก์ชันหลัก `display_welcome_message`, `get_command_input`, `is_valid_command`, `handle_command`, `main`
- [x] สร้างคลาส `Pet` เก็บสถานะ hunger / mood / energy พร้อมเมธอด `feed`, `play`, `rest`, `status`
- [x] ดักจับข้อผิดพลาดกรณีผู้ใช้ป้อนคำสั่งไม่ถูกต้องหรือกด Ctrl+C ด้วย try-except (ไม่ทำให้โปรแกรม crash)
- [x] เขียน unit test เบื้องต้น (`tests/test_pet.py`) และรันผ่านทั้งหมด
- [ ] ยังไม่เริ่ม: การเชื่อมต่อ API และการบันทึกข้อมูลแบบถาวร (วางแผนไว้ Sprint 2)
- [x] สร้าง GitHub repository และ push โค้ดขึ้นเรียบร้อยแล้ว

## 2. ผลการทดสอบระบบ (Quality Assurance & Debugging Report)

### 2.1 Unit Tests (`pytest`)
รันคำสั่ง `pytest -v` — ผลลัพธ์: **7 passed in 0.02s**

| รายการทดสอบ | ผลลัพธ์ที่คาดหวัง | ผลการทดสอบจริง | สถานะ |
|---|---|---|---|
| `test_pet_creation_defaults` | ค่าเริ่มต้น hunger=50, mood=50, energy=100 | ตรงตามคาด | PASSED |
| `test_feed_reduces_hunger` | feed(20) ลด hunger ลง 20 | hunger จาก 50 → 30 | PASSED |
| `test_feed_does_not_go_below_zero` | ค่า hunger ไม่ต่ำกว่า 0 | hunger คงที่ที่ 0 | PASSED |
| `test_play_reduces_energy_and_increases_mood` | play(15) เพิ่ม mood ลด energy | mood 50→65, energy 100→85 | PASSED |
| `test_play_refuses_when_too_tired` | เมื่อ energy ไม่พอ ต้องปฏิเสธการเล่นและไม่เปลี่ยนค่า | แสดงข้อความเตือน, energy คงที่ | PASSED |
| `test_stats_never_exceed_bounds` | ค่าทุกสถานะอยู่ในช่วง 0-100 เสมอ | อยู่ในช่วงที่กำหนด | PASSED |
| `test_to_dict_returns_current_state` | `to_dict()` คืนค่าตรงกับสถานะปัจจุบัน | ตรงตามคาด | PASSED |

### 2.2 Manual / CLI Smoke Test
รันโปรแกรมจริงด้วยลำดับคำสั่งจำลอง: ตั้งชื่อ → feed → play → rest → status → คำสั่งมั่ว ("blahblah") → `QUIT` (พิมพ์ใหญ่)

| รายการทดสอบ | อินพุตที่ใช้ | ผลลัพธ์ที่คาดหวัง | ผลการทดสอบจริง | สถานะ |
|---|---|---|---|---|
| การตั้งชื่อและต้อนรับ | `Buddy` | แสดงข้อความต้อนรับด้วยชื่อที่ตั้ง | แสดง "ยินดีต้อนรับ Buddy!" | PASSED |
| คำสั่ง feed | `feed` | hunger ลดลง, mood เพิ่มขึ้นเล็กน้อย | hunger 50→30 | PASSED |
| คำสั่ง play | `play` | mood เพิ่ม, energy ลด | mood 65→70, energy 85→85→85 (คำนวณถูกต้อง) | PASSED |
| คำสั่ง rest | `rest` | energy เพิ่มขึ้น (ไม่เกิน 100) | energy กลับไป 100 | PASSED |
| คำสั่ง status | `status` | แสดงสถานะล่าสุดครบทั้ง 3 ค่า | แสดงผลถูกต้อง | PASSED |
| การจัดการคำสั่งผิด | `blahblah` | แจ้งเตือน ไม่ทำให้โปรแกรมพัง | แสดง "คำสั่งไม่ถูกต้อง กรุณาเลือกจากเมนู (1-5)" | PASSED |
| การออกจากโปรแกรม (case-insensitive) | `QUIT` (พิมพ์ใหญ่) | แสดงข้อความอำลาและหยุดทำงาน | แสดงข้อความอำลาและหลุดจาก loop | PASSED |

## 3. สรุปบทเรียนประจำสัปดาห์ (Retrospective: Wow! & Whoops!)
- **Wow!** (ส่วนที่ทำได้ดี): แยก Presentation Layer (`cli.py`) ออกจาก Business Logic (`pet.py`) ได้ชัดเจนตั้งแต่ Sprint แรก ทำให้พร้อมต่อยอด Data Access Layer ใน Sprint 2 ได้ทันที; ทุกเมธอดของ `Pet` จำกัดค่าสถานะไม่ให้หลุดช่วง 0-100 ตั้งแต่ต้น ป้องกันบั๊กที่มักเจอทีหลัง
- **Whoops!** (ปัญหาที่พบและแนวทางแก้ไข): ยังไม่มีการเชื่อมต่อ API หรือบันทึกข้อมูลถาวร — เป็นไปตามแผนที่ตั้งใจเว้นไว้สำหรับ Sprint 2 (Back-End) ตามเอกสารคำชี้แจงของวิชา ไม่ใช่ข้อผิดพลาด แต่ต้องติดตามต่อให้ทันกำหนดส่ง 25/9/69
- **ลิงก์ Repository / Pull Request:** https://github.com/parima1209/virtual-pet-ai-companion

## 4. สิ่งที่ต้องทำต่อก่อนส่งงาน Sprint 1 (18/9/69)
- [x] ใส่ชื่อสมาชิกในทีมในไฟล์นี้, `PLAN.md`, และ `README.md`
- [x] สร้าง GitHub repository และ push โค้ดชุดนี้ขึ้นไป แล้วแปะลิงก์ในหัวข้อ 3
- [ ] (ถ้ามีเวลา) ทดสอบเพิ่มเติมกับ edge case อื่น ๆ เช่น กด Enter เปล่า หรือใส่ตัวเลขนอกช่วง 1-5
