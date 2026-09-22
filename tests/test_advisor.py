"""
tests/test_advisor.py
Unit test สำหรับ web/advisor.py — "AI Advisor" (rule-based) ของ Final Sprint
รัน: pytest
"""
import os
import sys
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "web"))

import advisor  # noqa: E402
from src.pet import Pet  # noqa: E402


def test_wellbeing_score_full_health_is_100():
    p = Pet(name="Buddy", hunger=0, mood=100, energy=100)
    assert advisor.wellbeing_score(p) == 100


def test_wellbeing_score_worst_case_is_0():
    p = Pet(name="Buddy", hunger=100, mood=0, energy=0)
    assert advisor.wellbeing_score(p) == 0


def test_wellbeing_score_weights_mood_most():
    # mood สูงสุดแต่ hunger/energy แย่สุด ควรยังได้คะแนนมากกว่าครึ่งเพราะ mood มีน้ำหนัก 0.5
    p = Pet(name="Buddy", hunger=100, mood=100, energy=0)
    assert advisor.wellbeing_score(p) == 50


def test_mood_forecast_levels():
    assert advisor.mood_forecast(Pet(name="B", hunger=0, mood=100, energy=100)) == "แนวโน้มดีมาก"
    assert advisor.mood_forecast(Pet(name="B", hunger=40, mood=55, energy=55)) == "แนวโน้มปกติ"
    assert advisor.mood_forecast(Pet(name="B", hunger=70, mood=25, energy=30)) == "แนวโน้มเริ่มแย่ลง"
    assert advisor.mood_forecast(Pet(name="B", hunger=100, mood=0, energy=0)) == "แนวโน้มวิกฤต"


def test_recommend_action_picks_most_urgent_need():
    # hunger สูงสุด (ต้องการ feed มากสุด)
    p = Pet(name="Buddy", hunger=90, mood=60, energy=70)
    assert advisor.recommend_action(p) == "feed"

    # energy ต่ำสุด (ต้องการ rest มากสุด)
    p2 = Pet(name="Buddy", hunger=20, mood=60, energy=10)
    assert advisor.recommend_action(p2) == "rest"

    # mood ต่ำสุด (ต้องการ play มากสุด)
    p3 = Pet(name="Buddy", hunger=20, mood=10, energy=70)
    assert advisor.recommend_action(p3) == "play"


def test_recommend_action_suggests_interact_when_all_good():
    p = Pet(name="Buddy", hunger=10, mood=90, energy=90)
    assert advisor.recommend_action(p) == "interact"


def test_recent_interaction_count_filters_by_time_window():
    now = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    history = [
        {"timestamp": (now - timedelta(minutes=5)).isoformat()},
        {"timestamp": (now - timedelta(minutes=20)).isoformat()},
        {"timestamp": (now - timedelta(minutes=45)).isoformat()},  # นอกช่วง 30 นาที
        {"timestamp": "not-a-date"},  # ข้อมูลเสีย ต้องไม่ทำให้ crash
    ]
    assert advisor.recent_interaction_count(history, minutes=30, now=now) == 2


def test_recent_interaction_count_empty_history_returns_zero():
    assert advisor.recent_interaction_count([], minutes=30) == 0


def test_generate_advice_returns_all_expected_fields():
    p = Pet(name="Buddy", hunger=95, mood=40, energy=50)
    result = advisor.generate_advice(p, history_items=[])

    assert set(result.keys()) == {
        "score", "forecast", "recommended_action", "recommended_label",
        "recent_interactions_30min", "headline",
    }
    assert result["recommended_action"] == "feed"
    assert "Buddy" in result["headline"]


def test_generate_advice_suggests_interact_message_when_no_recent_interaction():
    p = Pet(name="Buddy", hunger=10, mood=90, energy=90)
    result = advisor.generate_advice(p, history_items=[])
    assert result["recommended_action"] == "interact"
    assert "ยังไม่ได้เจอเพื่อนใหม่" in result["headline"]
