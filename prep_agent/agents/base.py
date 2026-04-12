"""Base agent with ReAct reasoning loop."""

from __future__ import annotations

from datetime import datetime


class BaseAgent:
    """Base class for all agents in the career prep system.

    Implements the ReAct (Reasoning + Action) pattern:
    1. Observe: gather state from tracker, knowledge base, quiz history
    2. Reason: decide what action to take based on observations
    3. Act: execute the chosen action
    4. Evaluate: assess whether the action achieved its goal

    This is the core of agentic AI -- the agent doesn't just respond,
    it reasons about what to do next.
    """

    def __init__(self, name: str, config: dict | None = None) -> None:
        self.name = name
        self.config = config or {}
        self.memory: list[dict] = []  # Short-term conversation memory
        self.log: list[dict] = []  # Decision log for evaluation

    def observe(self, context: dict) -> dict:
        """Gather relevant state. Override in subclasses."""
        return context

    def reason(self, observations: dict) -> dict:
        """Decide what action to take. Override in subclasses.

        Returns:
            dict with keys:
                action (str): the action name to execute
                params (dict): parameters for the action
                reasoning (str): human-readable explanation of why
        """
        raise NotImplementedError

    def act(self, action: str, params: dict) -> dict:
        """Execute an action. Override in subclasses.

        Returns:
            dict with keys:
                result (any): the action output
                success (bool): whether the action succeeded
                message (str): human-readable summary
        """
        raise NotImplementedError

    def evaluate(self, action_result: dict) -> dict:
        """Assess the action outcome. Override in subclasses.

        Returns:
            dict with keys:
                satisfied (bool): whether the goal was met
                feedback (str): what went wrong (if not satisfied)
                next_action (str | None): hint for next iteration
        """
        return {"satisfied": True, "feedback": "", "next_action": None}

    def run(self, context: dict, max_iterations: int = 3) -> dict:
        """Execute the full ReAct loop.

        This is the main entry point. It runs:
            observe -> reason -> act -> evaluate
        and loops if evaluate says to continue.

        The loop is bounded by *max_iterations* to prevent runaway reasoning.
        Each iteration feeds the evaluation back into observations so the
        agent can self-correct.

        Args:
            context: initial state dict (tracker data, user input, etc.)
            max_iterations: safety cap on reasoning cycles

        Returns:
            dict with agent name, final result, iteration count, and
            the full reasoning trace for transparency.
        """
        observations = self.observe(context)
        result: dict = {}

        for i in range(max_iterations):
            decision = self.reason(observations)
            self._log_decision(i, decision)

            result = self.act(decision["action"], decision.get("params", {}))

            evaluation = self.evaluate(result)

            if evaluation["satisfied"]:
                return {
                    "agent": self.name,
                    "result": result,
                    "iterations": i + 1,
                    "reasoning_trace": self.log[-max_iterations:],
                }

            # Feed evaluation back into observations for next iteration
            observations["feedback"] = evaluation["feedback"]
            observations["previous_result"] = result

        return {
            "agent": self.name,
            "result": result,
            "iterations": max_iterations,
            "reasoning_trace": self.log[-max_iterations:],
            "note": "Max iterations reached",
        }

    def _log_decision(self, iteration: int, decision: dict) -> None:
        """Log a decision for evaluation and debugging."""
        self.log.append(
            {
                "agent": self.name,
                "iteration": iteration,
                "action": decision.get("action"),
                "reasoning": decision.get("reasoning", ""),
                "timestamp": datetime.now().isoformat(),
            }
        )

    def add_memory(self, role: str, content: str) -> None:
        """Add to short-term memory."""
        self.memory.append({"role": role, "content": content})
        # Keep last 20 messages
        if len(self.memory) > 20:
            self.memory = self.memory[-20:]
