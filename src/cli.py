"""
cli.py
ส่วน Presentation Layer (Front-End / CLI) ของโปรเจค Virtual Pet (AI Companion)

Sprint 1 deliverable: เมนูหลัก, การรับและตรวจสอบข้อมูลนำเข้า (Input Validation)
"""

from src.pet import Pet

WELCOME_BANNER = r"""
=====================================
   Virtual Pet (AI Companion)
=====================================
"""

MENU_TEXT = """
เลือกคำสั่ง:
  [1] feed   - ให้อาหาร
  [2] play   - เล่นด้วยกัน
  [3] rest   - พักผ่อน
  [4] status - เช็คสถานะ
  [5] quit   - ออกจากโปรแกรม
"""

VALID_COMMANDS = {"1", "feed", "2", "play", "3", "rest", "4", "status", "5", "quit"}


def display_welcome_message() -> None:
    """แสดงข้อความต้อนรับและเมนูหลักเข้าสู่โปรแกรม"""
    print(WELCOME_BANNER)
    print(MENU_TEXT)


def get_command_input(prompt: str = "\nพิมพ์คำสั่ง > ") -> str:
    """
    รับคำสั่งจากผู้ใช้ พร้อมทำความสะอาดข้อมูลนำเข้า (Input Validation)
    - ลบช่องว่างหัวท้ายด้วย .strip()
    - แปลงเป็นตัวพิมพ์เล็กด้วย .lower() เพื่อไม่ให้ไวต่อตัวพิมพ์เล็ก-ใหญ่ (เช่น QUIT, Quit, quit)
    """
    raw = input(prompt)
    return raw.strip().lower()


def is_valid_command(command: str) -> bool:
    """ตรวจสอบว่าคำสั่งที่รับเข้ามาอยู่ในรายการคำสั่งที่รองรับหรือไม่"""
    return command in VALID_COMMANDS


def handle_command(command: str, pet: Pet) -> bool:
    """
    ประมวลผลคำสั่งของผู้ใช้ 1 คำสั่ง
    คืนค่า False เมื่อผู้ใช้ต้องการออกจากโปรแกรม มิฉะนั้นคืนค่า True
    """
    if command in ("1", "feed"):
        print(pet.feed())
    elif command in ("2", "play"):
        print(pet.play())
    elif command in ("3", "rest"):
        print(pet.rest())
    elif command in ("4", "status"):
        print(pet.status())
    elif command in ("5", "quit"):
        print(f"บาย ๆ แล้วมาเล่นกับ {pet.name} ใหม่นะ!")
        return False
    else:
        print("คำสั่งไม่ถูกต้อง กรุณาเลือกจากเมนู (1-5)")
    return True


def main() -> None:
    """จุดเริ่มต้นการทำงานของโปรแกรม ควบคุมลูปหลักด้วย while True + try-except"""
    display_welcome_message()

    raw_name = get_command_input("ตั้งชื่อสัตว์เลี้ยงของคุณ > ")
    pet = Pet(name=raw_name.title() if raw_name else "Pet")
    print(f"\nยินดีต้อนรับ {pet.name}!")

    running = True
    while running:
        try:
            command = get_command_input()
            if not is_valid_command(command):
                print("คำสั่งไม่ถูกต้อง กรุณาเลือกจากเมนู (1-5)")
                continue
            running = handle_command(command, pet)
        except (KeyboardInterrupt, EOFError):
            print("\nออกจากโปรแกรมทันที (Ctrl+C)")
            break
        except ValueError as exc:
            print(f"เกิดข้อผิดพลาดด้านข้อมูล: {exc}")


if __name__ == "__main__":
    main()
