"""Migration between markdown state files and SQLite.

Handles:
- Initial import: markdown/YAML/JSON  ->  SQLite  (first ``prep serve``)
- Write-through:  SQLite mutation      ->  regenerate tracker.md
- CLI sync:       tracker.md changed   ->  re-import to SQLite
"""

from __future__ import annotations

import json
import os
import sqlite3
from pathlib import Path
from typing import Any

from prep_agent.utils.file_ops import get_prep_dir
from prep_agent.web.database import (
    SCHEMA_VERSION,
    ensure_db,
    get_db,
    get_db_path,
    get_schema_version,
    init_schema,
    set_schema_version,
)


# ---------------------------------------------------------------------------
# Import: markdown / YAML / JSON  ->  SQLite
# ---------------------------------------------------------------------------


def needs_migration(db_path: Path | None = None) -> bool:
    """Return True if the database has not been populated yet."""
    path = db_path or get_db_path()
    if not path.exists():
        return True
    with get_db(path) as conn:
        version = get_schema_version(conn)
        if version < SCHEMA_VERSION:
            return True
        row = conn.execute("SELECT COUNT(*) FROM study_days").fetchone()
        return row[0] == 0


def run_migration(db_path: Path | None = None) -> None:
    """Import all existing state files into SQLite.

    Safe to call multiple times — clears and re-imports.
    """
    prep_dir = get_prep_dir()
    path = ensure_db(db_path)

    with get_db(path) as conn:
        _import_config(conn, prep_dir)
        _import_tracker(conn, prep_dir)
        _import_quiz_history(conn, prep_dir)
        set_schema_version(conn, SCHEMA_VERSION)


def _import_config(conn: sqlite3.Connection, prep_dir: Path) -> None:
    """Load config.yml and insert into the ``config`` table."""
    from prep_agent.core.config import load_config

    cfg = load_config()
    if not cfg:
        return

    conn.execute("DELETE FROM config")
    conn.execute(
        "INSERT INTO config (id, data) VALUES (1, ?)",
        (json.dumps(cfg, default=str),),
    )


def _import_tracker(conn: sqlite3.Connection, prep_dir: Path) -> None:
    """Load tracker.md and populate ``study_days``, ``tracks``,
    ``content_items`` tables."""
    tracker_path = prep_dir / "tracker.md"
    if not tracker_path.exists():
        return

    from prep_agent.core.tracker import Tracker

    tracker = Tracker(str(prep_dir))
    state = tracker.load()

    # --- study_days ---
    conn.execute("DELETE FROM study_days")
    for d in state.get("days", []):
        conn.execute(
            """INSERT INTO study_days
               (day_num, date, week, track_id, topic, status, notes, score, minutes)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                d.get("day_num", 0),
                d.get("date", ""),
                d.get("week", 1),
                d.get("track_id", ""),
                d.get("topic", ""),
                d.get("status", "pending"),
                d.get("notes", ""),
                int(d["score"]) if str(d.get("score", "")).isdigit() else None,
                int(d["minutes"]) if str(d.get("minutes", "")).isdigit() else None,
            ),
        )

    # --- tracks ---
    conn.execute("DELETE FROM tracks")
    for t in state.get("tracks", []):
        conn.execute(
            """INSERT INTO tracks (id, name, status, confidence)
               VALUES (?, ?, ?, ?)""",
            (
                t.get("id", t.get("name", "").lower().replace(" ", "-")),
                t.get("name", ""),
                t.get("status", "not_started").replace(" ", "_"),
                t.get("confidence", "-"),
            ),
        )

    # --- content_items ---
    conn.execute("DELETE FROM content_items")
    for c in state.get("content", []):
        conn.execute(
            "INSERT INTO content_items (title, status) VALUES (?, ?)",
            (c.get("title", ""), c.get("status", "not_started")),
        )


def _import_quiz_history(conn: sqlite3.Connection, prep_dir: Path) -> None:
    """Load quiz-history.json and populate ``quiz_results``."""
    history_path = prep_dir / "quiz-history.json"
    if not history_path.exists():
        return

    try:
        with open(history_path) as f:
            entries = json.load(f)
    except (json.JSONDecodeError, OSError):
        return

    if not isinstance(entries, list):
        return

    conn.execute("DELETE FROM quiz_results")
    for entry in entries:
        score = entry.get("score", 0)
        total = entry.get("total", 0)
        pct = entry.get("percentage", (score / total * 100) if total else 0.0)
        conn.execute(
            """INSERT INTO quiz_results
               (topic, score, total, percentage, weak_areas, timestamp)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (
                entry.get("topic", ""),
                score,
                total,
                pct,
                json.dumps(entry.get("weak_areas", [])),
                entry.get("timestamp", ""),
            ),
        )


# ---------------------------------------------------------------------------
# Write-through: SQLite  ->  tracker.md
# ---------------------------------------------------------------------------


def sync_to_markdown(conn: sqlite3.Connection | None = None) -> None:
    """Regenerate ``tracker.md`` from the current SQLite state.

    This keeps the CLI in sync after web-side mutations.
    """
    from prep_agent.core.tracker import Tracker

    prep_dir = get_prep_dir()

    if conn is None:
        from prep_agent.web.database import get_db as _get_db
        with _get_db() as c:
            state = _build_state_from_db(c)
    else:
        state = _build_state_from_db(conn)

    tracker = Tracker(str(prep_dir))
    md = tracker._generate_tracker_md(state)
    with open(tracker.tracker_path, "w") as f:
        f.write(md)


def _build_state_from_db(conn: sqlite3.Connection) -> dict[str, Any]:
    """Reconstruct the tracker state dict from SQLite tables.

    The shape matches what ``Tracker._generate_tracker_md()`` expects.
    """
    days_rows = conn.execute(
        "SELECT * FROM study_days ORDER BY day_num"
    ).fetchall()
    tracks_rows = conn.execute("SELECT * FROM tracks ORDER BY id").fetchall()
    content_rows = conn.execute("SELECT * FROM content_items ORDER BY id").fetchall()
    quiz_rows = conn.execute(
        "SELECT * FROM quiz_results ORDER BY timestamp"
    ).fetchall()

    days = []
    for r in days_rows:
        days.append({
            "day_num": r["day_num"],
            "date": r["date"],
            "week": r["week"],
            "status": r["status"],
            "track_id": r["track_id"],
            "topic": r["topic"],
            "notes": r["notes"] or "",
            "score": str(r["score"]) if r["score"] is not None else "",
            "minutes": str(r["minutes"]) if r["minutes"] is not None else "",
        })

    tracks = []
    for r in tracks_rows:
        tracks.append({
            "id": r["id"],
            "name": r["name"],
            "status": r["status"].replace("_", " "),
            "confidence": r["confidence"],
        })

    content = []
    for r in content_rows:
        content.append({"title": r["title"], "status": r["status"]})

    quiz_history = []
    for r in quiz_rows:
        quiz_history.append({
            "date": r["timestamp"][:10] if r["timestamp"] else "",
            "topic": r["topic"],
            "score": r["score"],
            "total": r["total"],
        })

    done_count = sum(1 for d in days if d["status"] == "done")
    total = len(days)

    # Find current_day (first pending)
    current_day = 1
    for d in days:
        if d["status"] == "pending":
            current_day = d["day_num"]
            break

    # Compute weeks
    weeks = set()
    for d in days:
        weeks.add(d.get("week", 1))

    return {
        "current_day": current_day,
        "total_days": total,
        "current_week": min(weeks) if weeks else 1,
        "total_weeks": len(weeks) if weeks else 1,
        "start_date": days[0]["date"] if days else "",
        "streak": 0,
        "last_completed_day": max(
            (d["day_num"] for d in days if d["status"] == "done"), default=0
        ),
        "days": days,
        "tracks": tracks,
        "content": content,
        "quiz_history": quiz_history,
    }


# ---------------------------------------------------------------------------
# CLI -> Web sync: detect tracker.md changes
# ---------------------------------------------------------------------------

_tracker_mtime: float = 0.0


def check_cli_sync(db_path: Path | None = None) -> bool:
    """Re-import tracker.md if it was modified since the last check.

    Returns True if a re-import happened.
    """
    global _tracker_mtime

    tracker_path = get_prep_dir() / "tracker.md"
    if not tracker_path.exists():
        return False

    current_mtime = tracker_path.stat().st_mtime
    if current_mtime <= _tracker_mtime:
        return False

    _tracker_mtime = current_mtime
    path = db_path or get_db_path()
    with get_db(path) as conn:
        _import_tracker(conn, get_prep_dir())
    return True


def snapshot_tracker_mtime() -> None:
    """Record the current tracker.md mtime so the next check_cli_sync()
    doesn't re-import our own write-through."""
    global _tracker_mtime
    tracker_path = get_prep_dir() / "tracker.md"
    if tracker_path.exists():
        _tracker_mtime = tracker_path.stat().st_mtime
