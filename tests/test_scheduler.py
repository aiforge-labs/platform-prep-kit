"""Tests for reminder scheduler."""
import os
import tempfile
import json
import sys
import pytest


class TestScheduler:
    def test_save_and_load_state(self):
        from prep_agent.integrations.scheduler import Scheduler
        tmpdir = tempfile.mkdtemp()
        scheduler = Scheduler(prep_dir=tmpdir)
        scheduler._save_state({
            "installed": True,
            "paused": False,
            "morning_time": "07:00",
            "evening_time": "19:00",
        })
        state = scheduler._load_state()
        assert state["installed"] is True
        assert state["morning_time"] == "07:00"

    def test_initial_state(self):
        from prep_agent.integrations.scheduler import Scheduler
        tmpdir = tempfile.mkdtemp()
        scheduler = Scheduler(prep_dir=tmpdir)
        status = scheduler.get_status()
        assert status["installed"] is False

    def test_pause_state(self):
        from prep_agent.integrations.scheduler import Scheduler
        tmpdir = tempfile.mkdtemp()
        scheduler = Scheduler(prep_dir=tmpdir)
        scheduler._save_state({"installed": True, "paused": False, "morning_time": "07:00", "evening_time": "19:00"})
        scheduler.pause()
        assert scheduler.is_paused() is True

    def test_resume_state(self):
        from prep_agent.integrations.scheduler import Scheduler
        tmpdir = tempfile.mkdtemp()
        scheduler = Scheduler(prep_dir=tmpdir)
        scheduler._save_state({"installed": True, "paused": True, "morning_time": "07:00", "evening_time": "19:00"})
        scheduler.resume()
        assert scheduler.is_paused() is False


class TestNotifier:
    def test_is_available(self):
        from prep_agent.integrations.notifier import Notifier
        # Should return True on macOS/Linux, may vary on CI
        result = Notifier.is_available()
        assert isinstance(result, bool)

    def test_build_morning_notification(self):
        from prep_agent.integrations.notifier import build_morning_notification
        tracker_data = {
            "current_day": 5,
            "total_days": 42,
            "today_topic": "OWASP LLM Top 10",
            "streak": 4,
            "current_week": 1,
        }
        title, message = build_morning_notification(tracker_data)
        assert "Day 5" in title or "Day 5" in message
        assert len(title) > 0
        assert len(message) > 0

    def test_build_evening_notification(self):
        from prep_agent.integrations.notifier import build_evening_notification
        tracker_data = {
            "current_day": 5,
            "total_days": 42,
            "evening_focus": "Write vulnerability summaries",
            "streak": 4,
        }
        title, message = build_evening_notification(tracker_data)
        assert len(title) > 0

    def test_build_weekly_summary(self):
        from prep_agent.integrations.notifier import build_weekly_summary
        tracker_data = {
            "current_week": 1,
            "total_weeks": 8,
            "days_done": 5,
            "total_days": 42,
            "quiz_avg": 78,
        }
        title, message = build_weekly_summary(tracker_data)
        assert "Week" in title or "Week" in message
