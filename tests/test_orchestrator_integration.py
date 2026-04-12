"""Tests for agent-CLI integration: context builder + orchestrator wiring."""

from prep_agent.agents.context import build_agent_context
from prep_agent.agents.orchestrator import Orchestrator


# ------------------------------------------------------------------
# Context builder
# ------------------------------------------------------------------


class TestBuildAgentContext:
    def test_basic_context_shape(self):
        tracker_state = {
            "current_day": 5,
            "total_days": 50,
            "streak": 3,
            "days": [
                {"day_num": i, "status": "done" if i <= 4 else "pending", "topic": f"T{i}"}
                for i in range(1, 51)
            ],
            "tracks": [{"id": "t1", "name": "Track 1", "status": "in_progress"}],
            "content": [],
            "quiz_history": [],
        }
        config = {
            "strengths": ["Python", "AWS"],
            "gaps": [{"id": "g1", "topic": "Kubernetes"}],
        }

        ctx = build_agent_context(tracker_state, config)

        assert ctx["total_days"] == 50
        assert ctx["current_day"] == 5
        assert ctx["days_done"] == 4
        assert ctx["progress_pct"] == 8.0
        assert ctx["streak"] == 3
        assert ctx["strengths"] == ["Python", "AWS"]
        assert len(ctx["gaps"]) == 1
        assert ctx["tracks"][0]["name"] == "Track 1"

    def test_quiz_analysis(self):
        tracker_state = {
            "current_day": 10,
            "total_days": 50,
            "streak": 0,
            "days": [],
            "tracks": [],
            "content": [],
            "quiz_history": [
                {"topic": "IAM", "score": 3, "total": 10},
                {"topic": "IAM", "score": 4, "total": 10},
                {"topic": "K8s", "score": 9, "total": 10},
                {"topic": "K8s", "score": 8, "total": 10},
            ],
        }

        ctx = build_agent_context(tracker_state, {})

        assert "IAM" in ctx["weak_topics"]
        assert "K8s" in ctx["strong_topics"]
        assert ctx["quiz_avg"] > 0

    def test_today_entry_sets_topic(self):
        tracker_state = {"days": [], "current_day": 1, "total_days": 10, "streak": 0}
        today = {"topic": "OWASP LLM Top 10", "day_num": 5}

        ctx = build_agent_context(tracker_state, {}, today_entry=today)

        assert ctx["topic"] == "OWASP LLM Top 10"
        assert ctx["today_entry"]["day_num"] == 5

    def test_empty_state(self):
        ctx = build_agent_context({}, {})

        assert ctx["total_days"] == 0
        assert ctx["days_done"] == 0
        assert ctx["progress_pct"] == 0.0
        assert ctx["weak_topics"] == []
        assert ctx["strong_topics"] == []
        assert ctx["quiz_avg"] == 0.0


# ------------------------------------------------------------------
# Orchestrator integration
# ------------------------------------------------------------------


class TestOrchestratorIntegration:
    def _make_context(self, **overrides):
        base = {
            "total_days": 60,
            "current_day": 10,
            "days_done": 9,
            "progress_pct": 15.0,
            "streak": 3,
            "quiz_history": [],
            "quiz_avg": 0,
            "weak_topics": [],
            "strong_topics": [],
            "tracks": [],
            "content": [],
            "gaps": [],
            "strengths": [],
            "today_entry": {"topic": "Cloud Security", "morning_focus": "Study", "evening_focus": "Practice"},
            "topic": "Cloud Security",
        }
        base.update(overrides)
        return base

    def test_today_returns_plan(self):
        o = Orchestrator()
        result = o.handle_session("today", self._make_context())

        assert result["session_type"] == "today"
        assert "plan" in result
        assert "topic" in result["plan"]

    def test_study_returns_session(self):
        o = Orchestrator()
        result = o.handle_session("study", self._make_context())

        assert result["session_type"] == "study"
        assert "session" in result
        assert "planner" in result["agents_invoked"]
        assert "tutor" in result["agents_invoked"]

    def test_quiz_returns_difficulty(self):
        o = Orchestrator()
        ctx = self._make_context(
            quiz_history=[
                {"score": 9, "total": 10},
                {"score": 8, "total": 10},
            ]
        )
        result = o.handle_session("quiz", ctx)

        assert result["session_type"] == "quiz"
        assert "quiz" in result
        assert "difficulty" in result["quiz"]

    def test_review_returns_recommendations(self):
        o = Orchestrator()
        ctx = self._make_context(streak=0)
        result = o.handle_session("review", ctx)

        assert result["session_type"] == "review"
        assert "review" in result
        recs = result["review"].get("recommendations", [])
        assert isinstance(recs, list)

    def test_unknown_session_type(self):
        o = Orchestrator()
        result = o.handle_session("invalid", {})
        assert "error" in result
