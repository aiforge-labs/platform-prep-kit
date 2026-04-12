"""Orchestrator -- coordinates all agents using a ReAct meta-loop.

This is the brain of the career prep agent. It:
1. Observes the user's overall state
2. Reasons about which agent(s) to invoke
3. Delegates to specialized agents
4. Evaluates the combined result

The orchestrator itself follows the ReAct pattern at a higher level,
deciding WHICH agent to invoke rather than WHAT to do directly.
"""

from __future__ import annotations

from datetime import datetime

from prep_agent.agents.planner import PlannerAgent
from prep_agent.agents.quiz_agent import QuizAgent
from prep_agent.agents.reviewer import ReviewerAgent
from prep_agent.agents.tutor import TutorAgent


class Orchestrator:
    """Central coordinator for all career prep agents.

    Usage::

        orchestrator = Orchestrator(config)
        result = orchestrator.handle_session("study", context)
    """

    def __init__(self, config: dict | None = None) -> None:
        self.config = config or {}
        self.planner = PlannerAgent(config)
        self.tutor = TutorAgent(config)
        self.quiz = QuizAgent(config)
        self.reviewer = ReviewerAgent(config)
        self.session_log: list[dict] = []

    def handle_session(self, session_type: str, context: dict) -> dict:
        """Main entry point. Route to appropriate agent(s) based on session type.

        Args:
            session_type: one of "study", "quiz", "review", "today"
            context: dict with tracker state, config, etc.

        Returns:
            Dict with agent results, reasoning traces, and recommendations.
        """
        self._log_session_start(session_type)

        if session_type == "today":
            return self._handle_today(context)
        elif session_type == "study":
            return self._handle_study(context)
        elif session_type == "quiz":
            return self._handle_quiz(context)
        elif session_type == "review":
            return self._handle_review(context)
        else:
            return {"error": f"Unknown session type: {session_type}"}

    def _handle_today(self, context: dict) -> dict:
        """Handle 'prep today' -- get plan recommendation + review if needed."""
        plan_rec = self.planner.get_today_recommendation(context)

        # If we have enough history, also get reviewer input
        review = None
        if context.get("days_done", 0) >= 3:
            review = self.reviewer.generate_review(context)

        return {
            "session_type": "today",
            "plan": plan_rec,
            "review": review,
            "agents_invoked": ["planner"] + (["reviewer"] if review else []),
        }

    def _handle_study(self, context: dict) -> dict:
        """Handle 'prep study' -- tutor generates adapted session."""
        # Planner confirms today's topic
        plan_rec = self.planner.get_today_recommendation(context)

        # Tutor generates the study session
        study_context = {**context, "topic": plan_rec.get("topic", context.get("topic", ""))}
        session = self.tutor.generate_study_session(study_context)

        return {
            "session_type": "study",
            "plan": plan_rec,
            "session": session,
            "agents_invoked": ["planner", "tutor"],
        }

    def _handle_quiz(self, context: dict) -> dict:
        """Handle 'prep quiz' -- quiz agent prepares adapted quiz."""
        quiz_prep = self.quiz.prepare_quiz(context)

        return {
            "session_type": "quiz",
            "quiz": quiz_prep,
            "agents_invoked": ["quiz"],
        }

    def _handle_review(self, context: dict) -> dict:
        """Handle 'prep status' / weekly review -- full progress analysis."""
        review = self.reviewer.generate_review(context)
        plan_rec = self.planner.get_today_recommendation(context)

        return {
            "session_type": "review",
            "review": review,
            "plan": plan_rec,
            "agents_invoked": ["reviewer", "planner"],
        }

    def _log_session_start(self, session_type: str) -> None:
        self.session_log.append(
            {
                "type": session_type,
                "timestamp": datetime.now().isoformat(),
            }
        )

    def get_reasoning_summary(self) -> str:
        """Get a human-readable summary of recent agent decisions.

        Useful for showing the user WHY the agent made certain choices.
        """
        lines = ["## Agent Reasoning Trace\n"]
        for agent in [self.planner, self.tutor, self.quiz, self.reviewer]:
            if agent.log:
                lines.append(f"### {agent.name.title()} Agent")
                for entry in agent.log[-3:]:
                    lines.append(f"- **{entry['action']}**: {entry['reasoning']}")
                lines.append("")
        return "\n".join(lines)
