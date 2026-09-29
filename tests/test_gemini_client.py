"""
tests/test_gemini_client.py
Unit test สำหรับ web/gemini_client.py — คุยกับสัตว์เลี้ยงผ่าน Gemini API (Final Sprint, extra)
mock การเรียก requests.post ทั้งหมด ไม่ต้องพึ่งอินเทอร์เน็ตจริงหรือ API key จริงตอนรัน test
"""
import os
import sys
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "web"))

import gemini_client  # noqa: E402


def test_is_configured_false_without_api_key(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    assert gemini_client.is_configured() is False


def test_is_configured_true_with_api_key(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "fake-key-123")
    assert gemini_client.is_configured() is True


def test_get_reply_uses_fallback_when_no_api_key(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    reply, source = gemini_client.get_reply("Buddy", 50, 30, 80, "สวัสดี")

    assert source == "fallback"
    assert isinstance(reply, str) and reply


def test_fallback_reply_happy_mood_differs_from_sad_mood():
    happy = gemini_client._fallback_reply(90)
    sad = gemini_client._fallback_reply(10)
    assert happy in gemini_client._FALLBACK_HAPPY
    assert sad in gemini_client._FALLBACK_SAD


@patch("gemini_client.requests")
def test_get_reply_success_returns_gemini_text(mock_requests, monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "fake-key-123")
    mock_resp = MagicMock()
    mock_resp.raise_for_status.return_value = None
    mock_resp.json.return_value = {
        "candidates": [{"content": {"parts": [{"text": "หวัดดีเจ้าของ! วันนี้สนุกมากเลย"}]}}]
    }
    mock_requests.post.return_value = mock_resp
    mock_requests.exceptions = __import__("requests").exceptions

    reply, source = gemini_client.get_reply("Buddy", 70, 20, 90, "เป็นไงบ้าง")

    assert source == "gemini"
    assert reply == "หวัดดีเจ้าของ! วันนี้สนุกมากเลย"


@patch("gemini_client.requests")
def test_get_reply_timeout_falls_back(mock_requests, monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "fake-key-123")
    real_requests = __import__("requests")
    mock_requests.exceptions = real_requests.exceptions
    mock_requests.post.side_effect = real_requests.exceptions.Timeout("timed out")

    reply, source = gemini_client.get_reply("Buddy", 50, 30, 80, "หวัดดี")

    assert source == "fallback"
    assert isinstance(reply, str) and reply


@patch("gemini_client.requests")
def test_get_reply_connection_error_falls_back(mock_requests, monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "fake-key-123")
    real_requests = __import__("requests")
    mock_requests.exceptions = real_requests.exceptions
    mock_requests.post.side_effect = real_requests.exceptions.ConnectionError("no internet")

    reply, source = gemini_client.get_reply("Buddy", 50, 30, 80, "หวัดดี")

    assert source == "fallback"


@patch("gemini_client.requests")
def test_get_reply_bad_payload_falls_back(mock_requests, monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "fake-key-123")
    real_requests = __import__("requests")
    mock_requests.exceptions = real_requests.exceptions
    mock_resp = MagicMock()
    mock_resp.raise_for_status.return_value = None
    mock_resp.json.return_value = {"unexpected": "shape"}
    mock_requests.post.return_value = mock_resp

    reply, source = gemini_client.get_reply("Buddy", 50, 30, 80, "หวัดดี")

    assert source == "fallback"
    assert isinstance(reply, str) and reply


@patch("gemini_client.requests")
def test_get_reply_empty_text_falls_back(mock_requests, monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "fake-key-123")
    real_requests = __import__("requests")
    mock_requests.exceptions = real_requests.exceptions
    mock_resp = MagicMock()
    mock_resp.raise_for_status.return_value = None
    mock_resp.json.return_value = {"candidates": [{"content": {"parts": [{"text": "   "}]}}]}
    mock_requests.post.return_value = mock_resp

    reply, source = gemini_client.get_reply("Buddy", 50, 30, 80, "หวัดดี")

    assert source == "fallback"


def test_build_prompt_includes_pet_name_and_message():
    prompt = gemini_client._build_prompt("Buddy", 60, 20, 90, "วันนี้เป็นไงบ้าง")
    assert "Buddy" in prompt
    assert "วันนี้เป็นไงบ้าง" in prompt
