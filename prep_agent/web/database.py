"""SQLite database layer for the web UI.

Provides a connection factory with WAL mode for concurrent CLI + web access,
schema creation, and version-tracked migrations.

Database location: ``~/.prep/prep.db``
"""

from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Generator

from prep_agent.utils.file_ops import get_prep_dir

_DB_NAME = "prep.db"

# Current schema version — bump when adding migrations.
SCHEMA_VERSION = 1

# ---------------------------------------------------------------------------
# Schema DDL
# ---------------------------------------------------------------------------

_SCHEMA_SQL = """\
CREATE TABLE IF NOT EXISTS config (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    data TEXT NOT NULL,
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS study_days (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    day_num INTEGER NOT NULL UNIQUE,
    date TEXT NOT NULL,
    week INTEGER NOT NULL,
    track_id TEXT NOT NULL,
    topic TEXT NOT NULL,
    morning_focus TEXT NOT NULL DEFAULT '',
    evening_focus TEXT NOT NULL DEFAULT '',
    is_review_day INTEGER NOT NULL DEFAULT 0,
    is_buffer_day INTEGER NOT NULL DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'done', 'skipped')),
    notes TEXT NOT NULL DEFAULT '',
    score INTEGER,
    minutes INTEGER,
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS tracks (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    start_day INTEGER,
    end_day INTEGER,
    status TEXT NOT NULL DEFAULT 'not_started'
        CHECK (status IN ('not_started', 'in_progress', 'completed')),
    confidence TEXT NOT NULL DEFAULT '-',
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS quiz_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic TEXT NOT NULL,
    score INTEGER NOT NULL,
    total INTEGER NOT NULL,
    percentage REAL NOT NULL,
    weak_areas TEXT NOT NULL DEFAULT '[]',
    answers TEXT NOT NULL DEFAULT '[]',
    timestamp TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS sessions (
    id TEXT PRIMARY KEY,
    session_type TEXT NOT NULL
        CHECK (session_type IN ('study', 'quiz', 'review', 'onboarding')),
    topic TEXT NOT NULL DEFAULT '',
    state TEXT NOT NULL DEFAULT '{}',
    started_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    completed_at TEXT
);

CREATE TABLE IF NOT EXISTS knowledge_progress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    knowledge_pack TEXT NOT NULL,
    section_id TEXT NOT NULL,
    section_title TEXT NOT NULL,
    completed INTEGER NOT NULL DEFAULT 0,
    completed_at TEXT,
    UNIQUE (knowledge_pack, section_id)
);

CREATE TABLE IF NOT EXISTS content_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    type TEXT NOT NULL DEFAULT 'blog',
    status TEXT NOT NULL DEFAULT 'not_started',
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS migrations (
    version INTEGER PRIMARY KEY,
    applied_at TEXT NOT NULL DEFAULT (datetime('now'))
);
"""

# ---------------------------------------------------------------------------
# Connection helpers
# ---------------------------------------------------------------------------


def get_db_path() -> Path:
    """Return the path to the SQLite database file."""
    return get_prep_dir() / _DB_NAME


def _configure_connection(conn: sqlite3.Connection) -> None:
    """Apply runtime PRAGMAs for performance and safety."""
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=5000")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.row_factory = sqlite3.Row


def get_connection(db_path: Path | None = None) -> sqlite3.Connection:
    """Open (or create) the database and return a raw connection.

    Caller is responsible for closing it.
    """
    path = db_path or get_db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    _configure_connection(conn)
    return conn


@contextmanager
def get_db(db_path: Path | None = None) -> Generator[sqlite3.Connection, None, None]:
    """Context manager that yields a configured SQLite connection.

    Commits on clean exit, rolls back on exception, always closes.
    """
    conn = get_connection(db_path)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Schema management
# ---------------------------------------------------------------------------


def init_schema(conn: sqlite3.Connection) -> None:
    """Create all tables if they don't exist."""
    conn.executescript(_SCHEMA_SQL)
    conn.commit()


def get_schema_version(conn: sqlite3.Connection) -> int:
    """Return the highest applied migration version, or 0 if none."""
    try:
        row = conn.execute(
            "SELECT MAX(version) FROM migrations"
        ).fetchone()
        return row[0] or 0
    except sqlite3.OperationalError:
        return 0


def set_schema_version(conn: sqlite3.Connection, version: int) -> None:
    """Record that *version* has been applied."""
    conn.execute(
        "INSERT OR REPLACE INTO migrations (version) VALUES (?)",
        (version,),
    )


def ensure_db(db_path: Path | None = None) -> Path:
    """Create the database file and schema if they don't already exist.

    Returns the database path.
    """
    path = db_path or get_db_path()
    with get_db(path) as conn:
        init_schema(conn)
    return path


# ---------------------------------------------------------------------------
# Generic helpers
# ---------------------------------------------------------------------------


def row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    """Convert a sqlite3.Row to a plain dict."""
    return dict(row)


def rows_to_dicts(rows: list[sqlite3.Row]) -> list[dict[str, Any]]:
    """Convert a list of sqlite3.Row objects to a list of plain dicts."""
    return [dict(r) for r in rows]
