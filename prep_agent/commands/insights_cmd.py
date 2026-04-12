"""
Generate progress insights and recommendations.

Analyzes study pace, quiz performance, and consistency to produce
actionable recommendations.
"""

import click
import sys
from collections import defaultdict
from datetime import date, timedelta


@click.command("insights")
def insights_cmd():
    """Show progress insights and recommendations."""
    try:
        from prep_agent.core.tracker import Tracker
        from prep_agent.core.config import load_config
        from prep_agent.core.quiz_engine import QuizEngine
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
    state = tracker.load()
    progress = tracker.get_progress()
    cfg = load_config()

    try:
        from rich.console import Console
        from rich.panel import Panel
        from rich.table import Table
        console = Console()
    except ImportError:
        console = None

    days = state.get("days", [])
    total_days = progress.get("total_days", 1)
    completed = progress.get("completed_days", 0)
    streak = progress.get("streak", 0)
    study_hours = progress.get("study_hours")

    # ---- Pace analysis ----
    start_date_str = state.get("start_date", "")
    if start_date_str:
        start = date.fromisoformat(start_date_str)
        elapsed = (date.today() - start).days + 1
    else:
        elapsed = 1

    # Expected progress based on elapsed time
    study_days_in_plan = [d for d in days if d.get("date", "") <= date.today().isoformat()]
    expected_done = len(study_days_in_plan)
    if expected_done > 0:
        pace_ratio = completed / expected_done
    else:
        pace_ratio = 1.0

    if pace_ratio >= 0.9:
        pace = "on track"
        pace_color = "green"
    elif pace_ratio >= 0.7:
        pace = "slightly behind"
        pace_color = "yellow"
    else:
        pace = "behind schedule"
        pace_color = "red"

    # ---- Quiz analysis ----
    engine = QuizEngine()
    history = engine.get_history(limit=100)

    topic_scores: dict[str, list[float]] = defaultdict(list)
    for q in history:
        total_q = q.get("total", 0)
        if total_q > 0:
            topic_scores[q["topic"]].append(q["score"] / total_q * 100)

    strongest = sorted(
        topic_scores.items(),
        key=lambda x: sum(x[1]) / len(x[1]),
        reverse=True,
    )[:3]

    weakest = sorted(
        topic_scores.items(),
        key=lambda x: sum(x[1]) / len(x[1]),
    )[:3]

    # ---- Consistency ----
    avg_hours = round(study_hours / completed, 1) if study_hours and completed else None

    # ---- Recommendations ----
    recs = []
    if pace_ratio < 0.7:
        recs.append(f"You're {pace}. Consider adding extra study time or compressing low-priority tracks.")
    if weakest and sum(weakest[0][1]) / len(weakest[0][1]) < 50:
        recs.append(f"Focus on '{weakest[0][0]}' — your weakest area ({sum(weakest[0][1]) / len(weakest[0][1]):.0f}% avg). Run: prep study --weak")
    if streak == 0 and completed > 0:
        recs.append("Your streak broke. Get back on track today — consistency matters more than perfection.")
    if streak >= 7:
        recs.append(f"Amazing {streak}-day streak! Keep the momentum going.")
    if not history:
        recs.append("No quizzes taken yet. Run: prep quiz --topic <topic> to test your knowledge.")
    if len(recs) == 0:
        recs.append("You're doing great! Keep up the consistent study sessions.")

    # ---- Display ----
    if console:
        # Header
        console.print()
        console.print(Panel(
            f"[bold]Progress Insights[/bold]\n"
            f"Day {completed}/{total_days} | Week {progress.get('current_week', '?')} | "
            f"Elapsed: {elapsed} days",
            border_style="cyan",
            expand=False,
        ))

        # Pace
        console.print(f"\n[bold]Pace:[/bold] [{pace_color}]{pace}[/{pace_color}] "
                       f"({completed}/{expected_done} expected sessions completed)")

        # Study consistency
        console.print(f"[bold]Streak:[/bold] {streak} days")
        if study_hours:
            console.print(f"[bold]Total study time:[/bold] {study_hours}h"
                           + (f" ({avg_hours}h/session avg)" if avg_hours else ""))

        # Quiz performance
        if topic_scores:
            console.print("\n[bold green]Strongest Topics[/bold green]")
            for topic, scores in strongest:
                avg = sum(scores) / len(scores)
                console.print(f"  [green]+[/green] {topic}: {avg:.0f}% ({len(scores)} quiz{'es' if len(scores) > 1 else ''})")

            console.print("\n[bold red]Weakest Topics[/bold red]")
            for topic, scores in weakest:
                avg = sum(scores) / len(scores)
                console.print(f"  [red]-[/red] {topic}: {avg:.0f}% ({len(scores)} quiz{'es' if len(scores) > 1 else ''})")

        # Recommendations
        console.print()
        console.print(Panel(
            "\n".join(f"  [yellow]>[/yellow] {r}" for r in recs),
            title="[bold cyan]Recommendations[/bold cyan]",
            border_style="cyan",
            expand=False,
        ))
    else:
        # Fallback plain text
        click.echo(f"\nProgress Insights — Day {completed}/{total_days}")
        click.echo(f"Pace: {pace} ({completed}/{expected_done} expected)")
        click.echo(f"Streak: {streak} days")
        if study_hours:
            click.echo(f"Study time: {study_hours}h")
        click.echo("\nRecommendations:")
        for r in recs:
            click.echo(f"  > {r}")
