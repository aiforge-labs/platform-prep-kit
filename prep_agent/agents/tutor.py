"""Tutor Agent -- teaches concepts, adapts to user's level and background."""

from __future__ import annotations

from prep_agent.agents.base import BaseAgent


class TutorAgent(BaseAgent):
    """Teaches concepts by adapting to the user's background and progress.

    Observe: user's strengths, prior knowledge notes, quiz scores on topic
    Reason: what's the best teaching approach? basics first? advanced? analogy-based?
    Act: generate study content (standalone or AI prompt)
    Evaluate: did the user demonstrate understanding (via quiz)?
    """

    def __init__(self, config: dict | None = None) -> None:
        super().__init__("tutor", config)

    def observe(self, context: dict) -> dict:
        return {
            "topic": context.get("topic", ""),
            "user_strengths": context.get("strengths", []),
            "prior_notes": context.get("prior_notes", ""),
            "topic_quiz_scores": context.get("topic_quiz_scores", []),
            "knowledge_pack": context.get("knowledge_pack", ""),
            "session_type": context.get("session_type", "study"),
        }

    def reason(self, observations: dict) -> dict:
        topic = observations["topic"]
        scores = observations.get("topic_quiz_scores", [])
        strengths = observations.get("user_strengths", [])
        prior = observations.get("prior_notes", "")

        # First time studying this topic
        if not scores and not prior:
            # Check if user has related strengths for analogy-based teaching
            has_related = any(
                s.lower() in topic.lower() or topic.lower() in s.lower()
                for s in strengths
            )
            if has_related:
                return {
                    "action": "teach_with_bridge",
                    "params": {"approach": "analogy", "from_strengths": strengths},
                    "reasoning": (
                        f"First time on '{topic}'. User has related experience "
                        "-- using analogy-based approach."
                    ),
                }
            return {
                "action": "teach_fundamentals",
                "params": {"approach": "basics_first"},
                "reasoning": (
                    f"First time on '{topic}'. No prior knowledge. "
                    "Starting with fundamentals."
                ),
            }

        # Low scores: needs review with different approach
        if scores and sum(scores) / len(scores) < 60:
            avg = sum(scores) / len(scores)
            return {
                "action": "teach_remedial",
                "params": {
                    "approach": "targeted_review",
                    "weak_areas": observations.get("feedback", ""),
                },
                "reasoning": (
                    f"Low quiz scores on '{topic}' (avg {avg:.0f}%). "
                    "Targeted review needed."
                ),
            }

        # Has prior knowledge: go deeper
        return {
            "action": "teach_advanced",
            "params": {"approach": "deep_dive"},
            "reasoning": f"User has prior knowledge on '{topic}'. Going deeper.",
        }

    def act(self, action: str, params: dict) -> dict:
        approach = params.get("approach", "basics_first")
        return {
            "result": {
                "approach": approach,
                "action": action,
            },
            "success": True,
            "message": f"Study session prepared with {approach} approach.",
        }

    def generate_study_session(self, context: dict) -> dict:
        """Generate a study session adapted to user's state.

        Returns a structured session with:
            approach: how to teach (basics/analogy/deep_dive/review)
            content: study material (from knowledge packs or generated)
            questions: practice questions
            reasoning: why this approach was chosen
        """
        # Retrieve relevant knowledge if available
        topic = context.get("topic", "")
        if topic and not context.get("knowledge_pack"):
            try:
                from prep_agent.core.knowledge import KnowledgeBase

                kb = KnowledgeBase()
                results = kb.search(topic, top_k=3)
                if results:
                    snippets = []
                    for r in results:
                        lines = r.get("matching_lines", [])[:3]
                        if lines:
                            snippets.append(f"{r['topic']}: {' '.join(lines)}")
                    if snippets:
                        context = {**context, "knowledge_pack": "\n".join(snippets)}
            except Exception:
                pass  # Knowledge retrieval is best-effort

        result = self.run(context)
        agent_result = result.get("result", {}).get("result", {})
        return {
            "topic": context.get("topic", ""),
            "approach": agent_result.get("approach", "basics_first"),
            "reasoning_trace": result.get("reasoning_trace", []),
            "iterations": result.get("iterations", 1),
        }
