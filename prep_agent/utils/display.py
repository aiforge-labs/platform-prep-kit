"""
Terminal display utilities built on the *rich* library.

Every public function in this module writes directly to the console.
They are intentionally stateless so callers never need to manage a
``Console`` instance.
"""

from __future__ import annotations

from typing import Any, Sequence

from rich.console import Console
from rich.panel import Panel
from rich.progress import BarColumn, Progress, TextColumn
from rich.table import Table
from rich.text import Text

console = Console()

APP_NAME = "Career Prep Agent"
APP_VERSION = "0.1.0"

# ------------------------------------------------------------------
# Banner
# ------------------------------------------------------------------

def print_banner() -> None:
    """Display the application name and version in a styled banner."""
    title = Text(f"{APP_NAME}  v{APP_VERSION}", style="bold cyan")
    console.print(Panel(title, border_style="bright_blue", expand=False))


# ------------------------------------------------------------------
# Today card
# ------------------------------------------------------------------

def print_today_card(
    day_num: int,
    total_days: int,
    week: int,
    track: str,
    topic: str,
    morning: str,
    evening: str,
    progress_pct: float,
) -> None:
    """Render a rich panel summarising today's study plan."""
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("key", style="bold white", no_wrap=True)
    table.add_column("value", style="white")

    table.add_row("Day", f"{day_num} / {total_days}")
    table.add_row("Week", str(week))
    table.add_row("Track", track)
    table.add_row("Topic", topic)
    table.add_row("Morning", morning)
    table.add_row("Evening", evening)

    bar = _inline_bar(progress_pct)
    table.add_row("Progress", bar)

    console.print(
        Panel(
            table,
            title=f"[bold green]Day {day_num}[/bold green]",
            border_style="green",
            expand=False,
        )
    )


# ------------------------------------------------------------------
# Status dashboard
# ------------------------------------------------------------------

def print_status_dashboard(tracker_data: dict[str, Any]) -> None:
    """Print an overall progress dashboard from *tracker_data*.

    Expected keys (all optional — missing keys are silently skipped):
        completed_days, total_days, current_week, total_weeks,
        topics_done, topics_total, streak, study_hours,
        tracks (list of dicts with name / done / total).
    """
    summary = Table(title="Preparation Status", show_header=False, box=None, padding=(0, 2))
    summary.add_column("metric", style="bold cyan")
    summary.add_column("value")

    days_done = tracker_data.get("completed_days", 0)
    total_days = tracker_data.get("total_days", 1)
    pct = (days_done / total_days) * 100 if total_days else 0

    summary.add_row("Days completed", f"{days_done} / {total_days}  ({pct:.0f}%)")
    summary.add_row("Current week", str(tracker_data.get("current_week", "—")))
    summary.add_row("Topics covered", f"{tracker_data.get('topics_done', 0)} / {tracker_data.get('topics_total', '—')}")
    summary.add_row("Current streak", f"{tracker_data.get('streak', 0)} days")

    study_hours = tracker_data.get("study_hours")
    summary.add_row("Total study hours", f"{study_hours}h" if study_hours else "—")

    est_end = tracker_data.get("est_end_date")
    if est_end:
        summary.add_row("Estimated completion", est_end)

    quizzes_taken = tracker_data.get("quizzes_taken", 0)
    if quizzes_taken > 0:
        avg_score = tracker_data.get("avg_score", 0.0)
        summary.add_row("Quizzes taken", str(quizzes_taken))
        summary.add_row("Average score", f"{avg_score:.0f}%")
        weakest = tracker_data.get("weakest_topic")
        if weakest:
            summary.add_row("Weakest topic", weakest)

    console.print(Panel(summary, border_style="bright_blue", expand=False))

    # Per-track breakdown (if provided)
    tracks: Sequence[dict[str, Any]] = tracker_data.get("tracks", [])
    if tracks:
        track_table = Table(title="Track Breakdown")
        track_table.add_column("Track", style="bold")
        track_table.add_column("Done", justify="right")
        track_table.add_column("Total", justify="right")
        track_table.add_column("Progress")

        for t in tracks:
            done = t.get("done", 0)
            total = t.get("total", 1)
            track_table.add_row(
                t.get("name", "?"),
                str(done),
                str(total),
                _inline_bar((done / total) * 100 if total else 0),
            )

        console.print(track_table)


# ------------------------------------------------------------------
# Fitment report
# ------------------------------------------------------------------

def print_fitment_report(analysis: dict[str, Any]) -> None:
    """Display a fitment score with colour-coded strengths and gaps.

    Expected keys:
        score (int 0-100), strengths (list[str]), gaps (list[str]),
        recommendations (list[str]).
    """
    score = analysis.get("score", 0)
    colour = "green" if score >= 75 else "yellow" if score >= 50 else "red"

    console.print(
        Panel(
            Text(f"Fitment Score: {score}%", style=f"bold {colour}"),
            border_style=colour,
            expand=False,
        )
    )

    # Strengths
    strengths = analysis.get("strengths", [])
    if strengths:
        console.print("\n[bold green]Strengths[/bold green]")
        for s in strengths:
            console.print(f"  [green]+[/green] {s}")

    # Gaps
    gaps = analysis.get("gaps", [])
    if gaps:
        console.print("\n[bold red]Gaps[/bold red]")
        for g in gaps:
            console.print(f"  [red]-[/red] {g}")

    # Recommendations
    recs = analysis.get("recommendations", [])
    if recs:
        console.print("\n[bold cyan]Recommendations[/bold cyan]")
        for i, r in enumerate(recs, 1):
            console.print(f"  {i}. {r}")


# ------------------------------------------------------------------
# Quiz result
# ------------------------------------------------------------------

def print_quiz_result(
    score: int,
    total: int,
    topic: str,
    weak_areas: Sequence[str] | None = None,
) -> None:
    """Show quiz results with pass/fail colouring."""
    pct = (score / total) * 100 if total else 0
    colour = "green" if pct >= 70 else "yellow" if pct >= 50 else "red"

    console.print(
        Panel(
            Text(f"{score}/{total}  ({pct:.0f}%)", style=f"bold {colour}"),
            title=f"Quiz: {topic}",
            border_style=colour,
            expand=False,
        )
    )

    if weak_areas:
        console.print("[bold yellow]Areas to revisit:[/bold yellow]")
        for area in weak_areas:
            console.print(f"  - {area}")


# ------------------------------------------------------------------
# Reusable progress bar
# ------------------------------------------------------------------

def progress_bar(current: int, total: int, label: str = "") -> None:
    """Render a one-shot progress bar to the console."""
    with Progress(
        TextColumn("[bold blue]{task.description}"),
        BarColumn(bar_width=40),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        console=console,
        transient=True,
    ) as prog:
        task = prog.add_task(label, total=total, completed=current)
        prog.refresh()


# ------------------------------------------------------------------
# Styled messages
# ------------------------------------------------------------------

def success(msg: str) -> None:
    """Print a green success message."""
    console.print(f"[bold green]OK[/bold green] {msg}")


def warning(msg: str) -> None:
    """Print a yellow warning message."""
    console.print(f"[bold yellow]WARN[/bold yellow] {msg}")


def error(msg: str) -> None:
    """Print a red error message."""
    console.print(f"[bold red]ERR[/bold red] {msg}")


def info(msg: str) -> None:
    """Print a cyan informational message."""
    console.print(f"[bold cyan]INFO[/bold cyan] {msg}")


# ------------------------------------------------------------------
# Agent output
# ------------------------------------------------------------------

def print_agent_recommendations(recommendations: list[str]) -> None:
    """Display agent recommendations in a styled panel."""
    if not recommendations:
        return
    items = "\n".join(f"  [bold yellow]>[/bold yellow] {r}" for r in recommendations)
    console.print(
        Panel(
            items,
            title="[bold cyan]Agent Recommendations[/bold cyan]",
            border_style="cyan",
            expand=False,
        )
    )


def print_reasoning_trace(trace: list[dict]) -> None:
    """Display agent reasoning trace for transparency."""
    if not trace:
        return
    console.print("\n[dim]Agent reasoning:[/dim]")
    for entry in trace[-3:]:
        action = entry.get("action", "?")
        reasoning = entry.get("reasoning", "")
        console.print(f"  [dim]{action}:[/dim] {reasoning}")


# ------------------------------------------------------------------
# Internal helpers
# ------------------------------------------------------------------

def _inline_bar(pct: float, width: int = 20) -> str:
    """Return a text-based bar like ``[=========>          ] 48%``."""
    filled = int(width * pct / 100)
    empty = width - filled
    return f"[{'=' * filled}{'>' if empty else ''}{'.' * max(0, empty - 1)}] {pct:.0f}%"
