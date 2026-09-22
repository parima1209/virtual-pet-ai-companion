"""
tests/test_web_app.py
Unit test สำหรับ logic ฝั่ง Flask web app (web/app.py) โดยเฉพาะฟังก์ชันเลือกสไปรต์
รัน: pytest
"""

import os
import sys
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "web"))

import app as web_app  # noqa: E402
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
    fresh_pet = Pet(name="Buddy", hunger=30, mood=50, energy=80)
    monkeypatch.setattr(web_app, "pet", fresh_pet)
    now = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    monkeypatch.setattr(web_app, "last_updated", now - timedelta(minutes=30))

    web_app.apply_neglect_decay(now=now)

    # 30 นาที: hunger +6 (ทุก 5 นาที +1), energy -3 (ทุก 10 นาที -1)
    assert web_app.pet.hunger == 36
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
    fresh_pet = Pet(name="Buddy", hunger=85, mood=50, energy=80)
    monkeypatch.setattr(web_app, "pet", fresh_pet)
    now = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    # ปล่อยไว้ 60 นาที -> hunger +12 (85->97, ทะลุเกณฑ์ 90) -> mood ต้องลดลงด้วย
    monkeypatch.setattr(web_app, "last_updated", now - timedelta(minutes=60))

    web_app.apply_neglect_decay(now=now)

    assert web_app.pet.hunger == 97
    assert web_app.pet.mood == 45


def test_apply_neglect_decay_caps_at_24_hours(monkeypatch, tmp_path):
    monkeypatch.setattr(web_app, "STATE_FILE", str(tmp_path / "pet_state.json"))
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
    # 50 นาที: hunger +10 (10->20), energy -5 (100->95)
    assert data["hunger"] == 20
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
