"""Context builder — bridges core module state into agent-compatible context dicts.

The core modules (tracker, config) use plain dicts.  The agent system
(Orchestrator, PlannerAgent, etc.) expects a specific context shape.
This module translates between the two so neither layer has to know
about the other.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from prep_agent.models import PrepConfig


def build_agent_context(
    tracker_state: dict[str, Any],
    config: dict[str, Any],
    today_entry: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a context dict that the Orchestrator and agents expect.

    Args:
        tracker_state: Output of ``Tracker.load()`` — keys include
            ``days``, ``tracks``, ``content``, ``quiz_history``,
            ``current_day``, ``total_days``, ``streak``, etc.
        config: Output of ``load_config()`` — keys include
            ``strengths``, ``gaps``, ``timeline``, etc.
        today_entry: Optional output of ``Tracker.get_today()``.

    Returns:
        Dict with all keys the agent ``observe()`` methods read.
    """
    days = tracker_state.get("days", [])
    total_days = tracker_state.get("total_days", len(days))
    days_done = sum(1 for d in days if d.get("status") == "done")
    pct = round(days_done / total_days * 100, 1) if total_days else 0.0

    quiz_history = tracker_state.get("quiz_history", [])
    weak_topics, strong_topics, quiz_avg = _analyse_quiz_history(quiz_history)

    topic = ""
    if today_entry:
        topic = today_entry.get("topic", "")

    return {
        # Progress scalars
        "total_days": total_days,
        "current_day": tracker_state.get("current_day", 1),
        "days_done": days_done,
        "progress_pct": pct,
        "streak": tracker_state.get("streak", 0),
        # Quiz analysis
        "quiz_history": quiz_history,
        "quiz_avg": quiz_avg,
        "weak_topics": weak_topics,
        "strong_topics": strong_topics,
        # Structural data
        "tracks": tracker_state.get("tracks", []),
        "content": tracker_state.get("content", []),
        "gaps": config.get("gaps", []),
        "strengths": config.get("strengths", []),
        # Today
        "today_entry": today_entry or {},
        "topic": topic,
    }


def _analyse_quiz_history(
    quiz_history: list[dict[str, Any]],
) -> tuple[list[str], list[str], float]:
    """Derive weak/strong topics and average score from quiz history.

    Returns:
        (weak_topics, strong_topics, overall_avg_pct)
    """
    if not quiz_history:
        return [], [], 0.0

    topic_scores: dict[str, list[float]] = {}
    for q in quiz_history:
        total = q.get("total", 0)
        if total <= 0:
            continue
        pct = q.get("score", 0) / total * 100
        topic = q.get("topic", "unknown")
        topic_scores.setdefault(topic, []).append(pct)

    weak: list[str] = []
    strong: list[str] = []
    all_scores: list[float] = []

    for topic, scores in topic_scores.items():
        avg = sum(scores) / len(scores)
        all_scores.append(avg)
        if avg < 60:
            weak.append(topic)
        elif avg >= 80:
            strong.append(topic)

    overall_avg = sum(all_scores) / len(all_scores) if all_scores else 0.0
    return weak, strong, round(overall_avg, 1)


def config_as_model(config_dict: dict[str, Any]) -> PrepConfig | None:
    """Best-effort conversion of a config dict to a typed PrepConfig.

    Returns ``None`` if the dict doesn't match the Pydantic schema —
    callers should fall back to using the raw dict.
    """
    try:
        from prep_agent.models import PrepConfig

        return PrepConfig.model_validate(config_dict)
    except Exception:
        return None
