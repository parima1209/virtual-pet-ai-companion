"""
tests/test_web_app.py
Unit test สำหรับ logic ฝั่ง Flask web app (web/app.py) โดยเฉพาะฟังก์ชันเลือกสไปรต์
รัน: pytest
"""

import os
import sys
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
