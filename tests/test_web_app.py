"""
tests/test_web_app.py
Unit test สำหรับ logic ฝั่ง Flask web app (web/app.py) โดยเฉพาะฟังก์ชันเลือกสไปรต์
รัน: pytest
"""

import os
import sys
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "web"))

import app as web_app  # noqa: E402
from app import sprite_for  # noqa: E402
from src.pet import Pet  # noqa: E402


# ที่อยู่ไฟล์ข้อมูลจริงของโปรเจกต์ (จดไว้ตั้งแต่ import ก่อนที่เทสใดจะเปลี่ยนค่า) ใช้เช็คว่าเทสไม่แตะไฟล์จริง
REAL_STATE_FILE = web_app.STATE_FILE
REAL_HISTORY_FILE = web_app.history.HISTORY_FILE


@pytest.fixture(autouse=True)
def _isolate_data_files(monkeypatch, tmp_path):
    """ย้าย data/pet_state.json และ data/interaction_history.json ไปโฟลเดอร์ชั่วคราวในทุกเทส
    เดิมเทสบางตัวไม่ได้ redirect ไฟล์ ทำให้ `pytest` เขียนทับสถานะสัตว์เลี้ยงจริงของผู้รัน (แก้เมื่อ 4/10/69)
    เทสที่ monkeypatch STATE_FILE/HISTORY_FILE เองเพิ่มก็ยังใช้ได้ตามเดิม (ชี้ไปที่ tmp_path เดียวกัน)"""
    monkeypatch.setattr(web_app, "DATA_DIR", str(tmp_path))
    monkeypatch.setattr(web_app, "STATE_FILE", str(tmp_path / "pet_state.json"))
    monkeypatch.setattr(web_app.history, "DATA_DIR", str(tmp_path))
    monkeypatch.setattr(web_app.history, "HISTORY_FILE", str(tmp_path / "interaction_history.json"))


@pytest.fixture(autouse=True)
def _reset_decay_carry():
    """ล้างเศษ decay (_decay_carry) ก่อน/หลังทุกเทส กันค่าค้างข้ามเทสทำให้ผลไม่แน่นอน"""
    web_app._decay_carry.update(anchor=None, hunger=0.0, energy=0.0, clean=0.0)
    yield
    web_app._decay_carry.update(anchor=None, hunger=0.0, energy=0.0, clean=0.0)


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


# ---------------------------------------------------------------------------
# Sprint 2 — Unit test สำหรับ /api/interact แบบ mock การเรียก API จริง
# (ไม่พึ่งอินเทอร์เน็ตจริงตอนรัน test/CI ตามที่ DoD ของ Sprint 2 กำหนด)
# ---------------------------------------------------------------------------
def _fake_response(json_data):
    resp = MagicMock()
    resp.raise_for_status = MagicMock()
    resp.json.return_value = json_data
    return resp


def test_api_interact_dog_success(monkeypatch, tmp_path):
    monkeypatch.setattr(web_app.history, "HISTORY_FILE", str(tmp_path / "interaction_history.json"))
    monkeypatch.setattr(web_app.random, "choice", lambda seq: True)
    fake_resp = _fake_response({"status": "success", "message": "https://images.dog.ceo/x.jpg"})
    with patch.object(web_app.requests, "get", return_value=fake_resp):
        client = web_app.app.test_client()
        res = client.get("/api/interact")

    assert res.status_code == 200
    data = res.get_json()
    assert data["source"] == "Dog API"
    assert data["interaction"]["kind"] == "image"


def test_api_interact_cat_fact_success(monkeypatch, tmp_path):
    monkeypatch.setattr(web_app.history, "HISTORY_FILE", str(tmp_path / "interaction_history.json"))
    monkeypatch.setattr(web_app.random, "choice", lambda seq: False)
    fake_resp = _fake_response({"fact": "Cats sleep a lot."})
    with patch.object(web_app.requests, "get", return_value=fake_resp):
        client = web_app.app.test_client()
        res = client.get("/api/interact")

    assert res.status_code == 200
    data = res.get_json()
    assert data["source"] == "Cat Facts API"
    assert data["interaction"]["kind"] == "fact"


def test_api_interact_timeout_returns_friendly_error(monkeypatch, tmp_path):
    monkeypatch.setattr(web_app.history, "HISTORY_FILE", str(tmp_path / "interaction_history.json"))
    monkeypatch.setattr(web_app.random, "choice", lambda seq: True)
    with patch.object(web_app.requests, "get", side_effect=web_app.requests.exceptions.Timeout):
        client = web_app.app.test_client()
        res = client.get("/api/interact")

    assert res.status_code == 504
    assert "error" in res.get_json()


def test_api_interact_connection_error_returns_502(monkeypatch, tmp_path):
    monkeypatch.setattr(web_app.history, "HISTORY_FILE", str(tmp_path / "interaction_history.json"))
    monkeypatch.setattr(web_app.random, "choice", lambda seq: True)
    with patch.object(
        web_app.requests, "get", side_effect=web_app.requests.exceptions.ConnectionError
    ):
        client = web_app.app.test_client()
        res = client.get("/api/interact")

    assert res.status_code == 502
    assert "error" in res.get_json()


def test_api_interact_bad_payload_returns_502(monkeypatch, tmp_path):
    monkeypatch.setattr(web_app.history, "HISTORY_FILE", str(tmp_path / "interaction_history.json"))
    monkeypatch.setattr(web_app.random, "choice", lambda seq: True)
    fake_resp = _fake_response({"status": "error"})  # ไม่มี "message" ตามที่คาดหวัง
    with patch.object(web_app.requests, "get", return_value=fake_resp):
        client = web_app.app.test_client()
        res = client.get("/api/interact")

    assert res.status_code == 502
    assert "error" in res.get_json()


def test_api_history_search_filter_sort(monkeypatch, tmp_path):
    monkeypatch.setattr(web_app.history, "HISTORY_FILE", str(tmp_path / "interaction_history.json"))
    web_app.history.save_history([
        {"timestamp": "2026-01-01T10:00:00", "source": "Dog API", "kind": "image", "content": "a"},
        {"timestamp": "2026-01-02T10:00:00", "source": "Cat Facts API", "kind": "fact",
         "content": "cats nap"},
    ])
    client = web_app.app.test_client()

    res = client.get("/api/history?q=nap")
    assert res.get_json()["count"] == 1

    res = client.get("/api/history?source=Dog API")
    assert res.get_json()["count"] == 1

    res = client.get("/api/history?order=asc")
    results = res.get_json()["results"]
    assert results[0]["source"] == "Dog API"


# ---------------------------------------------------------------------------
# Sprint 3 — Unit test สำหรับ neglect decay (ปล่อยสัตว์เลี้ยงไว้นาน -> hunger/energy เปลี่ยนตามเวลาจริง)
# ---------------------------------------------------------------------------
def test_apply_neglect_decay_increases_hunger_and_decreases_energy(monkeypatch, tmp_path):
    monkeypatch.setattr(web_app, "STATE_FILE", str(tmp_path / "pet_state.json"))
    monkeypatch.setattr(web_app, "cleanliness", 100)
    fresh_pet = Pet(name="Buddy", hunger=30, mood=50, energy=80)
    monkeypatch.setattr(web_app, "pet", fresh_pet)
    now = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    monkeypatch.setattr(web_app, "last_updated", now - timedelta(minutes=30))

    web_app.apply_neglect_decay(now=now)

    # 30 นาที: hunger +12 (ทุก 2.5 นาที +1), energy -3 (ทุก 10 นาที -1)
    assert web_app.pet.hunger == 42
    assert web_app.pet.energy == 77
    assert web_app.last_updated == now


def test_apply_neglect_decay_no_last_updated_sets_baseline_without_changing_stats(tmp_path, monkeypatch):
    monkeypatch.setattr(web_app, "STATE_FILE", str(tmp_path / "pet_state.json"))
    fresh_pet = Pet(name="Buddy", hunger=30, mood=50, energy=80)
    monkeypatch.setattr(web_app, "pet", fresh_pet)
    monkeypatch.setattr(web_app, "last_updated", None)
    now = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

    web_app.apply_neglect_decay(now=now)

    assert web_app.pet.hunger == 30
    assert web_app.pet.energy == 80
    assert web_app.last_updated == now


def test_apply_neglect_decay_drops_mood_when_critically_neglected(monkeypatch, tmp_path):
    monkeypatch.setattr(web_app, "STATE_FILE", str(tmp_path / "pet_state.json"))
    monkeypatch.setattr(web_app, "cleanliness", 100)
    fresh_pet = Pet(name="Buddy", hunger=85, mood=50, energy=80)
    monkeypatch.setattr(web_app, "pet", fresh_pet)
    now = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    # ปล่อยไว้ 60 นาที -> hunger +24 (85->109 แต่ถูก clamp ที่ 100, ทะลุเกณฑ์ 90) -> mood ต้องลดลงด้วย
    monkeypatch.setattr(web_app, "last_updated", now - timedelta(minutes=60))

    web_app.apply_neglect_decay(now=now)

    assert web_app.pet.hunger == 100
    assert web_app.pet.mood == 45


def test_apply_neglect_decay_caps_at_24_hours(monkeypatch, tmp_path):
    monkeypatch.setattr(web_app, "STATE_FILE", str(tmp_path / "pet_state.json"))
    monkeypatch.setattr(web_app, "cleanliness", 100)
    fresh_pet = Pet(name="Buddy", hunger=0, mood=50, energy=100)
    monkeypatch.setattr(web_app, "pet", fresh_pet)
    now = datetime(2026, 1, 5, 12, 0, 0, tzinfo=timezone.utc)
    # ปล่อยไว้ 5 วัน แต่เพดานคือ 24 ชม. (1440 นาที) -> hunger +288 ก็ถูก clamp ที่ 100 อยู่ดี
    monkeypatch.setattr(web_app, "last_updated", now - timedelta(days=5))

    web_app.apply_neglect_decay(now=now)

    assert web_app.pet.hunger == 100
    assert web_app.pet.energy == 0


def test_state_payload_reports_neglected_and_warning_text(monkeypatch, tmp_path):
    monkeypatch.setattr(web_app, "STATE_FILE", str(tmp_path / "pet_state.json"))
    hungry_pet = Pet(name="Buddy", hunger=95, mood=50, energy=5)
    monkeypatch.setattr(web_app, "pet", hungry_pet)

    payload = web_app.state_payload()

    assert payload["neglected"] is True
    assert "Buddy" in payload["warning"]
    assert "หิว" in payload["warning"]
    assert "หมดแรง" in payload["warning"]


def test_state_payload_not_neglected_when_stats_ok():
    ok_pet = Pet(name="Buddy", hunger=30, mood=60, energy=80)
    with patch.object(web_app, "pet", ok_pet):
        payload = web_app.state_payload()
    assert payload["neglected"] is False
    assert payload["warning"] is None


def test_api_state_endpoint_applies_decay_from_elapsed_time(monkeypatch, tmp_path):
    monkeypatch.setattr(web_app, "STATE_FILE", str(tmp_path / "pet_state.json"))
    fresh_pet = Pet(name="Buddy", hunger=10, mood=50, energy=100)
    monkeypatch.setattr(web_app, "pet", fresh_pet)
    monkeypatch.setattr(
        web_app, "last_updated", datetime.now(timezone.utc) - timedelta(minutes=50)
    )

    client = web_app.app.test_client()
    res = client.get("/api/state")

    assert res.status_code == 200
    data = res.get_json()
    # 50 นาที: hunger +20 (10->30, ทุก 2.5 นาที +1), energy -5 (100->95)
    assert data["hunger"] == 30
    assert data["energy"] == 95


# ---------------------------------------------------------------------------
# Final Sprint — Unit test ครอบคลุม /api/action (Feed/Play/Rest/คำสั่งไม่รู้จัก) ผ่าน HTTP จริง
# ---------------------------------------------------------------------------
def _post_action(client, action):
    return client.post(
        "/api/action",
        json={"action": action},
        content_type="application/json",
    )


def test_api_action_feed_reduces_hunger(monkeypatch, tmp_path):
    monkeypatch.setattr(web_app, "STATE_FILE", str(tmp_path / "pet_state.json"))
    monkeypatch.setattr(web_app, "pet", Pet(name="Buddy", hunger=50, mood=50, energy=80))
    monkeypatch.setattr(web_app, "last_updated", datetime.now(timezone.utc))

    res = _post_action(web_app.app.test_client(), "feed")

    assert res.status_code == 200
    data = res.get_json()
    assert data["hunger"] == 30


def test_api_action_play_reduces_energy_increases_mood(monkeypatch, tmp_path):
    monkeypatch.setattr(web_app, "STATE_FILE", str(tmp_path / "pet_state.json"))
    monkeypatch.setattr(web_app, "pet", Pet(name="Buddy", hunger=30, mood=50, energy=80))
    monkeypatch.setattr(web_app, "last_updated", datetime.now(timezone.utc))

    res = _post_action(web_app.app.test_client(), "play")

    assert res.status_code == 200
    data = res.get_json()
    assert data["energy"] == 65
    assert data["mood"] == 65


def test_api_action_rest_restores_energy(monkeypatch, tmp_path):
    monkeypatch.setattr(web_app, "STATE_FILE", str(tmp_path / "pet_state.json"))
    monkeypatch.setattr(web_app, "pet", Pet(name="Buddy", hunger=30, mood=50, energy=50))
    monkeypatch.setattr(web_app, "last_updated", datetime.now(timezone.utc))

    res = _post_action(web_app.app.test_client(), "rest")

    assert res.status_code == 200
    assert res.get_json()["energy"] == 75


def test_api_action_unknown_action_returns_400(monkeypatch, tmp_path):
    monkeypatch.setattr(web_app, "STATE_FILE", str(tmp_path / "pet_state.json"))
    monkeypatch.setattr(web_app, "pet", Pet(name="Buddy", hunger=30, mood=50, energy=50))
    monkeypatch.setattr(web_app, "last_updated", datetime.now(timezone.utc))

    res = _post_action(web_app.app.test_client(), "blahblah")

    assert res.status_code == 400
    assert "error" in res.get_json()


def test_api_state_endpoint_returns_current_pet(monkeypatch, tmp_path):
    monkeypatch.setattr(web_app, "STATE_FILE", str(tmp_path / "pet_state.json"))
    monkeypatch.setattr(web_app, "pet", Pet(name="Mochi", hunger=40, mood=60, energy=90))
    monkeypatch.setattr(web_app, "last_updated", datetime.now(timezone.utc))

    res = web_app.app.test_client().get("/api/state")

    assert res.status_code == 200
    data = res.get_json()
    assert data["name"] == "Mochi"
    assert data["hunger"] == 40


# ---------------------------------------------------------------------------
# Final Sprint — Unit test สำหรับ Data Access Layer: save_pet / load_pet (JSON persistence)
# ---------------------------------------------------------------------------
def test_save_pet_then_load_pet_roundtrip(monkeypatch, tmp_path):
    state_file = tmp_path / "pet_state.json"
    monkeypatch.setattr(web_app, "STATE_FILE", str(state_file))
    p = Pet(name="Mochi", hunger=42, mood=63, energy=77)
    when = datetime(2026, 3, 1, 9, 30, 0, tzinfo=timezone.utc)

    web_app.save_pet(p, when=when)
    assert state_file.exists()

    loaded_pet, loaded_last_updated = web_app.load_pet()

    assert loaded_pet.name == "Mochi"
    assert loaded_pet.hunger == 42
    assert loaded_pet.mood == 63
    assert loaded_pet.energy == 77
    assert loaded_last_updated == when


def test_load_pet_missing_file_returns_default_buddy(monkeypatch, tmp_path):
    monkeypatch.setattr(web_app, "STATE_FILE", str(tmp_path / "does_not_exist.json"))

    loaded_pet, loaded_last_updated = web_app.load_pet()

    assert loaded_pet.name == "Buddy"
    assert loaded_last_updated is None


def test_load_pet_corrupt_file_returns_default_without_crash(monkeypatch, tmp_path):
    state_file = tmp_path / "pet_state.json"
    state_file.write_text("{ not valid json", encoding="utf-8")
    monkeypatch.setattr(web_app, "STATE_FILE", str(state_file))

    loaded_pet, loaded_last_updated = web_app.load_pet()

    assert loaded_pet.name == "Buddy"
    assert loaded_last_updated is None


def _restore_state_globals_after_test(monkeypatch):
    """load_pet() แก้ global cleanliness/growth_points/birth_time -> ให้ monkeypatch คืนค่าเดิมหลังจบเทส"""
    monkeypatch.setattr(web_app, "cleanliness", web_app.cleanliness)
    monkeypatch.setattr(web_app, "growth_points", web_app.growth_points)
    monkeypatch.setattr(web_app, "birth_time", web_app.birth_time)


def test_load_pet_json_that_is_not_an_object_returns_default(monkeypatch, tmp_path):
    # JSON ถูกไวยากรณ์แต่โครงสร้างผิด (list) เคย crash ตอนเริ่มโปรแกรมด้วย AttributeError
    _restore_state_globals_after_test(monkeypatch)
    state_file = tmp_path / "pet_state.json"
    state_file.write_text("[]", encoding="utf-8")
    monkeypatch.setattr(web_app, "STATE_FILE", str(state_file))

    loaded_pet, loaded_last_updated = web_app.load_pet()

    assert loaded_pet.name == "Buddy"
    assert (loaded_pet.hunger, loaded_pet.mood, loaded_pet.energy) == (50, 50, 100)
    assert loaded_last_updated is None
    assert web_app.cleanliness == 100 and web_app.growth_points == 0.0


def test_load_pet_non_utf8_file_returns_default_without_crash(monkeypatch, tmp_path):
    _restore_state_globals_after_test(monkeypatch)
    state_file = tmp_path / "pet_state.json"
    state_file.write_bytes(b"\xff\xfe\x00 not utf-8")
    monkeypatch.setattr(web_app, "STATE_FILE", str(state_file))

    loaded_pet, loaded_last_updated = web_app.load_pet()

    assert loaded_pet.name == "Buddy"
    assert loaded_last_updated is None


def test_load_pet_wrong_field_types_fall_back_per_field(monkeypatch, tmp_path):
    # ช่องที่ผิดชนิด (ข้อความ/null/list/bool) ใช้ค่าเริ่มต้นเฉพาะช่องนั้น ไม่ crash ตอนเริ่มโปรแกรม
    # และ /api/state ต้องตอบ 200 ได้ (เดิม hunger เป็นข้อความทำให้ตอบ 500)
    _restore_state_globals_after_test(monkeypatch)
    state_file = tmp_path / "pet_state.json"
    state_file.write_text(
        '{"name": null, "hunger": "abc", "mood": [1], "energy": true,'
        ' "cleanliness": {}, "growth_points": "x", "last_updated": 12345}',
        encoding="utf-8",
    )
    monkeypatch.setattr(web_app, "STATE_FILE", str(state_file))

    loaded_pet, loaded_last_updated = web_app.load_pet()

    assert loaded_pet.name == "Buddy"
    assert (loaded_pet.hunger, loaded_pet.mood, loaded_pet.energy) == (50, 50, 100)
    assert web_app.cleanliness == 100
    assert web_app.growth_points == 0.0
    assert loaded_last_updated is None

    monkeypatch.setattr(web_app, "pet", loaded_pet)
    monkeypatch.setattr(web_app, "last_updated", None)
    res = web_app.app.test_client().get("/api/state")
    assert res.status_code == 200
    assert res.get_json()["hunger"] == 50


def test_load_pet_clamps_out_of_range_numbers_and_keeps_valid_fields(monkeypatch, tmp_path):
    _restore_state_globals_after_test(monkeypatch)
    state_file = tmp_path / "pet_state.json"
    state_file.write_text(
        '{"name": "  Mochi  ", "hunger": 500, "mood": -50, "energy": "70.9",'
        ' "cleanliness": 1000, "growth_points": -5}',
        encoding="utf-8",
    )
    monkeypatch.setattr(web_app, "STATE_FILE", str(state_file))

    loaded_pet, _ = web_app.load_pet()

    assert loaded_pet.name == "Mochi"
    assert loaded_pet.hunger == 100
    assert loaded_pet.mood == 0
    assert loaded_pet.energy == 70
    assert web_app.cleanliness == 100
    assert web_app.growth_points == 0.0


def test_load_pet_truncates_overlong_name_and_rejects_nan(monkeypatch, tmp_path):
    _restore_state_globals_after_test(monkeypatch)
    state_file = tmp_path / "pet_state.json"
    state_file.write_text(
        '{"name": "' + "x" * 50 + '", "hunger": NaN, "growth_points": Infinity}', encoding="utf-8"
    )
    monkeypatch.setattr(web_app, "STATE_FILE", str(state_file))

    loaded_pet, _ = web_app.load_pet()

    assert len(loaded_pet.name) == web_app.MAX_NAME_LENGTH
    assert loaded_pet.hunger == 50
    assert web_app.growth_points == 0.0


def test_pytest_never_touches_real_data_files(monkeypatch):
    # กันบั๊ก "รัน pytest แล้วสถานะสัตว์เลี้ยงจริงถูกเขียนทับ": ไฟล์ที่เทสใช้ต้องไม่ใช่ไฟล์จริงของโปรเจกต์
    # และกดปุ่มผ่าน HTTP แล้วไฟล์จริงต้องไม่ถูกสร้าง/แก้ไข
    assert os.path.abspath(web_app.STATE_FILE) != os.path.abspath(REAL_STATE_FILE)
    assert os.path.abspath(web_app.history.HISTORY_FILE) != os.path.abspath(REAL_HISTORY_FILE)

    def snapshot(path):
        return open(path, "rb").read() if os.path.exists(path) else None

    monkeypatch.setattr(web_app, "pet", Pet(name="Buddy"))
    monkeypatch.setattr(web_app, "last_updated", None)
    before = (snapshot(REAL_STATE_FILE), snapshot(REAL_HISTORY_FILE))
    client = web_app.app.test_client()
    assert client.post("/api/action", json={"action": "feed"}).status_code == 200
    assert client.post("/api/rename", json={"name": "Tester"}).status_code == 200
    monkeypatch.setattr(web_app.random, "choice", lambda seq: False)
    with patch.object(web_app.requests, "get", return_value=_fake_response({"fact": "x"})):
        assert client.get("/api/interact").status_code == 200
    after = (snapshot(REAL_STATE_FILE), snapshot(REAL_HISTORY_FILE))

    assert before == after


def test_api_advice_endpoint_returns_recommendation(monkeypatch, tmp_path):
    monkeypatch.setattr(web_app, "STATE_FILE", str(tmp_path / "pet_state.json"))
    monkeypatch.setattr(web_app.history, "HISTORY_FILE", str(tmp_path / "interaction_history.json"))
    monkeypatch.setattr(web_app, "pet", Pet(name="Buddy", hunger=90, mood=50, energy=50))
    monkeypatch.setattr(web_app, "last_updated", datetime.now(timezone.utc))

    res = web_app.app.test_client().get("/api/advice")

    assert res.status_code == 200
    data = res.get_json()
    assert data["recommended_action"] == "feed"
    assert "Buddy" in data["headline"]


def test_index_route_renders_pet_name(monkeypatch, tmp_path):
    monkeypatch.setattr(web_app, "STATE_FILE", str(tmp_path / "pet_state.json"))
    monkeypatch.setattr(web_app, "pet", Pet(name="Mochi", hunger=30, mood=60, energy=90))

    res = web_app.app.test_client().get("/")

    assert res.status_code == 200
    assert b"Mochi" in res.data


# ---------------------------------------------------------------------------
# Final Sprint (extra) — Cleanliness: ความสะอาดลดลงตามเวลา + อาบน้ำ + อารมณ์เสียเมื่อสกปรกมาก
# ---------------------------------------------------------------------------
def test_apply_neglect_decay_reduces_cleanliness_over_time(monkeypatch, tmp_path):
    monkeypatch.setattr(web_app, "STATE_FILE", str(tmp_path / "pet_state.json"))
    monkeypatch.setattr(web_app, "cleanliness", 100)
    monkeypatch.setattr(web_app, "pet", Pet(name="Buddy", hunger=30, mood=50, energy=80))
    now = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    monkeypatch.setattr(web_app, "last_updated", now - timedelta(minutes=40))

    web_app.apply_neglect_decay(now=now)

    # 40 นาที: cleanliness -5 (ทุก 8 นาที -1)
    assert web_app.cleanliness == 95


def test_apply_neglect_decay_drops_mood_when_too_dirty(monkeypatch, tmp_path):
    monkeypatch.setattr(web_app, "STATE_FILE", str(tmp_path / "pet_state.json"))
    monkeypatch.setattr(web_app, "cleanliness", 32)
    monkeypatch.setattr(web_app, "pet", Pet(name="Buddy", hunger=10, mood=50, energy=90))
    now = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    # ปล่อยไว้ 40 นาที -> cleanliness -5 (32->27, ต่ำกว่าเกณฑ์สกปรก 30) -> mood ต้องลดลงด้วย
    monkeypatch.setattr(web_app, "last_updated", now - timedelta(minutes=40))

    web_app.apply_neglect_decay(now=now)

    assert web_app.cleanliness == 27
    assert web_app.pet.mood == 47


def test_api_action_bathe_increases_cleanliness_and_mood(monkeypatch, tmp_path):
    monkeypatch.setattr(web_app, "STATE_FILE", str(tmp_path / "pet_state.json"))
    monkeypatch.setattr(web_app, "cleanliness", 20)
    monkeypatch.setattr(web_app, "pet", Pet(name="Buddy", hunger=30, mood=50, energy=80))
    monkeypatch.setattr(web_app, "last_updated", datetime.now(timezone.utc))

    res = _post_action(web_app.app.test_client(), "bathe")

    assert res.status_code == 200
    data = res.get_json()
    assert data["cleanliness"] == 60
    assert data["mood"] == 55
    assert data["dirty"] is False


def test_api_action_play_dirties_pet(monkeypatch, tmp_path):
    monkeypatch.setattr(web_app, "STATE_FILE", str(tmp_path / "pet_state.json"))
    monkeypatch.setattr(web_app, "cleanliness", 100)
    monkeypatch.setattr(web_app, "pet", Pet(name="Buddy", hunger=30, mood=50, energy=80))
    monkeypatch.setattr(web_app, "last_updated", datetime.now(timezone.utc))

    res = _post_action(web_app.app.test_client(), "play")

    assert res.status_code == 200
    assert res.get_json()["cleanliness"] == 90


# ---------------------------------------------------------------------------
# Final Sprint (extra) — กลางวัน/กลางคืน: เล่นตอนดึกได้ mood เพิ่มแค่ครึ่งเดียว
# ---------------------------------------------------------------------------
def test_api_action_play_at_night_gives_half_mood_gain(monkeypatch, tmp_path):
    monkeypatch.setattr(web_app, "STATE_FILE", str(tmp_path / "pet_state.json"))
    monkeypatch.setattr(web_app, "cleanliness", 100)
    monkeypatch.setattr(web_app, "pet", Pet(name="Buddy", hunger=30, mood=50, energy=80))
    monkeypatch.setattr(web_app, "last_updated", datetime.now(timezone.utc))
    monkeypatch.setattr(web_app, "is_night_time", lambda now=None: True)

    res = _post_action(web_app.app.test_client(), "play")

    assert res.status_code == 200
    data = res.get_json()
    # ปกติ play() ให้ mood +15 (50->65) แต่ตอนกลางคืนได้แค่ครึ่งเดียว -> +7 (50->57)
    assert data["mood"] == 57
    assert "ง่วง" in data["message"]


def test_is_night_time_true_for_midnight_local():
    now = datetime(2026, 1, 1, 0, 0, 0, tzinfo=timezone.utc).astimezone().replace(hour=0)
    assert web_app.is_night_time(now.astimezone(timezone.utc)) is True


def test_is_night_time_false_for_noon_local():
    now = datetime(2026, 1, 1, 0, 0, 0, tzinfo=timezone.utc).astimezone().replace(hour=12)
    assert web_app.is_night_time(now.astimezone(timezone.utc)) is False


# ---------------------------------------------------------------------------
# Final Sprint (extra) — โตขึ้นตามเวลา: baby -> teen -> adult
# ---------------------------------------------------------------------------
def test_life_stage_for_thresholds():
    assert web_app.life_stage_for(0) == "baby"
    assert web_app.life_stage_for(web_app.STAGE_TEEN_POINTS - 1) == "baby"
    assert web_app.life_stage_for(web_app.STAGE_TEEN_POINTS) == "teen"
    assert web_app.life_stage_for(web_app.STAGE_ADULT_POINTS - 1) == "teen"
    assert web_app.life_stage_for(web_app.STAGE_ADULT_POINTS) == "adult"


def test_care_quality_perfect_care_is_one(monkeypatch):
    monkeypatch.setattr(web_app, "pet", Pet(name="Buddy", hunger=0, mood=100, energy=100))
    monkeypatch.setattr(web_app, "cleanliness", 100)
    assert web_app.care_quality() == 1.0


def test_care_quality_worst_care_is_zero(monkeypatch):
    monkeypatch.setattr(web_app, "pet", Pet(name="Buddy", hunger=100, mood=0, energy=0))
    monkeypatch.setattr(web_app, "cleanliness", 0)
    assert web_app.care_quality() == 0.0


def test_apply_growth_scales_with_care_quality(monkeypatch):
    monkeypatch.setattr(web_app, "pet", Pet(name="Buddy", hunger=0, mood=100, energy=100))
    monkeypatch.setattr(web_app, "cleanliness", 100)
    monkeypatch.setattr(web_app, "growth_points", 0.0)

    web_app.apply_growth(100)  # 100 นาที คุณภาพเต็ม 1.0 -> คูณ 1.5 เท่า

    assert web_app.growth_points == 150.0


def test_apply_growth_still_grows_slowly_when_care_is_worst(monkeypatch):
    monkeypatch.setattr(web_app, "pet", Pet(name="Buddy", hunger=100, mood=0, energy=0))
    monkeypatch.setattr(web_app, "cleanliness", 0)
    monkeypatch.setattr(web_app, "growth_points", 0.0)

    web_app.apply_growth(100)  # คุณภาพ 0.0 -> คูณแค่ 0.5 เท่า (ยังโตอยู่ แต่ช้าลง)

    assert web_app.growth_points == 50.0


def test_apply_neglect_decay_accumulates_growth_points(monkeypatch, tmp_path):
    monkeypatch.setattr(web_app, "STATE_FILE", str(tmp_path / "pet_state.json"))
    monkeypatch.setattr(web_app, "cleanliness", 100)
    monkeypatch.setattr(web_app, "growth_points", 0.0)
    monkeypatch.setattr(web_app, "pet", Pet(name="Buddy", hunger=0, mood=100, energy=100))
    now = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    monkeypatch.setattr(web_app, "last_updated", now - timedelta(minutes=100))

    web_app.apply_neglect_decay(now=now)

    assert web_app.growth_points > 0


def test_state_payload_includes_lifelike_fields(monkeypatch):
    monkeypatch.setattr(web_app, "pet", Pet(name="Buddy", hunger=30, mood=60, energy=80))
    monkeypatch.setattr(web_app, "cleanliness", 100)
    monkeypatch.setattr(web_app, "growth_points", 0.0)

    payload = web_app.state_payload()

    assert payload["cleanliness"] == 100
    assert payload["dirty"] is False
    assert payload["life_stage"] == "baby"
    assert "is_night" in payload
    assert "growth_points" in payload


# ---------------------------------------------------------------------------
# Final Sprint (extra) — ตั้งชื่อได้: /api/rename
# ---------------------------------------------------------------------------
def test_api_rename_success(monkeypatch, tmp_path):
    monkeypatch.setattr(web_app, "STATE_FILE", str(tmp_path / "pet_state.json"))
    monkeypatch.setattr(web_app, "pet", Pet(name="Buddy", hunger=30, mood=50, energy=80))
    monkeypatch.setattr(web_app, "last_updated", datetime.now(timezone.utc))

    res = web_app.app.test_client().post(
        "/api/rename", json={"name": "Mochi"}, content_type="application/json"
    )

    assert res.status_code == 200
    data = res.get_json()
    assert data["name"] == "Mochi"
    assert web_app.pet.name == "Mochi"


def test_api_rename_empty_name_returns_400(monkeypatch, tmp_path):
    monkeypatch.setattr(web_app, "STATE_FILE", str(tmp_path / "pet_state.json"))
    monkeypatch.setattr(web_app, "pet", Pet(name="Buddy", hunger=30, mood=50, energy=80))
    monkeypatch.setattr(web_app, "last_updated", datetime.now(timezone.utc))

    res = web_app.app.test_client().post(
        "/api/rename", json={"name": "   "}, content_type="application/json"
    )

    assert res.status_code == 400


def test_api_rename_too_long_returns_400(monkeypatch, tmp_path):
    monkeypatch.setattr(web_app, "STATE_FILE", str(tmp_path / "pet_state.json"))
    monkeypatch.setattr(web_app, "pet", Pet(name="Buddy", hunger=30, mood=50, energy=80))
    monkeypatch.setattr(web_app, "last_updated", datetime.now(timezone.utc))

    res = web_app.app.test_client().post(
        "/api/rename", json={"name": "x" * 30}, content_type="application/json"
    )

    assert res.status_code == 400


# ---------------------------------------------------------------------------
# Final Sprint (extra) — คุยกับสัตว์เลี้ยง: /api/chat (mock gemini_client เพื่อไม่ต้องพึ่งอินเทอร์เน็ตจริง)
# ---------------------------------------------------------------------------
def test_api_chat_returns_reply_from_gemini_client(monkeypatch, tmp_path):
    monkeypatch.setattr(web_app, "STATE_FILE", str(tmp_path / "pet_state.json"))
    monkeypatch.setattr(web_app, "pet", Pet(name="Buddy", hunger=30, mood=50, energy=80))
    monkeypatch.setattr(web_app, "last_updated", datetime.now(timezone.utc))
    monkeypatch.setattr(
        web_app.gemini_client, "get_reply", lambda *a, **k: ("หวัดดีจ้า!", "fallback")
    )

    res = web_app.app.test_client().post(
        "/api/chat", json={"message": "สวัสดี"}, content_type="application/json"
    )

    assert res.status_code == 200
    data = res.get_json()
    assert data["reply"] == "หวัดดีจ้า!"
    assert data["source"] == "fallback"


def test_api_chat_empty_message_returns_400(monkeypatch, tmp_path):
    monkeypatch.setattr(web_app, "STATE_FILE", str(tmp_path / "pet_state.json"))
    monkeypatch.setattr(web_app, "pet", Pet(name="Buddy", hunger=30, mood=50, energy=80))
    monkeypatch.setattr(web_app, "last_updated", datetime.now(timezone.utc))

    res = web_app.app.test_client().post(
        "/api/chat", json={"message": "  "}, content_type="application/json"
    )

    assert res.status_code == 400


# ---------------------------------------------------------------------------
# บั๊กที่เจอ 4/10/69: เปิด/รีเฟรชถี่กว่ารอบการลด -> เศษถูกปัดทิ้งทุกครั้ง -> energy ไม่ลดเลย
# ---------------------------------------------------------------------------
def _setup_decay_state(monkeypatch, tmp_path, start):
    monkeypatch.setattr(web_app, "STATE_FILE", str(tmp_path / "pet_state.json"))
    monkeypatch.setattr(web_app, "cleanliness", 100)
    monkeypatch.setattr(web_app, "pet", Pet(name="Buddy", hunger=0, mood=50, energy=100))
    monkeypatch.setattr(web_app, "last_updated", start)


def test_decay_accumulates_when_polled_more_often_than_decay_interval(monkeypatch, tmp_path):
    start = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    _setup_decay_state(monkeypatch, tmp_path, start)

    # จำลองเปิด/รีเฟรช/กดปุ่มทุก 5 นาที ต่อเนื่อง 60 นาที (ถี่กว่ารอบลด energy 10 นาที)
    for step in range(1, 13):
        web_app.apply_neglect_decay(now=start + timedelta(minutes=5 * step))

    # ต้องได้ผลเท่ากับการปล่อยไว้ 60 นาทีรวดเดียว: energy -6, hunger +24, cleanliness -7 (7.5 ปัดลง)
    assert web_app.pet.energy == 94
    assert web_app.pet.hunger == 24
    assert web_app.cleanliness == 93


def test_decay_accumulates_even_when_polled_every_minute(monkeypatch, tmp_path):
    start = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    _setup_decay_state(monkeypatch, tmp_path, start)

    for step in range(1, 61):  # ทุก 1 นาที ครบ 60 นาที
        web_app.apply_neglect_decay(now=start + timedelta(minutes=step))

    assert web_app.pet.energy == 94
    assert web_app.pet.hunger == 24


def test_decay_carry_is_discarded_when_baseline_time_is_edited(monkeypatch, tmp_path):
    """แก้ last_updated ในไฟล์ (วิธีที่ใช้ซ้อม demo) ต้องคำนวณจากเวลาที่ย้อนไปล้วนๆ ไม่ปนเศษเก่า"""
    start = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    _setup_decay_state(monkeypatch, tmp_path, start)
    web_app.apply_neglect_decay(now=start + timedelta(minutes=7))  # สร้างเศษค้างไว้ก่อน

    now = start + timedelta(hours=5)
    monkeypatch.setattr(web_app, "pet", Pet(name="Buddy", hunger=0, mood=50, energy=100))
    monkeypatch.setattr(web_app, "last_updated", now - timedelta(minutes=30))  # เหมือนแก้เวลาในไฟล์
    web_app.apply_neglect_decay(now=now)

    assert web_app.pet.hunger == 12   # 30 นาที x 0.4 พอดี ไม่มีเศษเก่าบวกเข้ามา
    assert web_app.pet.energy == 97   # 30 นาที x 0.1 = 3 พอดี


def test_split_whole_handles_floating_point_error():
    assert web_app._split_whole(0.9999999999999999) == (1, 0.0)
    whole, rest = web_app._split_whole(2.5)
    assert whole == 2 and rest == 0.5


# ---------------------------------------------------------------------------
# 4/10/69 — save_pet แบบ atomic + หน้าเว็บอัปเดตค่าสถานะอัตโนมัติ
# ---------------------------------------------------------------------------
def test_save_pet_is_atomic_and_leaves_no_temp_file(monkeypatch, tmp_path):
    import json

    state_file = tmp_path / "pet_state.json"
    monkeypatch.setattr(web_app, "STATE_FILE", str(state_file))
    for hunger in (10, 20, 30):
        web_app.save_pet(Pet(name="Mochi", hunger=hunger))
        assert json.loads(state_file.read_text(encoding="utf-8"))["hunger"] == hunger
    assert [f.name for f in tmp_path.iterdir()] == ["pet_state.json"]


def test_save_pet_failure_keeps_old_file_intact(monkeypatch, tmp_path):
    import json

    state_file = tmp_path / "pet_state.json"
    monkeypatch.setattr(web_app, "STATE_FILE", str(state_file))
    web_app.save_pet(Pet(name="Mochi", hunger=11))

    def boom(src, dst):
        raise OSError("disk error (จำลอง)")

    monkeypatch.setattr(web_app.os, "replace", boom)
    web_app.save_pet(Pet(name="Mochi", hunger=99))  # ต้องไม่ crash

    assert json.loads(state_file.read_text(encoding="utf-8"))["hunger"] == 11
    assert [f.name for f in tmp_path.iterdir()] == ["pet_state.json"]


def test_frontend_auto_refresh_guard():
    """ตัวเฝ้าระวังแบบง่าย (ไม่ใช่ behaviour test): ต้องมีการโพลทุก 30 วิ และข้ามเมื่อแท็บถูกซ่อน"""
    js_path = os.path.join(os.path.dirname(__file__), "..", "web", "static", "js", "main.js")
    with open(js_path, encoding="utf-8") as f:
        js = f.read()
    assert "AUTO_REFRESH_MS = 30000" in js
    assert "setInterval(pollState, AUTO_REFRESH_MS)" in js
    assert "document.hidden" in js


# ---------------------------------------------------------------------------
# 4/10/69 — แถบ + ตัวเลขความคืบหน้าการเติบโต (growth_progress)
# ---------------------------------------------------------------------------
def test_growth_progress_baby_halfway_to_teen():
    g = web_app.growth_progress(web_app.STAGE_TEEN_POINTS / 2)
    assert g["start"] == 0 and g["target"] == web_app.STAGE_TEEN_POINTS
    assert g["percent"] == 50.0
    assert g["next_label"] == web_app._STAGE_LABEL["teen"]


def test_growth_progress_teen_range_starts_from_teen_threshold():
    g = web_app.growth_progress(web_app.STAGE_TEEN_POINTS)
    assert g["start"] == web_app.STAGE_TEEN_POINTS
    assert g["target"] == web_app.STAGE_ADULT_POINTS
    assert g["percent"] == 0.0
    assert g["next_label"] == web_app._STAGE_LABEL["adult"]


def test_growth_progress_adult_is_full_without_target():
    g = web_app.growth_progress(web_app.STAGE_ADULT_POINTS + 999)
    assert g["target"] is None and g["next_label"] is None
    assert g["percent"] == 100


def test_state_payload_includes_growth_progress(monkeypatch):
    monkeypatch.setattr(web_app, "growth_points", web_app.STAGE_TEEN_POINTS + 10)
    payload = web_app.state_payload()
    assert payload["life_stage"] == "teen"
    assert payload["growth_progress"]["target"] == web_app.STAGE_ADULT_POINTS
