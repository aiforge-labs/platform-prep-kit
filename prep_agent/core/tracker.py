"""Progress tracker — reads and updates markdown-based progress files."""

from __future__ import annotations

import os
import re
from datetime import date, datetime
from typing import Any


class Tracker:
    """Manages a markdown-based progress tracker for study plans."""

    def __init__(self, prep_dir: str | None = None):
        self.prep_dir = prep_dir or os.path.expanduser("~/.prep")
        self.tracker_path = os.path.join(self.prep_dir, "tracker.md")

    # ------------------------------------------------------------------
    # Initialization
    # ------------------------------------------------------------------

    def initialize(self, plan: dict[str, Any], config: dict[str, Any]) -> None:
        """Create initial tracker.md from a study plan."""
        os.makedirs(self.prep_dir, exist_ok=True)

        state: dict[str, Any] = {
            "current_day": 1,
            "total_days": plan["total_days"],
            "current_week": 1,
            "total_weeks": plan["total_weeks"],
            "start_date": plan["days"][0]["date"] if plan["days"] else date.today().isoformat(),
            "streak": 0,
            "last_completed_day": 0,
            "days": [],
            "tracks": [],
            "content": [],
            "quiz_history": [],
        }

        # Build day entries
        for d in plan["days"]:
            state["days"].append(
                {
                    "day_num": d["day_num"],
                    "date": d["date"],
                    "status": "pending",
                    "track_id": d.get("track_id", ""),
                    "topic": d["topic"],
                    "notes": "",
                    "score": "",
                    "minutes": "",
                }
            )

        # Build track entries
        for t in plan["tracks"]:
            state["tracks"].append(
                {
                    "id": t["id"],
                    "name": t["name"],
                    "status": "not started",
                    "confidence": "-",
                }
            )

        # Build content entries
        for d in plan["days"]:
            if d.get("content_task"):
                state["content"].append(
                    {"title": d["content_task"], "status": "pending"}
                )

        md = self._generate_tracker_md(state)
        with open(self.tracker_path, "w") as f:
            f.write(md)

    # ------------------------------------------------------------------
    # Load / Parse
    # ------------------------------------------------------------------

    def load(self) -> dict[str, Any]:
        """Load tracker state from markdown file.

        Returns a dict with keys: current_day, total_days, current_week,
        total_weeks, start_date, today_topic, today_track, morning_focus,
        evening_focus, content_task, streak, last_completed_day, days,
        tracks, content, quiz_history, progress_pct.
        """
        with open(self.tracker_path) as f:
            content = f.read()
        return self._parse_tracker_md(content)

    def get_today(self) -> dict[str, Any] | None:
        """Get today's entry from tracker."""
        state = self.load()
        today_str = date.today().isoformat()
        for d in state.get("days", []):
            if d["date"] == today_str:
                return d
        return None

    # ------------------------------------------------------------------
    # Mutations
    # ------------------------------------------------------------------

    def mark_done(
        self,
        day_num: int | None = None,
        notes: str | None = None,
        score: int | None = None,
        minutes: int | None = None,
    ) -> None:
        """Mark a day as completed, update streak."""
        state = self.load()

        target = day_num
        if target is None:
            # Default to next pending day
            for d in state["days"]:
                if d["status"] == "pending":
                    target = d["day_num"]
                    break

        if target is None:
            return

        for d in state["days"]:
            if d["day_num"] == target:
                d["status"] = "done"
                if notes:
                    d["notes"] = notes
                if score is not None:
                    d["score"] = str(score)
                if minutes is not None:
                    d["minutes"] = str(minutes)
                break

        # Update streak
        state["last_completed_day"] = target
        state["streak"] = self._calc_streak(state["days"])

        self._save(state)

    def insert_review_day(
        self, after_day_num: int, track_id: str, topic: str
    ) -> bool:
        """Insert a review day after a given day number.

        Shifts subsequent day_nums and recalculates dates.
        Returns True if inserted, False if plan exceeds 90 days.
        """
        state = self.load()
        days = state["days"]

        if len(days) >= 90:
            return False

        # Find insertion index
        insert_idx = None
        for i, d in enumerate(days):
            if d["day_num"] == after_day_num:
                insert_idx = i + 1
                break
        if insert_idx is None:
            return False

        # Determine date for new day (day after the reference day)
        ref_date = days[insert_idx - 1].get("date", "")
        if ref_date:
            from datetime import timedelta
            new_date = (date.fromisoformat(ref_date) + timedelta(days=1)).isoformat()
        else:
            new_date = ""

        # Create review entry
        new_day = {
            "day_num": after_day_num + 1,
            "date": new_date,
            "status": "pending",
            "track_id": track_id,
            "topic": f"Review: {topic}",
            "notes": "",
            "score": "",
            "minutes": "",
        }

        # Shift subsequent day_nums
        for d in days[insert_idx:]:
            d["day_num"] += 1

        days.insert(insert_idx, new_day)
        state["total_days"] = len(days)
        self._save(state)
        return True

    def compress_track(self, track_id: str, remove_days: int = 1) -> int:
        """Remove pending days from a track to compress the plan.

        Removes from the end of the track's pending days.
        Returns the number of days actually removed.
        """
        state = self.load()
        days = state["days"]

        # Find pending days for this track (from the end)
        removable = []
        for i in range(len(days) - 1, -1, -1):
            d = days[i]
            if d.get("track_id") == track_id and d["status"] == "pending":
                removable.append(i)
            if len(removable) >= remove_days:
                break

        if not removable:
            return 0

        # Remove days (highest index first to avoid shifting)
        for idx in sorted(removable, reverse=True):
            days.pop(idx)

        # Renumber day_nums
        for i, d in enumerate(days):
            d["day_num"] = i + 1

        state["total_days"] = len(days)
        self._save(state)
        return len(removable)

    def update_track_status(
        self, track_id: str, status: str, confidence: str | None = None
    ) -> None:
        """Update a track's status and confidence level."""
        state = self.load()
        for t in state["tracks"]:
            if t["id"] == track_id:
                t["status"] = status
                if confidence is not None:
                    t["confidence"] = confidence
                break
        self._save(state)

    def update_content_status(self, title: str, status: str) -> None:
        """Update content creation status."""
        state = self.load()
        for c in state["content"]:
            if c["title"] == title:
                c["status"] = status
                break
        self._save(state)

    def log_quiz(
        self,
        topic: str,
        score: int,
        total: int,
        weak_areas: list[str] | None = None,
    ) -> None:
        """Log a quiz result."""
        state = self.load()
        entry: dict[str, Any] = {
            "date": date.today().isoformat(),
            "topic": topic,
            "score": score,
            "total": total,
        }
        if weak_areas:
            entry["weak_areas"] = weak_areas
        state.setdefault("quiz_history", []).append(entry)
        self._save(state)

    # ------------------------------------------------------------------
    # Progress helpers
    # ------------------------------------------------------------------

    def get_streak(self) -> int:
        """Calculate current consecutive day streak."""
        state = self.load()
        return self._calc_streak(state["days"])

    def get_progress(self) -> dict[str, Any]:
        """Calculate overall progress metrics."""
        state = self.load()
        days = state.get("days", [])
        done = [d for d in days if d["status"] == "done"]
        total = len(days)

        tracks = state.get("tracks", [])
        tracks_completed = sum(1 for t in tracks if t["status"] == "completed")

        content = state.get("content", [])
        content_done = sum(1 for c in content if c["status"] == "done")

        # Per-track progress breakdown — group days by track_id
        from collections import OrderedDict
        track_map: OrderedDict[str, dict[str, Any]] = OrderedDict()
        for d in days:
            tid = d.get("track_id", "")
            if not tid:
                continue
            if tid not in track_map:
                # Find display name from tracks list (fuzzy: id startswith or contains)
                display_name = tid
                for t in tracks:
                    t_id = t.get("id", "")
                    if t_id == tid or t_id.startswith(tid) or tid.startswith(t_id):
                        display_name = t.get("name", tid)
                        break
                track_map[tid] = {"name": display_name, "done": 0, "total": 0}
            track_map[tid]["total"] += 1
            if d["status"] == "done":
                track_map[tid]["done"] += 1
        track_progress = list(track_map.values())

        quizzes = state.get("quiz_history", [])
        scores = [q["score"] / q["total"] * 100 for q in quizzes if q.get("total")]
        avg_score = round(sum(scores) / len(scores), 1) if scores else 0.0

        # Weakest quiz topic
        weakest_topic = None
        if quizzes:
            from collections import defaultdict
            topic_scores: dict[str, list[float]] = defaultdict(list)
            for q in quizzes:
                if q.get("total"):
                    topic_scores[q["topic"]].append(q["score"] / q["total"] * 100)
            if topic_scores:
                weakest_topic = min(
                    topic_scores,
                    key=lambda t: sum(topic_scores[t]) / len(topic_scores[t]),
                )

        # Study hours from minutes
        total_minutes = sum(
            int(d.get("minutes", 0) or 0)
            for d in done
            if str(d.get("minutes", "")).isdigit()
        )
        study_hours = round(total_minutes / 60, 1) if total_minutes else None

        pct = round(len(done) / total * 100, 1) if total else 0.0

        # Find next study day and estimated completion
        today_str = date.today().isoformat()
        next_study_day = None
        est_end_date = None
        pending_dates = []
        for d in days:
            if d["status"] == "pending":
                pending_dates.append(d["date"])
                if d["date"] > today_str and next_study_day is None:
                    next_study_day = d["date"]
        if pending_dates:
            est_end_date = max(pending_dates)

        return {
            # Keys used by print_status_dashboard
            "completed_days": len(done),
            "total_days": total,
            "current_week": state.get("current_week", "—"),
            "total_weeks": state.get("total_weeks", "—"),
            "streak": self._calc_streak(days, today_str),
            "topics_done": len({d["topic"] for d in done}),
            "topics_total": len({d["topic"] for d in days}),
            "tracks": track_progress,
            "study_hours": study_hours,
            "quizzes_taken": len(quizzes),
            "avg_score": avg_score,
            "weakest_topic": weakest_topic,
            "est_end_date": est_end_date,
            # Legacy / agent-context keys
            "days_done": len(done),
            "days_total": total,
            "pct": pct,
            "tracks_completed": tracks_completed,
            "content_done": content_done,
            "next_study_day": next_study_day,
        }

    # ------------------------------------------------------------------
    # Markdown generation
    # ------------------------------------------------------------------

    def _generate_tracker_md(self, state: dict[str, Any]) -> str:
        """Generate tracker.md content from state."""
        lines: list[str] = []
        days = state.get("days", [])
        total = state.get("total_days", len(days))
        done_count = sum(1 for d in days if d.get("status") == "done")
        pct = round(done_count / total * 100) if total else 0
        bar = self._progress_bar(pct)

        current_day = state.get("current_day", 1)
        # Advance current_day to first pending
        for d in days:
            if d["status"] == "pending":
                current_day = d["day_num"]
                break

        current_week = state.get("current_week", 1)
        total_weeks = state.get("total_weeks", 1)
        streak = state.get("streak", 0)
        start_date = state.get("start_date", "")

        # --- Header ---
        lines.append("# Prep Tracker")
        lines.append("")
        lines.append(f"**Day {current_day}/{total}** | **Week {current_week}/{total_weeks}**  ")
        lines.append(f"**Start:** {start_date} | **Streak:** {streak} days  ")
        lines.append(f"**Progress:** {bar} {pct}%  ")
        lines.append("")

        # --- Daily Log ---
        lines.append("## Daily Log")
        lines.append("")
        lines.append("| Day | Date | Track | Topic | Status | Score | Minutes | Notes |")
        lines.append("|-----|------|-------|-------|--------|-------|---------|-------|")
        for d in days:
            day_num = d.get("day_num", "")
            dt = d.get("date", "")
            track_id = d.get("track_id", "")
            topic = d.get("topic", "")
            status = d.get("status", "pending")
            score = d.get("score", "")
            minutes_val = d.get("minutes", "")
            notes = d.get("notes", "")
            lines.append(f"| {day_num} | {dt} | {track_id} | {topic} | {status} | {score} | {minutes_val} | {notes} |")
        lines.append("")

        # --- Track Progress ---
        tracks = state.get("tracks", [])
        if tracks:
            lines.append("## Track Progress")
            lines.append("")
            lines.append("| Track | Status | Confidence |")
            lines.append("|-------|--------|------------|")
            for t in tracks:
                lines.append(f"| {t['name']} | {t['status']} | {t['confidence']} |")
            lines.append("")

        # --- Content Progress ---
        content = state.get("content", [])
        if content:
            lines.append("## Content Progress")
            lines.append("")
            lines.append("| Item | Status |")
            lines.append("|------|--------|")
            for c in content:
                lines.append(f"| {c['title']} | {c['status']} |")
            lines.append("")

        # --- Quiz History ---
        quizzes = state.get("quiz_history", [])
        lines.append("## Quiz History")
        lines.append("")
        lines.append("| Date | Topic | Score |")
        lines.append("|------|-------|-------|")
        for q in quizzes:
            total_q = q.get("total", 0)
            score_q = q.get("score", 0)
            score_str = f"{score_q}/{total_q}" if total_q else str(score_q)
            lines.append(f"| {q.get('date', '')} | {q.get('topic', '')} | {score_str} |")
        lines.append("")

        return "\n".join(lines)

    def _parse_tracker_md(self, content: str) -> dict[str, Any]:
        """Parse tracker.md back into state dict."""
        state: dict[str, Any] = {
            "current_day": 1,
            "total_days": 0,
            "current_week": 1,
            "total_weeks": 1,
            "start_date": "",
            "today_topic": None,
            "today_track": None,
            "morning_focus": None,
            "evening_focus": None,
            "content_task": None,
            "streak": 0,
            "last_completed_day": 0,
            "days": [],
            "tracks": [],
            "content": [],
            "quiz_history": [],
            "progress_pct": 0.0,
        }

        # Parse header
        m = re.search(r"\*\*Day (\d+)/(\d+)\*\*\s*\|\s*\*\*Week (\d+)/(\d+)\*\*", content)
        if m:
            state["current_day"] = int(m.group(1))
            state["total_days"] = int(m.group(2))
            state["current_week"] = int(m.group(3))
            state["total_weeks"] = int(m.group(4))

        m = re.search(r"\*\*Start:\*\*\s*(\S+)", content)
        if m:
            state["start_date"] = m.group(1)

        m = re.search(r"\*\*Streak:\*\*\s*(\d+)", content)
        if m:
            state["streak"] = int(m.group(1))

        m = re.search(r"\*\*Progress:\*\*.*?(\d+)%", content)
        if m:
            state["progress_pct"] = float(m.group(1))

        # Parse Daily Log table — support old and new column formats
        sample = content[content.find("## Daily Log"):][:400] if "## Daily Log" in content else ""
        has_track = "| Track |" in sample or "| track |" in sample.lower()
        has_minutes = "| Minutes |" in sample or "| minutes |" in sample.lower()
        if has_track and has_minutes:
            cols = ["day", "date", "track_id", "topic", "status", "score", "minutes", "notes"]
        elif has_track:
            cols = ["day", "date", "track_id", "topic", "status", "score", "notes"]
        elif has_minutes:
            cols = ["day", "date", "topic", "status", "score", "minutes", "notes"]
        else:
            cols = ["day", "date", "topic", "status", "score", "notes"]
        state["days"] = self._parse_table(content, "## Daily Log", cols, {"day": "day_num"})
        for d in state["days"]:
            d["day_num"] = int(d["day_num"]) if str(d.get("day_num", "")).isdigit() else 0

        # Find last completed day and set today's topic
        today_str = date.today().isoformat()
        for d in state["days"]:
            if d["status"] == "done":
                state["last_completed_day"] = max(
                    state["last_completed_day"], d["day_num"]
                )
            if d["date"] == today_str:
                state["today_topic"] = d["topic"]

        # Parse Track Progress table
        state["tracks"] = self._parse_table(
            content,
            "## Track Progress",
            ["track", "status", "confidence"],
            {"track": "name"},
        )
        # Add id field derived from name
        for t in state["tracks"]:
            t["id"] = t["name"].lower().replace(" ", "-")

        # Parse Content Progress table
        state["content"] = self._parse_table(
            content,
            "## Content Progress",
            ["item", "status"],
            {"item": "title"},
        )

        # Parse Quiz History table
        raw_quizzes = self._parse_table(
            content,
            "## Quiz History",
            ["date", "topic", "score"],
            {},
        )
        for q in raw_quizzes:
            score_parts = q.get("score", "0/0").split("/")
            parsed: dict[str, Any] = {
                "date": q["date"],
                "topic": q["topic"],
                "score": int(score_parts[0]) if score_parts[0].isdigit() else 0,
                "total": int(score_parts[1]) if len(score_parts) > 1 and score_parts[1].isdigit() else 0,
            }
            state["quiz_history"].append(parsed)

        return state

    # ------------------------------------------------------------------
    # Internal utilities
    # ------------------------------------------------------------------

    def _save(self, state: dict[str, Any]) -> None:
        """Write state back to tracker.md."""
        md = self._generate_tracker_md(state)
        with open(self.tracker_path, "w") as f:
            f.write(md)

    @staticmethod
    def _calc_streak(days: list[dict[str, Any]], today_str: str | None = None) -> int:
        """Calculate consecutive completed study days backwards from today."""
        if today_str is None:
            today_str = date.today().isoformat()
        # Only consider days on or before today, sorted newest-first
        past_days = sorted(
            [d for d in days if d.get("date", "") <= today_str],
            key=lambda d: d.get("date", ""),
            reverse=True,
        )
        streak = 0
        for d in past_days:
            if d.get("status") == "done":
                streak += 1
            else:
                break
        return streak

    @staticmethod
    def _progress_bar(pct: int, width: int = 20) -> str:
        """Render a text progress bar: [=====>              ]."""
        filled = round(width * pct / 100)
        empty = width - filled
        arrow = ">" if 0 < filled < width else ""
        bar_filled = "=" * max(0, filled - (1 if arrow else 0))
        return f"[{bar_filled}{arrow}{'.' * empty}]"

    @staticmethod
    def _parse_table(
        content: str,
        section_header: str,
        columns: list[str],
        rename: dict[str, str],
    ) -> list[dict[str, Any]]:
        """Parse a markdown table under a given section header.

        Parameters
        ----------
        content : full markdown text
        section_header : e.g. "## Daily Log"
        columns : column names in order (lowercase)
        rename : mapping from column name to desired key name
        """
        rows: list[dict[str, Any]] = []

        # Find section
        idx = content.find(section_header)
        if idx == -1:
            return rows

        # Find next section or end
        block = content[idx:]
        next_section = re.search(r"\n## ", block[len(section_header) :])
        if next_section:
            block = block[: len(section_header) + next_section.start()]

        # Find table rows (skip header and separator lines)
        table_lines = [
            ln.strip()
            for ln in block.split("\n")
            if ln.strip().startswith("|") and not re.match(r"^\|[\s\-:|]+\|$", ln.strip())
        ]

        # Skip the header row (first pipe-delimited line)
        if table_lines:
            table_lines = table_lines[1:]

        for line in table_lines:
            cells = [c.strip() for c in line.strip("|").split("|")]
            if len(cells) < len(columns):
                cells.extend([""] * (len(columns) - len(cells)))

            row: dict[str, Any] = {}
            for i, col in enumerate(columns):
                key = rename.get(col, col)
                row[key] = cells[i] if i < len(cells) else ""
            rows.append(row)

        return rows
