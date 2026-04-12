"""Quiz Agent -- generates questions, evaluates answers, tracks mastery."""

from __future__ import annotations

from prep_agent.agents.base import BaseAgent


class QuizAgent(BaseAgent):
    """Generates and evaluates quizzes adapted to the user's mastery level.

    Observe: user's quiz history, current topic, mastery level
    Reason: what difficulty? which areas to probe? how many questions?
    Act: select/generate questions and evaluate answers
    Evaluate: has the user demonstrated mastery?
    """

    def __init__(self, config: dict | None = None) -> None:
        super().__init__("quiz", config)

    def observe(self, context: dict) -> dict:
        return {
            "topic": context.get("topic", ""),
            "quiz_history": context.get("quiz_history", []),
            "mastery_level": self._calculate_mastery(context.get("quiz_history", [])),
            "available_questions": context.get("available_questions", []),
            "previously_asked": context.get("previously_asked", set()),
        }

    def reason(self, observations: dict) -> dict:
        mastery = observations["mastery_level"]
        topic = observations["topic"]

        if mastery < 40:
            return {
                "action": "quiz_easy",
                "params": {"difficulty": "easy", "num": 5},
                "reasoning": (
                    f"Low mastery ({mastery:.0f}%) on '{topic}'. "
                    "Starting with easy questions to build confidence."
                ),
            }
        elif mastery < 70:
            return {
                "action": "quiz_mixed",
                "params": {"difficulty": "mixed", "num": 7},
                "reasoning": (
                    f"Moderate mastery ({mastery:.0f}%) on '{topic}'. "
                    "Mixed difficulty to identify remaining gaps."
                ),
            }
        else:
            return {
                "action": "quiz_hard",
                "params": {"difficulty": "hard", "num": 5},
                "reasoning": (
                    f"High mastery ({mastery:.0f}%) on '{topic}'. "
                    "Hard questions to verify deep understanding."
                ),
            }

    def act(self, action: str, params: dict) -> dict:
        return {
            "result": {
                "difficulty": params.get("difficulty", "mixed"),
                "num_questions": params.get("num", 5),
            },
            "success": True,
            "message": (
                f"Quiz prepared: {params.get('num', 5)} "
                f"{params.get('difficulty', 'mixed')} questions."
            ),
        }

    def _calculate_mastery(self, quiz_history: list[dict]) -> float:
        """Calculate mastery level from quiz history (0-100).

        Uses weighted average of the last 5 quizzes, with more recent
        quizzes weighted higher. This reflects current understanding
        better than a simple average over all time.
        """
        if not quiz_history:
            return 0.0
        # Weight recent scores more heavily
        scores: list[tuple[float, int]] = []
        for i, q in enumerate(quiz_history[-5:]):  # Last 5 quizzes
            score_pct = (q.get("score", 0) / max(q.get("total", 1), 1)) * 100
            weight = i + 1  # More recent = higher weight
            scores.append((score_pct, weight))
        if not scores:
            return 0.0
        weighted_sum = sum(s * w for s, w in scores)
        total_weight = sum(w for _, w in scores)
        return weighted_sum / total_weight

    def prepare_quiz(self, context: dict) -> dict:
        """Prepare a quiz session adapted to mastery level."""
        result = self.run(context)
        agent_result = result.get("result", {}).get("result", {})
        return {
            "topic": context.get("topic", ""),
            "difficulty": agent_result.get("difficulty", "mixed"),
            "num_questions": agent_result.get("num_questions", 5),
            "mastery_before": self._calculate_mastery(context.get("quiz_history", [])),
            "reasoning_trace": result.get("reasoning_trace", []),
        }
