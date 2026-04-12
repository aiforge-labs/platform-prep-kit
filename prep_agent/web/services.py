"""Service layer — bridges web routes to core modules + SQLite.

Every function here reads from SQLite (fast, structured) and writes through
to both SQLite and tracker.md (so the CLI stays in sync).
"""

from __future__ import annotations

import json
import sqlite3
from datetime import date, datetime
from typing import Any

from prep_agent.web.database import get_db, rows_to_dicts
from prep_agent.web.migrate import sync_to_markdown, snapshot_tracker_mtime


# ---------------------------------------------------------------------------
# Read helpers
# ---------------------------------------------------------------------------


def get_config() -> dict[str, Any]:
    """Return the current config dict from SQLite."""
    with get_db() as conn:
        row = conn.execute("SELECT data FROM config WHERE id = 1").fetchone()
    if row:
        return json.loads(row["data"])
    return {}


def get_progress() -> dict[str, Any]:
    """Calculate overall progress metrics from SQLite."""
    with get_db() as conn:
        days = rows_to_dicts(
            conn.execute("SELECT * FROM study_days ORDER BY day_num").fetchall()
        )
        tracks = rows_to_dicts(
            conn.execute("SELECT * FROM tracks ORDER BY id").fetchall()
        )
        quizzes = rows_to_dicts(
            conn.execute("SELECT * FROM quiz_results ORDER BY timestamp").fetchall()
        )

    done = [d for d in days if d["status"] == "done"]
    total = len(days)
    pct = round(len(done) / total * 100, 1) if total else 0.0

    scores = [q["percentage"] for q in quizzes if q.get("percentage")]
    avg_score = round(sum(scores) / len(scores), 1) if scores else 0.0

    total_minutes = sum(d.get("minutes") or 0 for d in done)
    study_hours = round(total_minutes / 60, 1) if total_minutes else 0.0

    # Per-track breakdown
    track_map: dict[str, dict[str, Any]] = {}
    for d in days:
        tid = d.get("track_id", "")
        if not tid:
            continue
        if tid not in track_map:
            name = tid
            for t in tracks:
                if t["id"] == tid:
                    name = t["name"]
                    break
            track_map[tid] = {"id": tid, "name": name, "done": 0, "total": 0}
        track_map[tid]["total"] += 1
        if d["status"] == "done":
            track_map[tid]["done"] += 1

    # Next study day
    today_str = date.today().isoformat()
    next_study_day = None
    for d in days:
        if d["status"] == "pending" and d["date"] > today_str:
            next_study_day = d["date"]
            break

    return {
        "completed_days": len(done),
        "total_days": total,
        "progress_pct": pct,
        "streak": _calc_streak(days),
        "study_hours": study_hours,
        "quizzes_taken": len(quizzes),
        "avg_score": avg_score,
        "tracks": tracks,
        "track_progress": list(track_map.values()),
        "days": days,
        "quiz_history": quizzes,
        "next_study_day": next_study_day,
    }


def get_today() -> dict[str, Any] | None:
    """Return today's study day entry, or None."""
    today_str = date.today().isoformat()
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM study_days WHERE date = ?", (today_str,)
        ).fetchone()
    if row:
        return dict(row)
    return None


def get_study_days(
    week: int | None = None,
    track_id: str | None = None,
) -> list[dict[str, Any]]:
    """Return study days with optional filters."""
    query = "SELECT * FROM study_days WHERE 1=1"
    params: list[Any] = []
    if week is not None:
        query += " AND week = ?"
        params.append(week)
    if track_id:
        query += " AND track_id = ?"
        params.append(track_id)
    query += " ORDER BY day_num"

    with get_db() as conn:
        return rows_to_dicts(conn.execute(query, params).fetchall())


def get_tracks() -> list[dict[str, Any]]:
    """Return all tracks."""
    with get_db() as conn:
        return rows_to_dicts(
            conn.execute("SELECT * FROM tracks ORDER BY id").fetchall()
        )


def get_quiz_history(limit: int = 50) -> list[dict[str, Any]]:
    """Return recent quiz results."""
    with get_db() as conn:
        return rows_to_dicts(
            conn.execute(
                "SELECT * FROM quiz_results ORDER BY timestamp DESC LIMIT ?",
                (limit,),
            ).fetchall()
        )


# ---------------------------------------------------------------------------
# Write helpers
# ---------------------------------------------------------------------------


def mark_day_done(
    day_num: int,
    notes: str = "",
    score: int | None = None,
    minutes: int | None = None,
) -> None:
    """Mark a study day as done and sync to markdown."""
    with get_db() as conn:
        conn.execute(
            """UPDATE study_days
               SET status = 'done', notes = ?, score = ?, minutes = ?,
                   updated_at = datetime('now')
               WHERE day_num = ?""",
            (notes, score, minutes, day_num),
        )
        sync_to_markdown(conn)
    snapshot_tracker_mtime()


def save_day_notes(day_num: int, notes: str) -> None:
    """Update notes for a study day."""
    with get_db() as conn:
        conn.execute(
            "UPDATE study_days SET notes = ?, updated_at = datetime('now') WHERE day_num = ?",
            (notes, day_num),
        )
        sync_to_markdown(conn)
    snapshot_tracker_mtime()


def log_quiz_result(
    topic: str,
    score: int,
    total: int,
    weak_areas: list[str] | None = None,
) -> None:
    """Log a quiz result to SQLite and sync."""
    pct = round(score / total * 100, 1) if total else 0.0
    with get_db() as conn:
        conn.execute(
            """INSERT INTO quiz_results (topic, score, total, percentage, weak_areas)
               VALUES (?, ?, ?, ?, ?)""",
            (topic, score, total, pct, json.dumps(weak_areas or [])),
        )
        sync_to_markdown(conn)
    snapshot_tracker_mtime()


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _calc_streak(days: list[dict[str, Any]]) -> int:
    """Calculate consecutive completed days backwards from today."""
    today_str = date.today().isoformat()
    past = sorted(
        [d for d in days if d.get("date", "") <= today_str],
        key=lambda d: d.get("date", ""),
        reverse=True,
    )
    streak = 0
    for d in past:
        if d.get("status") == "done":
            streak += 1
        else:
            break
    return streak
