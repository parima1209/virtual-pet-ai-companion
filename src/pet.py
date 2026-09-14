"""
pet.py
โมดูลคลาส Pet สำหรับโปรเจค Virtual Pet (AI Companion)

Sprint 1: โครงสร้างพื้นฐานของ Pet (เก็บสถานะแบบ in-memory เท่านั้น)
การบันทึกข้อมูลแบบถาวร (JSON persistence) และการเชื่อมต่อ API (Dog API / Cat Facts API)
จะเพิ่มใน Sprint 2 (Back-End App Dev / Data Access Layer)
"""

from dataclasses import dataclass

MAX_STAT = 100
MIN_STAT = 0


def _clamp(value: int, low: int = MIN_STAT, high: int = MAX_STAT) -> int:
    """จำกัดค่าสถานะให้อยู่ในช่วง [low, high] เสมอ"""
    return max(low, min(high, value))


@dataclass
class Pet:
    """
    ตัวแทนสัตว์เลี้ยงเสมือน (Virtual Pet)

    Attributes:
        name (str): ชื่อสัตว์เลี้ยง
        hunger (int): ระดับความหิว 0 (อิ่มมาก) - 100 (หิวมาก)
        mood (int): ระดับความสุข 0 (เศร้า) - 100 (มีความสุขมาก)
        energy (int): ระดับพลังงาน 0 (หมดแรง) - 100 (เต็มเปี่ยม)
    """

    name: str
    hunger: int = 50
    mood: int = 50
    energy: int = 100

    def feed(self, amount: int = 20) -> str:
        """ให้อาหารสัตว์เลี้ยง ลดค่าความหิวลงและเพิ่มความสุขเล็กน้อย"""
        self.hunger = _clamp(self.hunger - amount)
        self.mood = _clamp(self.mood + 5)
        return f"{self.name} กินอาหารอย่างเอร็ดอร่อย! (hunger: {self.hunger})"

    def play(self, amount: int = 15) -> str:
        """เล่นกับสัตว์เลี้ยง เพิ่มความสุขแต่ใช้พลังงานและทำให้หิวขึ้นเล็กน้อย"""
        if self.energy < amount:
            return f"{self.name} เหนื่อยเกินกว่าจะเล่นแล้ว ลองให้พักผ่อนก่อนนะ"
        self.energy = _clamp(self.energy - amount)
        self.mood = _clamp(self.mood + amount)
        self.hunger = _clamp(self.hunger + 5)
        return f"{self.name} สนุกกับการเล่นมาก! (mood: {self.mood}, energy: {self.energy})"

    def rest(self, amount: int = 25) -> str:
        """ให้สัตว์เลี้ยงพักผ่อน ฟื้นฟูพลังงาน"""
        self.energy = _clamp(self.energy + amount)
        return f"{self.name} พักผ่อนจนสดชื่นขึ้น (energy: {self.energy})"

    def status(self) -> str:
        """แสดงสถานะปัจจุบันของสัตว์เลี้ยงในรูปแบบอ่านง่าย"""
        return (
            f"--- สถานะของ {self.name} ---\n"
            f"  ความหิว (hunger) : {self.hunger}/100\n"
            f"  ความสุข (mood)   : {self.mood}/100\n"
            f"  พลังงาน (energy) : {self.energy}/100"
        )

    def to_dict(self) -> dict:
        """แปลงสถานะ Pet เป็น dict (เตรียมไว้สำหรับ JSON persistence ใน Sprint 2)"""
        return {
            "name": self.name,
            "hunger": self.hunger,
            "mood": self.mood,
            "energy": self.energy,
        }
