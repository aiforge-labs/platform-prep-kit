"""
Date utilities for the platform-prep-kit.

All functions work with :class:`datetime.date` objects unless stated
otherwise.  The module is intentionally free of side-effects.
"""

from __future__ import annotations

import math
from datetime import date, datetime, timedelta
from typing import Sequence


def get_current_day(start_date: date) -> int:
    """Return the 1-based day number relative to *start_date*.

    Day 1 is *start_date* itself.  Returns 0 if today is before the
    start date.
    """
    delta = date.today() - start_date
    return max(0, delta.days + 1)


def get_current_week(start_date: date) -> int:
    """Return the 1-based week number relative to *start_date*.

    Week 1 covers days 1-7, week 2 covers days 8-14, etc.
    Returns 0 if today is before the start date.
    """
    day = get_current_day(start_date)
    if day <= 0:
        return 0
    return math.ceil(day / 7)


def format_date(d: date) -> str:
    """Return a human-readable date string, e.g. ``Mon, 24 Mar 2026``."""
    return d.strftime("%a, %d %b %Y")


def parse_date(text: str) -> date:
    """Parse a date from *text*.

    Supported formats (tried in order):
        - ``YYYY-MM-DD``
        - ``DD/MM/YYYY``
        - ``MM-DD-YYYY``

    Raises :class:`ValueError` when none of the formats match.
    """
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m-%d-%Y"):
        try:
            return datetime.strptime(text.strip(), fmt).date()
        except ValueError:
            continue
    raise ValueError(
        f"Unable to parse date '{text}'. "
        "Expected YYYY-MM-DD, DD/MM/YYYY, or MM-DD-YYYY."
    )


def is_study_day(d: date, study_days: Sequence[int] | None = None) -> bool:
    """Check whether *d* falls on a configured study day.

    *study_days* is a sequence of ISO weekday numbers (1 = Monday …
    7 = Sunday).  When *study_days* is ``None`` every day is a study
    day.
    """
    if study_days is None:
        return True
    return d.isoweekday() in study_days


def days_remaining(end_date: date) -> int:
    """Return the number of days from today until *end_date* (inclusive).

    Returns 0 when *end_date* is in the past.
    """
    delta = end_date - date.today()
    return max(0, delta.days)
