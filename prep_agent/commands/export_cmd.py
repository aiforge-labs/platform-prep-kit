"""
Export a full progress report.

Generates a comprehensive report including progress summary, completed
topics, quiz scores, and knowledge notes in Markdown or JSON format.
"""

import click
import json
import sys
from datetime import datetime
from pathlib import Path


@click.command("export")
@click.option(
    "--format", "fmt",
    type=click.Choice(["md", "json"], case_sensitive=False),
    default="md",
    help="Output format (default: md).",
)
@click.option(
    "--output", "-o",
    type=click.Path(),
    default=None,
    help="Output file path (defaults to ~/.prep/export-<date>.<fmt>).",
)
def export_cmd(fmt, output):
    """Export a full progress report."""
    try:
        from prep_agent.core.tracker import Tracker
        from prep_agent.core.config import load_config
        from prep_agent.core.knowledge import KnowledgeBase
        from prep_agent.utils.display import success, info, error
        from prep_agent.utils.file_ops import get_prep_dir
    except ImportError as exc:
        click.echo(f"Error: Missing dependency — {exc}", err=True)
        sys.exit(1)

    prep_dir = get_prep_dir()
    if not prep_dir.exists():
        error("No workspace found. Run 'prep init' first.")
        sys.exit(1)

    cfg = load_config()
    tracker = Tracker()
    tracker.load()
    progress = tracker.get_progress()
    kb = KnowledgeBase()

    # Build report data
    report_data = _build_report(cfg, progress, tracker, kb)

    # Determine output path
    if output:
        out_path = Path(output).expanduser()
    else:
        date_str = datetime.now().strftime("%Y-%m-%d")
        out_path = prep_dir / f"export-{date_str}.{fmt}"

    # Write in the requested format
    if fmt == "json":
        content = json.dumps(report_data, indent=2, default=str)
    else:
        content = _render_markdown(report_data)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(content, encoding="utf-8")

    success(f"Report exported to {out_path}")
    info(f"Format: {fmt.upper()}, Size: {len(content):,} bytes")


def _build_report(cfg, progress, tracker, kb):
    """Assemble all report data into a dictionary."""
    topics = kb.list_topics() or []
    knowledge = {}
    for t in topics:
        knowledge[t] = kb.get_topic(t)

    return {
        "generated_at": datetime.now().isoformat(),
        "summary": {
            "completed": progress.get("completed", 0),
            "total": progress.get("total", 0),
            "streak": progress.get("streak", 0),
            "percentage": (
                round(progress.get("completed", 0) / progress.get("total", 1) * 100, 1)
                if progress.get("total", 0) > 0
                else 0
            ),
        },
        "tracks": progress.get("tracks", {}),
        "completed_topics": progress.get("completed_topics", []),
        "quiz_history": progress.get("quiz_history", []),
        "weak_areas": progress.get("weak_areas", []),
        "knowledge_notes": knowledge,
        "config": {
            "timeline_weeks": cfg.get("timeline_weeks"),
            "daily_hours": cfg.get("daily_hours"),
            "gaps": cfg.get("gaps", []),
        },
    }


def _render_markdown(data):
    """Render the report data as a Markdown document."""
    lines = []
    s = data["summary"]

    lines.append("# Career Prep Progress Report")
    lines.append("")
    lines.append(f"Generated: {data['generated_at']}")
    lines.append("")

    # Summary
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- **Progress:** {s['completed']}/{s['total']} sessions ({s['percentage']}%)")
    lines.append(f"- **Streak:** {s['streak']} day(s)")
    lines.append("")

    # Tracks
    tracks = data.get("tracks", {})
    if tracks:
        lines.append("## Tracks")
        lines.append("")
        for track_name, track_info in tracks.items():
            done = track_info.get("completed", 0)
            total = track_info.get("total", 0)
            lines.append(f"- **{track_name}:** {done}/{total}")
        lines.append("")

    # Completed topics
    completed = data.get("completed_topics", [])
    if completed:
        lines.append("## Completed Topics")
        lines.append("")
        for topic in completed:
            name = topic if isinstance(topic, str) else topic.get("topic", "Unknown")
            lines.append(f"- {name}")
        lines.append("")

    # Quiz history
    quizzes = data.get("quiz_history", [])
    if quizzes:
        lines.append("## Quiz History")
        lines.append("")
        lines.append("| Date | Topic | Score |")
        lines.append("|------|-------|-------|")
        for q in quizzes:
            date = q.get("date", "")
            topic = q.get("topic", "")
            score = q.get("score", 0)
            total = q.get("total", 0)
            lines.append(f"| {date} | {topic} | {score}/{total} |")
        lines.append("")

    # Weak areas
    weak = data.get("weak_areas", [])
    if weak:
        lines.append("## Areas Needing Attention")
        lines.append("")
        for area in weak:
            lines.append(f"- {area}")
        lines.append("")

    # Knowledge notes
    notes = data.get("knowledge_notes", {})
    if notes:
        lines.append("## Knowledge Notes")
        lines.append("")
        for topic, content in sorted(notes.items()):
            lines.append(f"### {topic}")
            lines.append("")
            lines.append(content if content else "(empty)")
            lines.append("")

    return "\n".join(lines)
