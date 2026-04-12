"""Tests for the multi-agent system."""

from __future__ import annotations

import pytest


# ---------------------------------------------------------------------------
# BaseAgent ReAct loop
# ---------------------------------------------------------------------------


class TestBaseAgentReActLoop:
    """Verify the observe -> reason -> act -> evaluate loop."""

    def test_react_loop_runs_all_phases(self):
        """ReAct loop should execute observe, reason, act, evaluate in order."""
        from prep_agent.agents.base import BaseAgent

        call_order: list[str] = []

        class TrackedAgent(BaseAgent):
            def observe(self, context):
                call_order.append("observe")
                return context

            def reason(self, observations):
                call_order.append("reason")
                return {"action": "test", "params": {}, "reasoning": "test"}

            def act(self, action, params):
                call_order.append("act")
                return {"result": "ok", "success": True, "message": "done"}

            def evaluate(self, result):
                call_order.append("evaluate")
                return {"satisfied": True, "feedback": "", "next_action": None}

        agent = TrackedAgent("test")
        result = agent.run({"input": "hello"})

        assert call_order == ["observe", "reason", "act", "evaluate"]
        assert result["agent"] == "test"
        assert result["iterations"] == 1

    def test_react_loop_iterates_when_unsatisfied(self):
        """ReAct loop should iterate when evaluate returns unsatisfied."""
        from prep_agent.agents.base import BaseAgent

        iteration_count = 0

        class RetryAgent(BaseAgent):
            def reason(self, observations):
                return {"action": "retry", "params": {}, "reasoning": "trying again"}

            def act(self, action, params):
                nonlocal iteration_count
                iteration_count += 1
                return {
                    "result": iteration_count,
                    "success": True,
                    "message": f"attempt {iteration_count}",
                }

            def evaluate(self, result):
                # Satisfied on third attempt
                satisfied = result["result"] >= 3
                return {
                    "satisfied": satisfied,
                    "feedback": "" if satisfied else "not yet",
                    "next_action": None,
                }

        agent = RetryAgent("retry-test")
        result = agent.run({}, max_iterations=5)

        assert result["iterations"] == 3
        assert iteration_count == 3

    def test_react_loop_respects_max_iterations(self):
        """ReAct loop should stop at max_iterations even if unsatisfied."""
        from prep_agent.agents.base import BaseAgent

        class NeverSatisfiedAgent(BaseAgent):
            def reason(self, observations):
                return {"action": "loop", "params": {}, "reasoning": "still going"}

            def act(self, action, params):
                return {"result": "nope", "success": True, "message": "not done"}

            def evaluate(self, result):
                return {
                    "satisfied": False,
                    "feedback": "never done",
                    "next_action": None,
                }

        agent = NeverSatisfiedAgent("stuck")
        result = agent.run({}, max_iterations=2)

        assert result["iterations"] == 2
        assert "Max iterations reached" in result.get("note", "")


# ---------------------------------------------------------------------------
# PlannerAgent
# ---------------------------------------------------------------------------


class TestPlannerAgent:
    """Verify planner decisions based on progress context."""

    def test_detects_behind_schedule(self):
        """Planner should recommend compression when behind schedule."""
        from prep_agent.agents.planner import PlannerAgent

        planner = PlannerAgent()
        ctx = {
            "total_days": 60,
            "current_day": 45,  # 15 days left
            "progress_pct": 20,  # Only 20% done
            "weak_topics": [],
            "strong_topics": [],
            "quiz_avg": 50,
            "gaps": [{"id": "g1", "status": "pending"}],
        }
        result = planner.run(ctx)
        trace = result.get("reasoning_trace", [])
        assert len(trace) > 0
        assert trace[0]["action"] == "compress_plan"

    def test_detects_weak_topics_and_recommends_review(self):
        """Planner should add review sessions for weak topics."""
        from prep_agent.agents.planner import PlannerAgent

        planner = PlannerAgent()
        ctx = {
            "total_days": 60,
            "current_day": 20,
            "progress_pct": 50,  # On track
            "weak_topics": ["IAM Policies", "Encryption"],
            "strong_topics": ["Networking"],
            "quiz_avg": 65,
            "gaps": [],
        }
        result = planner.run(ctx)
        trace = result.get("reasoning_trace", [])
        assert trace[0]["action"] == "add_review"

    def test_continues_when_on_track(self):
        """Planner should continue as planned when everything is fine."""
        from prep_agent.agents.planner import PlannerAgent

        planner = PlannerAgent()
        ctx = {
            "total_days": 60,
            "current_day": 30,
            "progress_pct": 50,
            "weak_topics": [],
            "strong_topics": ["All"],
            "quiz_avg": 80,
            "gaps": [],
        }
        result = planner.run(ctx)
        trace = result.get("reasoning_trace", [])
        assert trace[0]["action"] == "continue"


# ---------------------------------------------------------------------------
# PlannerAgent — adjust_plan (Phase 5)
# ---------------------------------------------------------------------------


class TestPlannerAdjustPlan:
    """Verify planner actually modifies tracker based on quiz scores."""

    def _setup(self):
        import os
        import tempfile
        from prep_agent.core.tracker import Tracker
        tmpdir = tempfile.mkdtemp()
        os.makedirs(os.path.join(tmpdir, "knowledge"), exist_ok=True)
        tracker = Tracker(prep_dir=tmpdir)
        plan = {
            "total_days": 3, "total_weeks": 1, "hours_per_day": 2,
            "days": [
                {"day_num": 1, "date": "2026-04-01", "week": 1, "track_id": "sec",
                 "topic": "Security Basics", "morning_focus": "S", "evening_focus": "P",
                 "is_review_day": False, "is_buffer_day": False},
                {"day_num": 2, "date": "2026-04-02", "week": 1, "track_id": "sec",
                 "topic": "Security Basics", "morning_focus": "S", "evening_focus": "P",
                 "is_review_day": False, "is_buffer_day": False},
                {"day_num": 3, "date": "2026-04-03", "week": 1, "track_id": "net",
                 "topic": "Networking", "morning_focus": "S", "evening_focus": "P",
                 "is_review_day": False, "is_buffer_day": False},
            ],
            "tracks": [
                {"id": "sec", "name": "Security", "start_day": 1, "end_day": 2},
                {"id": "net", "name": "Networking", "start_day": 3, "end_day": 3},
            ],
        }
        cfg = {"profile": {"name": "T"}, "target": {"role": "T"}}
        tracker.initialize(plan, cfg)
        return tracker

    def test_inserts_review_on_low_score(self):
        from prep_agent.agents.planner import PlannerAgent
        tracker = self._setup()
        ctx = {
            "current_day": 1,
            "today_entry": {"track_id": "sec", "topic": "Security Basics"},
            "quiz_history": [{"topic": "Security Basics", "score": 2, "total": 10}],
        }
        planner = PlannerAgent()
        result = planner.adjust_plan(ctx, tracker)
        assert len(result["adjustments"]) >= 1
        assert "review" in result["adjustments"][0].lower()
        state = tracker.load()
        assert len(state["days"]) == 4  # was 3, now 4

    def test_compresses_on_high_score(self):
        from prep_agent.agents.planner import PlannerAgent
        tracker = self._setup()
        ctx = {
            "current_day": 1,
            "today_entry": {"track_id": "sec", "topic": "Security Basics"},
            "quiz_history": [
                {"topic": "Networking", "score": 9, "total": 10},
                {"topic": "Networking", "score": 9, "total": 10},
            ],
        }
        planner = PlannerAgent()
        result = planner.adjust_plan(ctx, tracker)
        assert len(result["adjustments"]) >= 1
        assert "compress" in result["adjustments"][0].lower()
        state = tracker.load()
        assert len(state["days"]) == 2  # was 3, now 2

    def test_max_two_adjustments(self):
        from prep_agent.agents.planner import PlannerAgent
        tracker = self._setup()
        ctx = {
            "current_day": 1,
            "today_entry": {"track_id": "sec", "topic": "Security Basics"},
            "quiz_history": [
                {"topic": "Security Basics", "score": 1, "total": 10},
                {"topic": "Networking", "score": 1, "total": 10},
                {"topic": "Extra Topic", "score": 1, "total": 10},
            ],
        }
        planner = PlannerAgent()
        result = planner.adjust_plan(ctx, tracker)
        assert len(result["adjustments"]) <= 2


# ---------------------------------------------------------------------------
# TutorAgent
# ---------------------------------------------------------------------------


class TestTutorAgent:
    """Verify tutor adapts teaching approach to user context."""

    def test_adapts_to_no_prior_knowledge(self):
        """Tutor should start with basics for new user on new topic."""
        from prep_agent.agents.tutor import TutorAgent

        tutor = TutorAgent()
        ctx = {
            "topic": "Kubernetes Security",
            "strengths": [],
            "prior_notes": "",
            "topic_quiz_scores": [],
        }
        result = tutor.run(ctx)
        action = result["result"]["result"]["action"]
        assert action == "teach_fundamentals"

    def test_adapts_to_related_experience(self):
        """Tutor should use analogy approach when user has related strengths."""
        from prep_agent.agents.tutor import TutorAgent

        tutor = TutorAgent()
        # The tutor checks if any strength string is a substring of the topic
        # or vice versa, so "Security" (strength) is in "Cloud Security" (topic).
        ctx = {
            "topic": "Cloud Security",
            "strengths": ["Security", "Networking"],
            "prior_notes": "",
            "topic_quiz_scores": [],
        }
        result = tutor.run(ctx)
        action = result["result"]["result"]["action"]
        assert action == "teach_with_bridge"
        assert result["result"]["result"]["approach"] == "analogy"

    def test_detects_low_quiz_scores_switches_to_remedial(self):
        """Tutor should switch to remedial when quiz scores are low."""
        from prep_agent.agents.tutor import TutorAgent

        tutor = TutorAgent()
        ctx = {
            "topic": "IAM",
            "strengths": [],
            "prior_notes": "Studied before",
            "topic_quiz_scores": [30, 40, 25],
        }
        result = tutor.run(ctx)
        action = result["result"]["result"]["action"]
        assert action == "teach_remedial"
        assert result["result"]["result"]["approach"] == "targeted_review"

    def test_goes_deeper_with_good_scores(self):
        """Tutor should go deeper when user has prior knowledge and decent scores."""
        from prep_agent.agents.tutor import TutorAgent

        tutor = TutorAgent()
        ctx = {
            "topic": "Networking",
            "strengths": [],
            "prior_notes": "Some notes on subnetting",
            "topic_quiz_scores": [80, 85],
        }
        result = tutor.run(ctx)
        action = result["result"]["result"]["action"]
        assert action == "teach_advanced"


# ---------------------------------------------------------------------------
# QuizAgent
# ---------------------------------------------------------------------------


class TestQuizAgent:
    """Verify quiz adapts difficulty to mastery level."""

    def test_selects_easy_for_low_mastery(self):
        """Quiz should pick easy questions when mastery is low."""
        from prep_agent.agents.quiz_agent import QuizAgent

        quiz = QuizAgent()
        ctx = {
            "topic": "IAM",
            "quiz_history": [
                {"score": 2, "total": 10},
                {"score": 3, "total": 10},
            ],
        }
        result = quiz.run(ctx)
        difficulty = result["result"]["result"]["difficulty"]
        assert difficulty == "easy"

    def test_selects_hard_for_high_mastery(self):
        """Quiz should pick hard questions when mastery is high."""
        from prep_agent.agents.quiz_agent import QuizAgent

        quiz = QuizAgent()
        ctx = {
            "topic": "Networking",
            "quiz_history": [
                {"score": 9, "total": 10},
                {"score": 10, "total": 10},
                {"score": 9, "total": 10},
            ],
        }
        result = quiz.run(ctx)
        difficulty = result["result"]["result"]["difficulty"]
        assert difficulty == "hard"

    def test_selects_mixed_for_moderate_mastery(self):
        """Quiz should pick mixed difficulty for moderate mastery."""
        from prep_agent.agents.quiz_agent import QuizAgent

        quiz = QuizAgent()
        ctx = {
            "topic": "Security",
            "quiz_history": [
                {"score": 6, "total": 10},
                {"score": 7, "total": 10},
            ],
        }
        result = quiz.run(ctx)
        difficulty = result["result"]["result"]["difficulty"]
        assert difficulty == "mixed"

    def test_empty_history_selects_easy(self):
        """Quiz should pick easy for a user with no quiz history."""
        from prep_agent.agents.quiz_agent import QuizAgent

        quiz = QuizAgent()
        ctx = {"topic": "New Topic", "quiz_history": []}
        result = quiz.run(ctx)
        difficulty = result["result"]["result"]["difficulty"]
        assert difficulty == "easy"


# ---------------------------------------------------------------------------
# ReviewerAgent
# ---------------------------------------------------------------------------


class TestReviewerAgent:
    """Verify reviewer generates appropriate recommendations."""

    def test_generates_recommendations(self):
        """Reviewer should generate at least one recommendation."""
        from prep_agent.agents.reviewer import ReviewerAgent

        reviewer = ReviewerAgent()
        ctx = {
            "days_done": 20,
            "total_days": 60,
            "progress_pct": 33,
            "streak": 5,
            "quiz_history": [
                {"score": 5, "total": 10},
                {"score": 4, "total": 10},
            ],
            "tracks": [],
            "content": [],
        }
        result = reviewer.run(ctx)
        recs = result["result"]["result"]["recommendations"]
        # Low quiz scores should trigger more_review recommendation
        assert len(recs) > 0
        assert any("review" in r.lower() for r in recs)

    def test_detects_broken_streak(self):
        """Reviewer should flag a broken streak (streak == 0)."""
        from prep_agent.agents.reviewer import ReviewerAgent

        reviewer = ReviewerAgent()
        ctx = {
            "days_done": 10,
            "total_days": 60,
            "progress_pct": 16,
            "streak": 0,
            "quiz_history": [{"score": 8, "total": 10}],
            "tracks": [],
            "content": [],
        }
        result = reviewer.run(ctx)
        recs = result["result"]["result"]["recommendations"]
        assert any("streak" in r.lower() for r in recs)

    def test_recommends_advancement_for_high_scores(self):
        """Reviewer should recommend advancement when quiz scores are high."""
        from prep_agent.agents.reviewer import ReviewerAgent

        reviewer = ReviewerAgent()
        ctx = {
            "days_done": 30,
            "total_days": 60,
            "progress_pct": 50,
            "streak": 10,
            "quiz_history": [
                {"score": 9, "total": 10},
                {"score": 10, "total": 10},
                {"score": 9, "total": 10},
                {"score": 10, "total": 10},
                {"score": 9, "total": 10},
            ],
            "tracks": [],
            "content": [],
        }
        result = reviewer.run(ctx)
        recs = result["result"]["result"]["recommendations"]
        assert any("harder" in r.lower() or "advance" in r.lower() for r in recs)


# ---------------------------------------------------------------------------
# Orchestrator routing (simulated -- no Orchestrator class yet)
# ---------------------------------------------------------------------------


class TestOrchestratorRouting:
    """Verify that session types route to the correct agents.

    Since the Orchestrator class does not exist yet, these tests verify
    the routing logic by directly invoking the agents that each session
    type would dispatch to.
    """

    def _route_session(self, session_type: str, context: dict) -> dict:
        """Simulate orchestrator routing logic."""
        from prep_agent.agents.planner import PlannerAgent
        from prep_agent.agents.tutor import TutorAgent
        from prep_agent.agents.quiz_agent import QuizAgent
        from prep_agent.agents.reviewer import ReviewerAgent

        if session_type == "study":
            planner = PlannerAgent()
            plan_result = planner.run(context)
            tutor = TutorAgent()
            tutor_result = tutor.run(context)
            return {
                "agents_used": ["planner", "tutor"],
                "plan": plan_result,
                "session": tutor_result,
            }
        elif session_type == "quiz":
            quiz = QuizAgent()
            quiz_result = quiz.run(context)
            return {"agents_used": ["quiz"], "quiz": quiz_result}
        elif session_type == "review":
            reviewer = ReviewerAgent()
            review_result = reviewer.run(context)
            planner = PlannerAgent()
            plan_result = planner.run(context)
            return {
                "agents_used": ["reviewer", "planner"],
                "review": review_result,
                "plan": plan_result,
            }
        else:
            return {"agents_used": [], "error": f"Unknown session type: {session_type}"}

    def test_study_routes_to_planner_and_tutor(self):
        """'study' session should invoke planner + tutor."""
        ctx = {
            "topic": "Cloud Security",
            "total_days": 60,
            "current_day": 10,
            "progress_pct": 15,
            "weak_topics": [],
            "strong_topics": [],
            "quiz_avg": 0,
            "gaps": [],
            "strengths": [],
            "prior_notes": "",
            "topic_quiz_scores": [],
        }
        result = self._route_session("study", ctx)
        assert "planner" in result["agents_used"]
        assert "tutor" in result["agents_used"]
        assert result["plan"]["agent"] == "planner"
        assert result["session"]["agent"] == "tutor"

    def test_quiz_routes_to_quiz_agent(self):
        """'quiz' session should invoke quiz agent."""
        ctx = {
            "topic": "IAM",
            "quiz_history": [{"score": 5, "total": 10}],
        }
        result = self._route_session("quiz", ctx)
        assert result["agents_used"] == ["quiz"]
        assert result["quiz"]["agent"] == "quiz"

    def test_review_routes_to_reviewer_and_planner(self):
        """'review' session should invoke reviewer + planner."""
        ctx = {
            "days_done": 20,
            "total_days": 60,
            "current_day": 20,
            "progress_pct": 33,
            "streak": 5,
            "quiz_history": [],
            "tracks": [],
            "content": [],
            "weak_topics": [],
            "strong_topics": [],
            "quiz_avg": 70,
            "gaps": [],
        }
        result = self._route_session("review", ctx)
        assert "reviewer" in result["agents_used"]
        assert "planner" in result["agents_used"]


# ---------------------------------------------------------------------------
# AgentEvaluator
# ---------------------------------------------------------------------------


class TestAgentEvaluator:
    """Verify the evaluation harness itself."""

    def test_all_scenarios_pass(self):
        """All built-in test scenarios should pass."""
        from prep_agent.agents.evaluation import AgentEvaluator

        evaluator = AgentEvaluator()
        results = evaluator.run_test_scenarios()

        assert len(results) >= 5, f"Expected at least 5 scenarios, got {len(results)}"
        for scenario in results:
            assert scenario["passed"], (
                f"Scenario FAILED: {scenario['scenario']} "
                f"(expected={scenario['expected']}, actual={scenario['actual']})"
            )

    def test_log_and_retrieve_decisions(self, tmp_path):
        """Logged decisions should be retrievable in reliability metrics."""
        from prep_agent.agents.evaluation import AgentEvaluator

        evaluator = AgentEvaluator(prep_dir=str(tmp_path))
        evaluator.log_agent_decision("planner", "compress", "behind schedule", "day 45/60")
        evaluator.log_agent_decision("tutor", "teach_fundamentals", "no prior", "new topic")

        reliability = evaluator.get_agent_reliability()
        assert reliability["total_decisions"] == 2
        assert "compress" in reliability["most_common_actions"]
        assert "teach_fundamentals" in reliability["most_common_actions"]

    def test_log_and_retrieve_sessions(self, tmp_path):
        """Logged sessions should appear in learning curve analysis."""
        from prep_agent.agents.evaluation import AgentEvaluator

        evaluator = AgentEvaluator(prep_dir=str(tmp_path))
        evaluator.log_session_quality("quiz", 30.0, quiz_score=60.0)
        evaluator.log_session_quality("quiz", 25.0, quiz_score=75.0)
        evaluator.log_session_quality("quiz", 20.0, quiz_score=85.0)

        curve = evaluator.get_learning_curve()
        assert curve["trend"] == "improving"
        assert len(curve["scores_over_time"]) == 3

    def test_progress_analytics_empty(self, tmp_path):
        """Progress analytics should handle empty data gracefully."""
        from prep_agent.agents.evaluation import AgentEvaluator

        evaluator = AgentEvaluator(prep_dir=str(tmp_path))
        progress = evaluator.get_progress_analytics()
        assert progress["study_consistency"] == 0.0
        assert progress["quiz_improvement"] == 0.0
        assert progress["time_to_mastery"] is None

    def test_generate_report(self, tmp_path):
        """Report generation should produce valid markdown."""
        from prep_agent.agents.evaluation import AgentEvaluator

        evaluator = AgentEvaluator(prep_dir=str(tmp_path))
        report = evaluator.generate_report()
        assert "# Agent Evaluation Report" in report
        assert "## Test Scenarios" in report
        assert "## Agent Reliability" in report
        assert "## Learning Curve" in report
        assert "PASS" in report
