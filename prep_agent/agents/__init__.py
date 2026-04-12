"""Multi-agent system for career prep.

Architecture:
    Orchestrator coordinates 4 specialized agents:
    - PlannerAgent: generates and adjusts study plans
    - TutorAgent: teaches concepts, adapts to user level
    - QuizAgent: generates questions, evaluates answers
    - ReviewerAgent: analyzes progress, suggests adjustments

Communication:
    Agents exchange Pydantic models (from prep_agent.models).
    The Orchestrator uses a ReAct loop: Observe -> Reason -> Act -> Evaluate.
"""
