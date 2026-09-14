"""
tests/test_pet.py
Unit test เบื้องต้นสำหรับคลาส Pet (Sprint 1)
รัน: pytest
"""

from src.pet import Pet


def test_pet_creation_defaults():
    pet = Pet(name="Buddy")
    assert pet.name == "Buddy"
    assert pet.hunger == 50
    assert pet.mood == 50
    assert pet.energy == 100


def test_feed_reduces_hunger():
    pet = Pet(name="Buddy", hunger=50)
    pet.feed(20)
    assert pet.hunger == 30


def test_feed_does_not_go_below_zero():
    pet = Pet(name="Buddy", hunger=10)
    pet.feed(50)
    assert pet.hunger == 0


def test_play_reduces_energy_and_increases_mood():
    pet = Pet(name="Buddy", mood=50, energy=100)
    pet.play(15)
    assert pet.mood == 65
    assert pet.energy == 85


def test_play_refuses_when_too_tired():
    pet = Pet(name="Buddy", energy=5)
    result = pet.play(15)
    assert "เหนื่อยเกินกว่า" in result
    assert pet.energy == 5  # ค่าพลังงานต้องไม่เปลี่ยนแปลง


def test_stats_never_exceed_bounds():
    pet = Pet(name="Buddy", hunger=95, mood=95, energy=95)
    pet.feed(50)
    pet.rest(50)
    assert 0 <= pet.hunger <= 100
    assert 0 <= pet.mood <= 100
    assert 0 <= pet.energy <= 100


def test_to_dict_returns_current_state():
    pet = Pet(name="Buddy", hunger=40, mood=60, energy=80)
    assert pet.to_dict() == {
        "name": "Buddy",
        "hunger": 40,
        "mood": 60,
        "energy": 80,
    }
