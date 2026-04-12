"""Evaluation harness -- measures agent reliability and learning effectiveness.

This module implements Step 10 of the AI agent design framework:
'Evaluate and Monitor'. It provides:
- Test scenarios to validate agent behavior
- Metrics collection for study session quality
- Structured logging of all agent decisions
- Progress analytics for continuous improvement
"""

from __future__ import annotations

import json
import os
from datetime import datetime


class AgentEvaluator:
    """Evaluates the career prep agent system's effectiveness.

    Tracks three categories of metrics:
    1. Agent behavior: Are decisions reasonable? (reasoning quality)
    2. Learning outcomes: Is the user actually learning? (quiz trends)
    3. System reliability: Does the agent work consistently? (error rates)
    """

    def __init__(self, prep_dir: str | None = None) -> None:
        self.prep_dir = prep_dir or os.path.expanduser("~/.prep")
        self.metrics_path = os.path.join(self.prep_dir, "agent-metrics.json")

    # ------------------------------------------------------------------
    # Persistence helpers
    # ------------------------------------------------------------------

    def _load_metrics(self) -> dict:
        """Load metrics from disk, returning empty structure if missing."""
        if os.path.exists(self.metrics_path):
            with open(self.metrics_path, "r") as fh:
                return json.load(fh)
        return {"decisions": [], "sessions": [], "version": 1}

    def _save_metrics(self, metrics: dict) -> None:
        """Persist metrics to disk, creating directories as needed."""
        os.makedirs(os.path.dirname(self.metrics_path), exist_ok=True)
        with open(self.metrics_path, "w") as fh:
            json.dump(metrics, fh, indent=2, default=str)

    # ------------------------------------------------------------------
    # Logging
    # ------------------------------------------------------------------

    def log_agent_decision(
        self,
        agent_name: str,
        action: str,
        reasoning: str,
        context_summary: str,
    ) -> None:
        """Log an agent decision for later analysis."""
        metrics = self._load_metrics()
        metrics["decisions"].append(
            {
                "agent": agent_name,
                "action": action,
                "reasoning": reasoning,
                "context_summary": context_summary,
                "timestamp": datetime.now().isoformat(),
            }
        )
        self._save_metrics(metrics)

    def log_session_quality(
        self,
        session_type: str,
        duration_minutes: float,
        user_rating: int | None = None,
        quiz_score: float | None = None,
    ) -> None:
        """Log session quality metrics."""
        metrics = self._load_metrics()
        metrics["sessions"].append(
            {
                "session_type": session_type,
                "duration_minutes": duration_minutes,
                "user_rating": user_rating,
                "quiz_score": quiz_score,
                "timestamp": datetime.now().isoformat(),
            }
        )
        self._save_metrics(metrics)

    # ------------------------------------------------------------------
    # Analytics
    # ------------------------------------------------------------------

    def get_learning_curve(self, topic: str | None = None) -> dict:
        """Analyze quiz score trends over time.

        Returns:
            dict with keys: topic, scores_over_time, trend, mastery_pct
        """
        metrics = self._load_metrics()
        sessions = metrics.get("sessions", [])

        # Collect quiz scores, optionally filtered by topic
        scores: list[float] = []
        for s in sessions:
            score = s.get("quiz_score")
            if score is not None:
                if topic is None or s.get("session_type", "").lower() == topic.lower():
                    scores.append(score)

        if not scores:
            return {
                "topic": topic or "all",
                "scores_over_time": [],
                "trend": "insufficient_data",
                "mastery_pct": 0.0,
            }

        # Determine trend from first half vs second half averages
        mid = max(len(scores) // 2, 1)
        first_half_avg = sum(scores[:mid]) / mid
        second_half_avg = sum(scores[mid:]) / max(len(scores[mid:]), 1)

        if second_half_avg > first_half_avg + 5:
            trend = "improving"
        elif second_half_avg < first_half_avg - 5:
            trend = "declining"
        else:
            trend = "stable"

        return {
            "topic": topic or "all",
            "scores_over_time": scores,
            "trend": trend,
            "mastery_pct": scores[-1] if scores else 0.0,
        }

    def get_agent_reliability(self) -> dict:
        """Analyze agent decision quality.

        Returns:
            dict with keys: total_decisions, error_rate, most_common_actions,
            avg_iterations
        """
        metrics = self._load_metrics()
        decisions = metrics.get("decisions", [])

        if not decisions:
            return {
                "total_decisions": 0,
                "error_rate": 0.0,
                "most_common_actions": {},
                "avg_iterations": 0.0,
            }

        # Count actions
        action_counts: dict[str, int] = {}
        error_count = 0
        for d in decisions:
            action = d.get("action", "unknown")
            action_counts[action] = action_counts.get(action, 0) + 1
            if "error" in action.lower() or "fail" in d.get("reasoning", "").lower():
                error_count += 1

        # Sort by frequency, take top 5
        sorted_actions = dict(
            sorted(action_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        )

        return {
            "total_decisions": len(decisions),
            "error_rate": error_count / len(decisions) if decisions else 0.0,
            "most_common_actions": sorted_actions,
            "avg_iterations": 1.0,  # From decision logs; each entry = 1 iteration
        }

    def get_progress_analytics(self) -> dict:
        """Comprehensive progress analytics.

        Returns:
            dict with keys: study_consistency, quiz_improvement,
            content_progress, time_to_mastery
        """
        metrics = self._load_metrics()
        sessions = metrics.get("sessions", [])

        # Study consistency: sessions per week (approximate)
        total_sessions = len(sessions)
        if total_sessions >= 2:
            first_ts = sessions[0].get("timestamp", "")
            last_ts = sessions[-1].get("timestamp", "")
            try:
                first_dt = datetime.fromisoformat(first_ts)
                last_dt = datetime.fromisoformat(last_ts)
                days_span = max((last_dt - first_dt).days, 1)
                weeks_span = max(days_span / 7, 1)
                sessions_per_week = total_sessions / weeks_span
            except (ValueError, TypeError):
                sessions_per_week = 0.0
        else:
            sessions_per_week = float(total_sessions)

        # Quiz improvement
        quiz_scores = [
            s["quiz_score"] for s in sessions if s.get("quiz_score") is not None
        ]
        if len(quiz_scores) >= 2:
            first_score = quiz_scores[0]
            last_score = quiz_scores[-1]
            quiz_improvement = last_score - first_score
        else:
            quiz_improvement = 0.0

        # Time to mastery: sessions until score consistently above 80
        mastery_session = None
        for i, score in enumerate(quiz_scores):
            if score >= 80:
                # Check if remaining scores also stay above 80
                remaining = quiz_scores[i:]
                if all(s >= 75 for s in remaining):
                    mastery_session = i + 1
                    break

        return {
            "study_consistency": round(sessions_per_week, 2),
            "quiz_improvement": round(quiz_improvement, 1),
            "content_progress": total_sessions,
            "time_to_mastery": mastery_session,
        }

    # ------------------------------------------------------------------
    # Test scenarios
    # ------------------------------------------------------------------

    def run_test_scenarios(self) -> list[dict]:
        """Run predefined test scenarios to validate agent behavior.

        Test scenarios:
        1. New user with no history -> should recommend fundamentals
        2. User with low quiz scores -> should recommend review
        3. User behind schedule -> should recommend compression
        4. User with high mastery -> should recommend advancement
        5. User with broken streak -> should encourage restart
        6. User with related strengths -> should use analogy approach
        7. User on track -> should continue as planned

        Returns:
            list of {scenario, expected, actual, passed}
        """
        from prep_agent.agents.planner import PlannerAgent
        from prep_agent.agents.tutor import TutorAgent
        from prep_agent.agents.quiz_agent import QuizAgent
        from prep_agent.agents.reviewer import ReviewerAgent

        results: list[dict] = []

        # Scenario 1: New user with no history -> tutor should teach fundamentals
        tutor = TutorAgent()
        ctx_new_user = {
            "topic": "Cloud Security Basics",
            "strengths": [],
            "prior_notes": "",
            "topic_quiz_scores": [],
        }
        tutor_result = tutor.run(ctx_new_user)
        action = tutor_result.get("result", {}).get("result", {}).get("action", "")
        results.append(
            {
                "scenario": "New user with no history",
                "expected": "teach_fundamentals",
                "actual": action,
                "passed": action == "teach_fundamentals",
            }
        )

        # Scenario 2: User with low quiz scores -> tutor should switch to remedial
        tutor2 = TutorAgent()
        ctx_low_scores = {
            "topic": "IAM Policies",
            "strengths": ["networking"],
            "prior_notes": "Studied before",
            "topic_quiz_scores": [30, 40, 35],
        }
        tutor_result2 = tutor2.run(ctx_low_scores)
        action2 = tutor_result2.get("result", {}).get("result", {}).get("action", "")
        results.append(
            {
                "scenario": "User with low quiz scores",
                "expected": "teach_remedial",
                "actual": action2,
                "passed": action2 == "teach_remedial",
            }
        )

        # Scenario 3: User behind schedule -> planner should compress
        planner = PlannerAgent()
        ctx_behind = {
            "total_days": 60,
            "current_day": 45,
            "progress_pct": 20,
            "weak_topics": [],
            "strong_topics": [],
            "quiz_avg": 50,
            "gaps": [{"id": "g1", "status": "pending"}],
        }
        planner_result = planner.run(ctx_behind)
        plan_action = (
            planner_result.get("reasoning_trace", [{}])[0].get("action", "")
            if planner_result.get("reasoning_trace")
            else ""
        )
        results.append(
            {
                "scenario": "User behind schedule",
                "expected": "compress_plan",
                "actual": plan_action,
                "passed": plan_action == "compress_plan",
            }
        )

        # Scenario 4: User with high mastery -> quiz should select hard questions
        quiz = QuizAgent()
        ctx_high = {
            "topic": "Kubernetes Security",
            "quiz_history": [
                {"score": 9, "total": 10},
                {"score": 10, "total": 10},
                {"score": 9, "total": 10},
            ],
        }
        quiz_result = quiz.run(ctx_high)
        quiz_difficulty = (
            quiz_result.get("result", {}).get("result", {}).get("difficulty", "")
        )
        results.append(
            {
                "scenario": "User with high mastery",
                "expected": "hard",
                "actual": quiz_difficulty,
                "passed": quiz_difficulty == "hard",
            }
        )

        # Scenario 5: User with broken streak -> reviewer should encourage restart
        reviewer = ReviewerAgent()
        ctx_broken = {
            "days_done": 20,
            "total_days": 60,
            "progress_pct": 33,
            "streak": 0,
            "quiz_history": [{"score": 7, "total": 10}],
            "tracks": [],
            "content": [],
        }
        review_result = reviewer.run(ctx_broken)
        recs = review_result.get("result", {}).get("result", {}).get(
            "recommendations", []
        )
        has_streak_rec = any("streak" in r.lower() for r in recs)
        results.append(
            {
                "scenario": "User with broken streak",
                "expected": "restart_streak recommendation",
                "actual": recs,
                "passed": has_streak_rec,
            }
        )

        # Scenario 6: User with related strengths -> tutor uses analogy approach
        tutor3 = TutorAgent()
        ctx_related = {
            "topic": "Cloud Security",
            "strengths": ["Security", "Networking"],
            "prior_notes": "",
            "topic_quiz_scores": [],
        }
        tutor_result3 = tutor3.run(ctx_related)
        action3 = tutor_result3.get("result", {}).get("result", {}).get("action", "")
        results.append(
            {
                "scenario": "User with related strengths",
                "expected": "teach_with_bridge",
                "actual": action3,
                "passed": action3 == "teach_with_bridge",
            }
        )

        # Scenario 7: User on track -> planner should continue
        planner2 = PlannerAgent()
        ctx_on_track = {
            "total_days": 60,
            "current_day": 30,
            "progress_pct": 50,
            "weak_topics": [],
            "strong_topics": ["Networking", "IAM"],
            "quiz_avg": 75,
            "gaps": [],
        }
        planner_result2 = planner2.run(ctx_on_track)
        plan_action2 = (
            planner_result2.get("reasoning_trace", [{}])[0].get("action", "")
            if planner_result2.get("reasoning_trace")
            else ""
        )
        results.append(
            {
                "scenario": "User on track with no weak topics",
                "expected": "continue",
                "actual": plan_action2,
                "passed": plan_action2 == "continue",
            }
        )

        return results

    # ------------------------------------------------------------------
    # Reporting
    # ------------------------------------------------------------------

    def generate_report(self) -> str:
        """Generate a markdown evaluation report."""
        reliability = self.get_agent_reliability()
        learning = self.get_learning_curve()
        progress = self.get_progress_analytics()
        scenarios = self.run_test_scenarios()

        passed = sum(1 for s in scenarios if s["passed"])
        total = len(scenarios)

        lines: list[str] = []
        lines.append("# Agent Evaluation Report")
        lines.append("")
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        lines.append("")

        # Test scenarios
        lines.append("## Test Scenarios")
        lines.append("")
        lines.append(f"**{passed}/{total} passed**")
        lines.append("")
        lines.append("| Scenario | Expected | Actual | Status |")
        lines.append("|----------|----------|--------|--------|")
        for s in scenarios:
            status = "PASS" if s["passed"] else "FAIL"
            actual_str = str(s["actual"])
            if len(actual_str) > 40:
                actual_str = actual_str[:37] + "..."
            lines.append(f"| {s['scenario']} | {s['expected']} | {actual_str} | {status} |")
        lines.append("")

        # Agent reliability
        lines.append("## Agent Reliability")
        lines.append("")
        lines.append(f"- Total decisions logged: {reliability['total_decisions']}")
        lines.append(f"- Error rate: {reliability['error_rate']:.1%}")
        if reliability["most_common_actions"]:
            lines.append("- Most common actions:")
            for action, count in reliability["most_common_actions"].items():
                lines.append(f"  - {action}: {count}")
        lines.append("")

        # Learning curve
        lines.append("## Learning Curve")
        lines.append("")
        lines.append(f"- Trend: {learning['trend']}")
        lines.append(f"- Current mastery: {learning['mastery_pct']:.0f}%")
        num_scores = len(learning["scores_over_time"])
        lines.append(f"- Quiz data points: {num_scores}")
        lines.append("")

        # Progress analytics
        lines.append("## Progress Analytics")
        lines.append("")
        lines.append(f"- Study consistency: {progress['study_consistency']} sessions/week")
        lines.append(f"- Quiz improvement: {progress['quiz_improvement']:+.1f} points")
        mastery_time = progress["time_to_mastery"]
        if mastery_time is not None:
            lines.append(f"- Sessions to mastery: {mastery_time}")
        else:
            lines.append("- Sessions to mastery: not yet achieved")
        lines.append("")

        return "\n".join(lines)
