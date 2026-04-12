"""Planner Agent -- generates and adjusts study plans based on progress."""

from __future__ import annotations

from prep_agent.agents.base import BaseAgent


class PlannerAgent(BaseAgent):
    """Generates and dynamically adjusts study plans.

    Observe: current progress, quiz scores, time remaining
    Reason: should we adjust the plan? speed up? slow down? skip?
    Act: regenerate or modify the study plan
    Evaluate: does the new plan fit the remaining time?
    """

    def __init__(self, config: dict | None = None) -> None:
        super().__init__("planner", config)

    def observe(self, context: dict) -> dict:
        """Gather planning-relevant state."""
        return {
            "days_remaining": context.get("total_days", 0) - context.get("current_day", 0),
            "progress_pct": context.get("progress_pct", 0),
            "weak_topics": context.get("weak_topics", []),
            "strong_topics": context.get("strong_topics", []),
            "quiz_avg": context.get("quiz_avg", 0),
            "gaps_remaining": [
                g for g in context.get("gaps", []) if g.get("status") != "completed"
            ],
        }

    def reason(self, observations: dict) -> dict:
        """Decide planning action based on progress."""
        progress = observations["progress_pct"]
        days_remaining = observations["days_remaining"]
        weak_topics = observations.get("weak_topics", [])

        # Behind schedule: compress remaining topics
        if progress < 30 and days_remaining < 20:
            return {
                "action": "compress_plan",
                "params": {"focus_on": "critical_gaps_only"},
                "reasoning": (
                    f"Behind schedule ({progress:.0f}% with {days_remaining} days left). "
                    "Compressing to critical topics only."
                ),
            }

        # Weak topics detected: schedule extra review
        if weak_topics:
            return {
                "action": "add_review",
                "params": {"topics": weak_topics},
                "reasoning": (
                    f"Weak areas detected: {', '.join(weak_topics[:3])}. "
                    "Adding review sessions."
                ),
            }

        # On track: continue as planned
        return {
            "action": "continue",
            "params": {},
            "reasoning": (
                f"On track ({progress:.0f}% complete, {days_remaining} days remaining). "
                "No adjustments needed."
            ),
        }

    def act(self, action: str, params: dict) -> dict:
        if action == "compress_plan":
            return {
                "result": "plan_compressed",
                "success": True,
                "message": f"Focus narrowed to: {params.get('focus_on')}",
            }
        elif action == "add_review":
            topics = params.get("topics", [])
            return {
                "result": "review_added",
                "success": True,
                "message": f"Review sessions added for: {', '.join(topics)}",
            }
        else:
            return {
                "result": "no_change",
                "success": True,
                "message": "Plan continues as scheduled.",
            }

    def evaluate(self, result: dict) -> dict:
        return {
            "satisfied": result.get("success", False),
            "feedback": "",
            "next_action": None,
        }

    def adjust_plan(self, context: dict, tracker) -> dict:
        """Actually modify the study plan based on quiz performance.

        Called after completing a day or taking a quiz. Makes at most
        2 adjustments to avoid plan churn.

        Returns: {adjustments: list[str]} describing changes made.
        """
        adjustments: list[str] = []
        quiz_history = context.get("quiz_history", [])
        if not quiz_history:
            return {"adjustments": []}

        # Group quiz scores by topic
        from collections import defaultdict
        topic_scores: dict[str, list[float]] = defaultdict(list)
        for q in quiz_history:
            total = q.get("total", 0)
            if total > 0:
                topic_scores[q["topic"]].append(q["score"] / total * 100)

        current_day = context.get("current_day", 1)
        today_entry = context.get("today_entry", {})
        current_track = today_entry.get("track_id", "")
        current_topic = today_entry.get("topic", "")

        for topic, scores in topic_scores.items():
            if len(adjustments) >= 2:
                break
            avg = sum(scores) / len(scores)

            # Low score → insert review day
            if avg < 50 and len(scores) >= 1:
                # Find track_id for this topic from days
                state = tracker.load()
                track_id = ""
                for d in state.get("days", []):
                    if d.get("topic") == topic or topic in d.get("topic", ""):
                        track_id = d.get("track_id", "")
                        break
                if track_id and tracker.insert_review_day(current_day, track_id, topic):
                    adjustments.append(f"Added review day for '{topic}' (avg score: {avg:.0f}%)")

            # High score → compress track
            elif avg > 85 and len(scores) >= 2:
                state = tracker.load()
                track_id = ""
                for d in state.get("days", []):
                    if d.get("topic") == topic or topic in d.get("topic", ""):
                        track_id = d.get("track_id", "")
                        break
                if track_id and track_id != current_track:
                    removed = tracker.compress_track(track_id, remove_days=1)
                    if removed:
                        adjustments.append(f"Compressed '{topic}' track by {removed} day (avg score: {avg:.0f}%)")

        return {"adjustments": adjustments}

    def get_today_recommendation(self, context: dict) -> dict:
        """Get what to study today based on plan + progress analysis."""
        result = self.run(context)
        # Return today's plan entry with any adjustments
        today = context.get("today_entry", {})
        return {
            "topic": today.get("topic", "Review"),
            "morning_focus": today.get("morning_focus", "Study"),
            "evening_focus": today.get("evening_focus", "Practice"),
            "adjustment": result.get("result", {}).get("message", ""),
            "reasoning": result.get("reasoning_trace", []),
        }
