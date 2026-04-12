"""
Show today's study plan at a glance.

Displays the current day's topic, tasks, and motivational streak info.
"""

import click
import sys


STREAK_MESSAGES = {
    0: "Today is day one. Let's go!",
    1: "Nice start — keep the momentum going.",
    3: "Three days strong. You're building a habit.",
    5: "Five-day streak! Consistency is your superpower.",
    7: "A full week! Impressive dedication.",
    14: "Two weeks of focused prep. You're in the zone.",
    21: "Three weeks — this is who you are now.",
    30: "A month of daily prep. Unstoppable.",
}


def _get_streak_message(streak: int) -> str:
    """Return the best motivational message for the current streak length."""
    best_key = 0
    for threshold in sorted(STREAK_MESSAGES.keys()):
        if streak >= threshold:
            best_key = threshold
    return STREAK_MESSAGES[best_key]


@click.command("today")
def today_cmd():
    """Show today's study topic, tasks, and streak."""
    try:
        from prep_agent.core.tracker import Tracker
        from prep_agent.core.config import load_config
        from prep_agent.utils.display import (
            print_today_card, print_agent_recommendations,
            print_reasoning_trace, success, info, warning, error,
        )
        from prep_agent.utils.file_ops import get_prep_dir
    except ImportError as exc:
        click.echo(f"Error: Missing dependency — {exc}", err=True)
        sys.exit(1)

    prep_dir = get_prep_dir()
    if not prep_dir.exists():
        error("No workspace found. Run 'prep init' first.")
        sys.exit(1)

    tracker = Tracker()
    tracker.load()
    cfg = load_config()

    today_entry = tracker.get_today()

    if today_entry is None:
        info("No study session scheduled for today.")
        # Try to find the next study day
        progress = tracker.get_progress()
        next_day = progress.get("next_study_day")
        total_days = progress.get("total_days", 0)
        if next_day:
            info(f"Next study day: {next_day}")
        elif total_days == 0:
            warning("Study plan is empty — run 'prep init' again to rebuild it.")
        else:
            success("All sessions complete — you're done with the plan!")
        return

    # Show the today card
    progress = tracker.get_progress()
    state = tracker.load()
    print_today_card(
        day_num=today_entry.get("day_num", 0),
        total_days=progress.get("days_total", 0),
        week=today_entry.get("week", 1),
        track=today_entry.get("track_id", today_entry.get("track", "")),
        topic=today_entry.get("topic", ""),
        morning=today_entry.get("morning_focus", "Study"),
        evening=today_entry.get("evening_focus", "Practice"),
        progress_pct=progress.get("pct", 0),
    )

    # Previous / next session context
    from datetime import date as dt_date
    today_str = dt_date.today().isoformat()
    prev_entry = None
    next_entry = None
    for d in state.get("days", []):
        if d["date"] < today_str:
            prev_entry = d
        elif d["date"] > today_str and next_entry is None:
            next_entry = d
    if prev_entry or next_entry:
        click.echo()
    if prev_entry:
        p_status = "done" if prev_entry.get("status") == "done" else "skipped"
        info(f"Previous: {prev_entry['topic']} ({p_status})")
    if next_entry:
        info(f"Up next:  {next_entry['topic']}")

    # Show quick-action hints
    topic_name = today_entry.get("topic", "")
    track_id = today_entry.get("track_id", "")
    quiz_bank = _find_quiz_bank(track_id, topic_name, cfg)
    click.echo()
    info("Quick actions:")
    click.echo(f"  prep study                  — study guide for today's topic")
    if quiz_bank:
        click.echo(f"  prep quiz --topic {quiz_bank:<16} — quiz yourself")
    else:
        click.echo(f"  prep quiz --list            — see available quiz banks")
    click.echo(f"  prep done                   — mark today complete")

    # Streak message
    streak = progress.get("streak", 0)
    if streak > 0:
        click.echo()
        msg = _get_streak_message(streak)
        info(f"Current streak: {streak} day{'s' if streak != 1 else ''} — {msg}")

    # Agent-powered recommendations
    try:
        from prep_agent.agents.orchestrator import Orchestrator
        from prep_agent.agents.context import build_agent_context

        ctx = build_agent_context(tracker.load(), cfg, today_entry)
        orchestrator = Orchestrator(cfg)
        result = orchestrator.handle_session("today", ctx)

        # Show planner adjustment if any
        plan = result.get("plan", {})
        adjustment = plan.get("adjustment", "")
        if adjustment and adjustment != "Plan continues as scheduled.":
            click.echo()
            info(f"Planner: {adjustment}")

        # Show reviewer recommendations if triggered
        review = result.get("review")
        if review and review.get("recommendations"):
            print_agent_recommendations(review["recommendations"])
    except Exception:
        pass  # Agent integration is best-effort; never break the core flow

    # If already done today
    if today_entry.get("status") == "done":
        click.echo()
        success("You've already completed today's session. Great work!")


def _find_quiz_bank(track_id: str, topic_name: str, cfg: dict) -> str | None:
    """Look up the quiz_bank for today's topic from the active template."""
    try:
        from prep_agent.core.templates import TemplateLoader
        template_id = cfg.get("template") or cfg.get("target", {}).get("template")
        if not template_id:
            return None
        tl = TemplateLoader()
        tmpl = tl.load_template(template_id)
        for track in tmpl.get("tracks", []):
            if track.get("id") == track_id:
                for topic in track.get("topics", []):
                    if topic.get("quiz_bank"):
                        return topic["quiz_bank"]
            for topic in track.get("topics", []):
                if topic.get("name") == topic_name and topic.get("quiz_bank"):
                    return topic["quiz_bank"]
    except Exception:
        pass
    return None
