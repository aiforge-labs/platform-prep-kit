"""
Mark today's study session as complete.

Logs completion, optional notes, confidence score, and updates the streak.
"""

import click
import sys


@click.command("done")
@click.option("--notes", type=str, default=None, help="Notes about what you studied or learned.")
@click.option("--score", type=click.IntRange(1, 10), default=None, help="Self-assessed confidence score (1-10).")
@click.option("--minutes", type=click.IntRange(1, 480), default=None, help="Minutes spent studying (1-480).")
def done_cmd(notes, score, minutes):
    """Mark today's study session as done."""
    try:
        from prep_agent.core.tracker import Tracker
        from prep_agent.utils.display import success, info, warning, error
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

    today_entry = tracker.get_today()
    if today_entry is None:
        warning("No study session scheduled for today.")
        progress = tracker.get_progress()
        next_day = progress.get("next_study_day")
        if next_day:
            info(f"Next study session: {next_day}")
        else:
            info("No more sessions — you've completed the plan!")
        return

    if today_entry.get("status") == "done":
        if not click.confirm("Today is already marked done. Update it?", default=False):
            return

    # Prompt for notes interactively if not provided
    if notes is None:
        notes = click.prompt("Any notes? (press Enter to skip)", default="", show_default=False)
        if not notes.strip():
            notes = None

    # Prompt for score interactively if not provided
    if score is None:
        raw = click.prompt(
            "Confidence score 1-10? (press Enter to skip)",
            default="",
            show_default=False,
        )
        if raw.strip():
            try:
                score = int(raw.strip())
                if not 1 <= score <= 10:
                    warning("Score must be 1-10. Skipping.")
                    score = None
            except ValueError:
                warning("Invalid number. Skipping score.")
                score = None

    # Prompt for minutes interactively if not provided
    if minutes is None:
        raw = click.prompt(
            "Minutes studied? (press Enter to skip)",
            default="",
            show_default=False,
        )
        if raw.strip():
            try:
                minutes = int(raw.strip())
                if not 1 <= minutes <= 480:
                    warning("Minutes must be 1-480. Skipping.")
                    minutes = None
            except ValueError:
                warning("Invalid number. Skipping minutes.")
                minutes = None

    # Mark done
    tracker.mark_done(notes=notes, score=score, minutes=minutes)

    # Show result
    progress = tracker.get_progress()
    streak = progress.get("streak", 0)
    completed = progress.get("completed_days", 0)
    total = progress.get("total_days", 0)
    pct = (completed / total * 100) if total > 0 else 0

    click.echo()
    success(f"Session complete! Topic: {today_entry.get('topic', 'Unknown')}")
    if notes:
        info(f"Notes: {notes}")
    if score is not None:
        info(f"Confidence: {score}/10")
    if minutes is not None:
        info(f"Time spent: {minutes} min")

    click.echo()
    info(f"Progress: {completed}/{total} sessions ({pct:.0f}%)")
    info(f"Streak: {streak} day{'s' if streak != 1 else ''}")

    # Milestone celebrations
    if streak in (3, 5, 7, 14, 21, 30):
        click.echo()
        success(f"Milestone reached: {streak}-day streak!")

    if pct >= 100:
        click.echo()
        success("You've completed the entire study plan. Congratulations!")
    elif pct >= 75:
        info("Almost there — the home stretch!")
    elif pct >= 50:
        info("Halfway done. Keep pushing!")

    # Adaptive plan adjustment (best-effort)
    try:
        from prep_agent.agents.planner import PlannerAgent
        from prep_agent.agents.context import build_agent_context
        from prep_agent.core.config import load_config

        cfg = load_config()
        ctx = build_agent_context(tracker.load(), cfg, today_entry)
        planner = PlannerAgent(cfg)
        result = planner.adjust_plan(ctx, tracker)
        for adj in result.get("adjustments", []):
            click.echo()
            info(f"Plan adjusted: {adj}")
    except Exception:
        pass
