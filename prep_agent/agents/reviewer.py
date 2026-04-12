"""Reviewer Agent -- analyzes progress and recommends adjustments."""

from __future__ import annotations

from prep_agent.agents.base import BaseAgent


class ReviewerAgent(BaseAgent):
    """Analyzes overall prep progress and recommends adjustments.

    Observe: all progress data -- days done, quiz scores, content created, streaks
    Reason: is the user on track? what needs attention?
    Act: generate a review report with recommendations
    Evaluate: are recommendations actionable?
    """

    def __init__(self, config: dict | None = None) -> None:
        super().__init__("reviewer", config)

    def observe(self, context: dict) -> dict:
        return {
            "days_done": context.get("days_done", 0),
            "total_days": context.get("total_days", 0),
            "progress_pct": context.get("progress_pct", 0),
            "streak": context.get("streak", 0),
            "quiz_history": context.get("quiz_history", []),
            "tracks": context.get("tracks", []),
            "content": context.get("content", []),
        }

    def reason(self, observations: dict) -> dict:
        progress = observations["progress_pct"]
        streak = observations["streak"]
        quiz_history = observations.get("quiz_history", [])

        # Analyze quiz trends
        if quiz_history:
            recent_avg = sum(
                q.get("score", 0) / max(q.get("total", 1), 1) * 100
                for q in quiz_history[-5:]
            ) / min(len(quiz_history), 5)
        else:
            recent_avg = 0.0

        recommendations: list[str] = []

        days_done = observations["days_done"]
        if streak == 0 and days_done > 0:
            # Only fire "streak broke" if the user had prior activity
            recommendations.append("restart_streak")
        if progress < 40 and days_done > observations["total_days"] * 0.3:
            recommendations.append("accelerate")
        if quiz_history and recent_avg < 60:
            # Only fire "quiz scores low" when there is actual quiz history
            recommendations.append("more_review")
        if recent_avg > 85:
            recommendations.append("advance_difficulty")

        content_done = sum(
            1 for c in observations.get("content", []) if c.get("status") == "published"
        )
        content_total = len(observations.get("content", []))
        if content_total > 0 and content_done == 0 and progress > 50:
            recommendations.append("start_content")

        return {
            "action": "generate_review",
            "params": {
                "recommendations": recommendations,
                "recent_quiz_avg": recent_avg,
                "streak": streak,
            },
            "reasoning": (
                f"Progress: {progress:.0f}%, Quiz avg: {recent_avg:.0f}%, "
                f"Streak: {streak}. {len(recommendations)} recommendations."
            ),
        }

    def act(self, action: str, params: dict) -> dict:
        recs = params.get("recommendations", [])
        messages = {
            "restart_streak": (
                "Your streak broke. Even 15 minutes today keeps momentum."
            ),
            "accelerate": (
                "Behind schedule. Focus on critical gaps only "
                "-- skip moderate priority topics."
            ),
            "more_review": (
                "Quiz scores are low. Add extra review sessions "
                "before moving to new topics."
            ),
            "advance_difficulty": (
                "Great quiz scores! Move to harder material "
                "and real-world scenarios."
            ),
            "start_content": (
                "You're past halfway but haven't started content creation. "
                "Start drafting now."
            ),
        }
        rec_messages = [messages.get(r, r) for r in recs]
        return {
            "result": {
                "recommendations": rec_messages,
                "quiz_avg": params.get("recent_quiz_avg", 0),
                "streak": params.get("streak", 0),
            },
            "success": True,
            "message": f"Review complete. {len(rec_messages)} recommendations.",
        }

    def generate_review(self, context: dict) -> dict:
        """Generate a comprehensive progress review."""
        result = self.run(context)
        agent_result = result.get("result", {}).get("result", {})
        return {
            "recommendations": agent_result.get("recommendations", []),
            "quiz_avg": agent_result.get("quiz_avg", 0),
            "streak": agent_result.get("streak", 0),
            "reasoning_trace": result.get("reasoning_trace", []),
        }
