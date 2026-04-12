"""
Display the full prep status dashboard.

Shows overall progress, track breakdown, quiz history, streak info,
and weak areas that need more attention.
"""

import click
import sys


@click.command("status")
def status_cmd():
    """Show the full progress dashboard."""
    try:
        from prep_agent.core.tracker import Tracker
        from prep_agent.core.config import load_config
        from prep_agent.utils.display import (
            print_status_dashboard, print_agent_recommendations, error,
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
    state = tracker.load()

    progress = tracker.get_progress()
    print_status_dashboard(progress)

    # Agent-powered review recommendations
    try:
        from prep_agent.agents.orchestrator import Orchestrator
        from prep_agent.agents.context import build_agent_context

        cfg = load_config()
        ctx = build_agent_context(state, cfg)
        orchestrator = Orchestrator(cfg)
        result = orchestrator.handle_session("review", ctx)

        review = result.get("review", {})
        recs = review.get("recommendations", [])
        if recs:
            print_agent_recommendations(recs)
    except Exception:
        pass  # Agent integration is best-effort
