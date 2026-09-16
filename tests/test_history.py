"""
tests/test_history.py
Unit test สำหรับ web/history.py — Data Access Layer + ฟังก์ชัน search/filter/sort
ของ "ประวัติการโต้ตอบ" (ขอบเขต Sprint 2)
รัน: pytest
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "web"))

import history  # noqa: E402


def test_load_history_returns_empty_list_when_no_file(tmp_path, monkeypatch):
    monkeypatch.setattr(history, "HISTORY_FILE", str(tmp_path / "interaction_history.json"))
    assert history.load_history() == []


def test_save_and_load_history_round_trip(tmp_path, monkeypatch):
    monkeypatch.setattr(history, "HISTORY_FILE", str(tmp_path / "interaction_history.json"))
    data = [{"timestamp": "2026-01-01T00:00:00", "source": "Dog API", "kind": "image", "content": "x"}]
    history.save_history(data)
    assert history.load_history() == data


def test_load_history_recovers_from_corrupt_file(tmp_path, monkeypatch):
    path = tmp_path / "interaction_history.json"
    path.write_text("not valid json", encoding="utf-8")
    monkeypatch.setattr(history, "HISTORY_FILE", str(path))
    assert history.load_history() == []


def test_add_entry_appends_with_timestamp(tmp_path, monkeypatch):
    monkeypatch.setattr(history, "HISTORY_FILE", str(tmp_path / "interaction_history.json"))
    entry = history.add_entry("Dog API", "image", "https://example.com/dog.jpg")
    assert entry["source"] == "Dog API"
    assert entry["kind"] == "image"
    assert "timestamp" in entry
    assert history.load_history() == [entry]


SAMPLE = [
    {"timestamp": "2026-01-01T10:00:00", "source": "Dog API", "kind": "image",
     "content": "https://a/dog1.jpg"},
    {"timestamp": "2026-01-02T10:00:00", "source": "Cat Facts API", "kind": "fact",
     "content": "Cats sleep a lot."},
    {"timestamp": "2026-01-03T10:00:00", "source": "Dog API", "kind": "image",
     "content": "https://a/dog2.jpg"},
]


def test_search_history_matches_substring_case_insensitive():
    result = history.search_history(SAMPLE, "SLEEP")
    assert len(result) == 1
    assert result[0]["source"] == "Cat Facts API"


def test_search_history_empty_query_returns_all():
    assert history.search_history(SAMPLE, "") == SAMPLE


def test_search_history_no_match_returns_empty():
    assert history.search_history(SAMPLE, "elephant") == []


def test_filter_history_by_source():
    result = history.filter_history(SAMPLE, source="Dog API")
    assert len(result) == 2
    assert all(item["source"] == "Dog API" for item in result)


def test_filter_history_by_kind():
    result = history.filter_history(SAMPLE, kind="fact")
    assert len(result) == 1
    assert result[0]["kind"] == "fact"


def test_filter_history_by_source_and_kind_combined():
    result = history.filter_history(SAMPLE, source="Dog API", kind="image")
    assert len(result) == 2


def test_filter_history_no_filters_returns_all():
    assert history.filter_history(SAMPLE) == SAMPLE


def test_sort_history_desc_newest_first():
    result = history.sort_history(SAMPLE, order="desc")
    assert [item["timestamp"] for item in result] == [
        "2026-01-03T10:00:00", "2026-01-02T10:00:00", "2026-01-01T10:00:00",
    ]


def test_sort_history_asc_oldest_first():
    result = history.sort_history(SAMPLE, order="asc")
    assert [item["timestamp"] for item in result] == [
        "2026-01-01T10:00:00", "2026-01-02T10:00:00", "2026-01-03T10:00:00",
    ]
