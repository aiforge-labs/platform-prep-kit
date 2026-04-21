"""
File-system operations for the platform-prep-kit.

The canonical data directory is ``~/.prep/``.  All read/write helpers
handle missing parents gracefully and use UTF-8 encoding.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

# ------------------------------------------------------------------
# Prep directory
# ------------------------------------------------------------------

_PREP_DIR = Path.home() / ".prep"

_SUBDIRS: list[str] = [
    "plans",
    "notes",
    "quizzes",
    "exports",
    "logs",
    "projects",
    "uploads",
]


def get_prep_dir() -> Path:
    """Return the path to ``~/.prep/``."""
    return _PREP_DIR


def ensure_prep_dir() -> Path:
    """Create ``~/.prep/`` and its standard subdirectories if needed.

    Returns the prep directory path.
    """
    _PREP_DIR.mkdir(parents=True, exist_ok=True)
    for sub in _SUBDIRS:
        (_PREP_DIR / sub).mkdir(exist_ok=True)
    return _PREP_DIR


# ------------------------------------------------------------------
# YAML
# ------------------------------------------------------------------

def read_yaml(path: str | Path) -> Any:
    """Load and return the contents of a YAML file.

    Returns ``None`` when the file does not exist.
    """
    p = Path(path)
    if not p.exists():
        return None
    with p.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def write_yaml(path: str | Path, data: Any) -> None:
    """Serialise *data* to a YAML file, creating parent dirs as needed."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as fh:
        yaml.dump(data, fh, default_flow_style=False, sort_keys=False, allow_unicode=True)


# ------------------------------------------------------------------
# Markdown
# ------------------------------------------------------------------

def read_markdown(path: str | Path) -> str | None:
    """Read a Markdown file and return its text.

    Returns ``None`` when the file does not exist.
    """
    p = Path(path)
    if not p.exists():
        return None
    return p.read_text(encoding="utf-8")


def write_markdown(path: str | Path, content: str) -> None:
    """Write *content* to a Markdown file, creating parent dirs as needed."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")


# ------------------------------------------------------------------
# JSON
# ------------------------------------------------------------------

def read_json(path: str | Path) -> Any:
    """Load and return the contents of a JSON file.

    Returns ``None`` when the file does not exist.
    """
    p = Path(path)
    if not p.exists():
        return None
    with p.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def write_json(path: str | Path, data: Any) -> None:
    """Serialise *data* to a JSON file, creating parent dirs as needed."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
