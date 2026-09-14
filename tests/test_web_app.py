"""
tests/test_web_app.py
Unit test สำหรับ logic ฝั่ง Flask web app (web/app.py) โดยเฉพาะฟังก์ชันเลือกสไปรต์
รัน: pytest
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "web"))

from app import sprite_for  # noqa: E402
from src.pet import Pet  # noqa: E402


def test_sprite_idle_by_default():
    p = Pet(name="Buddy", hunger=30, mood=50, energy=80)
    assert sprite_for(p) == "idle"


def test_sprite_hungry_when_hunger_high():
    p = Pet(name="Buddy", hunger=75, mood=50, energy=80)
    assert sprite_for(p) == "hungry"


def test_sprite_sleepy_when_energy_low():
    p = Pet(name="Buddy", hunger=20, mood=50, energy=10)
    assert sprite_for(p) == "sleepy"


def test_sprite_happy_when_mood_high():
    p = Pet(name="Buddy", hunger=20, mood=85, energy=80)
    assert sprite_for(p) == "happy"


def test_hunger_takes_priority_over_mood():
    # ถ้าทั้งหิวมากและอารมณ์ดีมาก ให้ถือว่าหิวสำคัญกว่า
    p = Pet(name="Buddy", hunger=90, mood=95, energy=80)
    assert sprite_for(p) == "hungry"
