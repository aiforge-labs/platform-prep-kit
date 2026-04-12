"""Study plan generator — creates day-by-day prep schedules from config."""

from __future__ import annotations

import math
from datetime import date, datetime, timedelta
from typing import Any

# Day-of-week name to number (Monday=0 .. Sunday=6)
_DOW_MAP: dict[str, int] = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
}

# Priority weights for allocation ordering
_PRIORITY_WEIGHT: dict[str, int] = {
    "critical": 3,
    "high": 2,
    "moderate": 1,
    "low": 0,
}


class StudyPlanner:
    """Generates a day-by-day study plan from a preparation config."""

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate(self, config: dict[str, Any]) -> dict[str, Any]:
        """Generate a complete study plan from *config*.

        Algorithm
        ---------
        1. Calculate total available study days and hours.
        2. Sort gaps by priority (critical > high > moderate).
        3. Allocate days per gap based on estimated_hours / daily_hours.
        4. Map to calendar with study_days from config.
        5. Interleave review days (every 3rd study day).
        6. Insert content creation at scheduled weeks.
        7. Reserve last 15 % of days for interview prep.
        8. Generate day-by-day entries.

        Returns
        -------
        dict with keys: total_days, total_weeks, hours_per_day, days,
        tracks, milestones.
        """
        params = self._calculate_schedule_params(config)

        gaps = config.get("gaps", [])
        available_days = params["available_days"]
        interview_days = max(1, math.ceil(available_days * 0.15))
        study_days_count = available_days - interview_days

        topics_with_days = self._allocate_topics(gaps, study_days_count)

        days = self._map_to_calendar(
            topics_with_days,
            params["start_date"],
            params["study_dow_set"],
            params["hours_per_day"],
        )

        days = self._add_review_days(days)
        days = self._add_content_days(days, config.get("content_plan", []))
        days = self._add_interview_prep(days, config, interview_days)

        # Build tracks summary
        tracks = self._build_tracks(topics_with_days, days)

        # Build milestones
        milestones = self._build_milestones(days, tracks)

        total_days = len(days)
        total_weeks = math.ceil(total_days / 7) if total_days else 0

        return {
            "total_days": total_days,
            "total_weeks": total_weeks,
            "hours_per_day": params["hours_per_day"],
            "days": days,
            "tracks": tracks,
            "milestones": milestones,
        }

    def generate_plan_md(self, plan: dict[str, Any], config: dict[str, Any]) -> str:
        """Generate human-readable study plan markdown."""
        lines: list[str] = []

        # --- Overview ---
        lines.append("# Study Plan")
        lines.append("")
        lines.append(
            f"**Duration:** {plan['total_weeks']} weeks "
            f"({plan['total_days']} study days)  "
        )
        lines.append(f"**Daily hours:** {plan['hours_per_day']}  ")
        lines.append(
            f"**Tracks:** {len(plan['tracks'])}  "
        )
        lines.append("")

        # --- Tracks overview ---
        lines.append("## Tracks")
        lines.append("")
        lines.append("| # | Track | Topics | Days |")
        lines.append("|---|-------|--------|------|")
        for idx, t in enumerate(plan["tracks"], 1):
            topic_count = len(t.get("topics", []))
            day_range = f"{t['start_day']}-{t['end_day']}" if t.get("start_day") else "-"
            lines.append(f"| {idx} | {t['name']} | {topic_count} | {day_range} |")
        lines.append("")

        # --- Milestones ---
        if plan["milestones"]:
            lines.append("## Milestones")
            lines.append("")
            for m in plan["milestones"]:
                lines.append(f"- **Day {m['day']}:** {m['description']}")
            lines.append("")

        # --- Weekly breakdown ---
        lines.append("## Weekly Breakdown")
        lines.append("")

        days_by_week: dict[int, list[dict]] = {}
        for d in plan["days"]:
            days_by_week.setdefault(d["week"], []).append(d)

        for week_num in sorted(days_by_week):
            week_days = days_by_week[week_num]
            lines.append(f"### Week {week_num}")
            lines.append("")
            lines.append("| Day | Date | Topic | Morning | Evening | Flags |")
            lines.append("|-----|------|-------|---------|---------|-------|")
            for d in week_days:
                flags = []
                if d.get("is_review_day"):
                    flags.append("Review")
                if d.get("is_buffer_day"):
                    flags.append("Buffer")
                if d.get("content_task"):
                    flags.append("Content")
                if d.get("research_task"):
                    flags.append("Research")
                flag_str = ", ".join(flags) if flags else "-"
                lines.append(
                    f"| {d['day_num']} "
                    f"| {d['date']} "
                    f"| {d['topic']} "
                    f"| {d.get('morning_focus', '-')} "
                    f"| {d.get('evening_focus', '-')} "
                    f"| {flag_str} |"
                )
            lines.append("")

        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _calculate_schedule_params(self, config: dict[str, Any]) -> dict[str, Any]:
        """Calculate available days, hours, daily study time."""
        # Config stores schedule info under "timeline"; fall back to legacy "schedule"
        timeline = config.get("timeline", config.get("schedule", {}))
        start_str = timeline.get("start_date", date.today().isoformat())
        end_str = timeline.get("end_date", None)
        duration_weeks = timeline.get("weeks", timeline.get("duration_weeks", 12))
        study_day_names: list[str] = timeline.get(
            "study_days", ["monday", "tuesday", "wednesday", "thursday", "friday"]
        )
        # Support hours_per_week (from create_default_config) or hours_per_day directly
        hours_per_week = timeline.get("hours_per_week")
        if hours_per_week is not None:
            days_per_week = max(1, len(study_day_names))
            hours_per_day = round(hours_per_week / days_per_week, 1)
        else:
            hours_per_day = timeline.get(
                "hours_per_day", config.get("daily_hours", 4)
            )

        start_date = self._parse_date(start_str)
        if end_str:
            end_date = self._parse_date(end_str)
        else:
            end_date = start_date + timedelta(weeks=duration_weeks)

        # Support both abbreviated ("mon") and full ("monday") day names
        _abbrev = {k[:3]: v for k, v in _DOW_MAP.items()}
        study_dow_set = {
            _DOW_MAP.get(d.lower(), _abbrev.get(d.lower()))
            for d in study_day_names
            if _DOW_MAP.get(d.lower(), _abbrev.get(d.lower())) is not None
        }

        # Count study days in range
        available_days = 0
        cursor = start_date
        while cursor <= end_date:
            if cursor.weekday() in study_dow_set:
                available_days += 1
            cursor += timedelta(days=1)

        return {
            "start_date": start_date,
            "end_date": end_date,
            "hours_per_day": hours_per_day,
            "study_dow_set": study_dow_set,
            "available_days": available_days,
        }

    def _allocate_topics(
        self, gaps: list[dict[str, Any]], available_days: int
    ) -> list[dict[str, Any]]:
        """Allocate days to each topic based on priority and hours."""
        if not gaps:
            return []

        # Sort by priority weight descending
        sorted_gaps = sorted(
            gaps,
            key=lambda g: _PRIORITY_WEIGHT.get(g.get("priority", "moderate"), 1),
            reverse=True,
        )

        # Calculate raw day needs (estimated_hours / assumed 4h default)
        total_raw = 0
        for gap in sorted_gaps:
            hours = gap.get("estimated_hours", 8)
            gap["_raw_days"] = max(1, math.ceil(hours / 4))
            total_raw += gap["_raw_days"]

        # Scale to fit available days
        if total_raw == 0:
            total_raw = 1
        scale = available_days / total_raw

        allocated: list[dict[str, Any]] = []
        used = 0
        for gap in sorted_gaps:
            days = max(1, round(gap["_raw_days"] * scale))
            # Don't exceed remaining
            days = min(days, available_days - used)
            if days <= 0:
                break
            topics = gap.get("topics", [gap.get("name", "Unnamed")])
            allocated.append(
                {
                    "track_id": gap.get("id", gap.get("name", "unknown")).lower().replace(" ", "-"),
                    "name": gap.get("name", "Unnamed"),
                    "priority": gap.get("priority", "moderate"),
                    "topics": topics,
                    "days": days,
                }
            )
            used += days

        return allocated

    def _map_to_calendar(
        self,
        topics_with_days: list[dict[str, Any]],
        start_date: date,
        study_dow_set: set[int],
        hours_per_day: float,
    ) -> list[dict[str, Any]]:
        """Map topic allocations to actual calendar dates."""
        days: list[dict[str, Any]] = []
        cursor = start_date
        day_num = 0

        for track in topics_with_days:
            track_topics = track["topics"]
            track_days = track["days"]
            topic_count = len(track_topics) if track_topics else 1

            for i in range(track_days):
                # Advance cursor to next study day
                while cursor.weekday() not in study_dow_set:
                    cursor += timedelta(days=1)

                day_num += 1
                topic_idx = min(i * topic_count // track_days, topic_count - 1)
                topic = track_topics[topic_idx] if track_topics else track["name"]

                # Split day into morning/evening focus
                morning = f"Study: {topic} (theory & concepts)"
                evening = f"Practice: {topic} (exercises & application)"

                week = ((cursor - start_date).days // 7) + 1

                days.append(
                    {
                        "day_num": day_num,
                        "date": cursor.isoformat(),
                        "week": week,
                        "track_id": track["track_id"],
                        "topic": topic,
                        "morning_focus": morning,
                        "evening_focus": evening,
                        "content_task": None,
                        "research_task": None,
                        "is_review_day": False,
                        "is_buffer_day": False,
                    }
                )
                cursor += timedelta(days=1)

        return days

    def _add_review_days(self, days: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Insert review/revision days every 3rd study day."""
        for i, day in enumerate(days):
            if (i + 1) % 3 == 0:
                day["is_review_day"] = True
                day["morning_focus"] = f"Review: {day['topic']} (revisit weak areas)"
                day["evening_focus"] = f"Quiz & self-test: {day['topic']}"
        return days

    def _add_content_days(
        self, days: list[dict[str, Any]], content_plan: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Add content creation tasks to appropriate days."""
        if not content_plan or not days:
            return days

        for item in content_plan:
            target_week = item.get("week", 1)
            title = item.get("title", "Content item")
            task_type = item.get("type", "content")

            # Find the first day in the target week
            for day in days:
                if day["week"] == target_week and not day.get("content_task"):
                    if task_type == "research":
                        day["research_task"] = title
                    else:
                        day["content_task"] = title
                    break

        return days

    def _add_interview_prep(
        self,
        days: list[dict[str, Any]],
        config: dict[str, Any],
        interview_days: int,
    ) -> list[dict[str, Any]]:
        """Reserve final days for interview preparation."""
        if not days:
            return days

        # Mark the last N days as interview prep / buffer
        start_idx = max(0, len(days) - interview_days)
        for i in range(start_idx, len(days)):
            days[i]["is_buffer_day"] = True
            days[i]["topic"] = "Interview Prep"
            days[i]["morning_focus"] = "Mock interviews & behavioral questions"
            days[i]["evening_focus"] = "Technical review & case studies"
            days[i]["track_id"] = "interview-prep"

        return days

    # ------------------------------------------------------------------
    # Builders
    # ------------------------------------------------------------------

    def _build_tracks(
        self,
        topics_with_days: list[dict[str, Any]],
        days: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Build tracks summary from allocated topics and scheduled days."""
        tracks: list[dict[str, Any]] = []
        seen_ids: set[str] = set()

        for track in topics_with_days:
            tid = track["track_id"]
            if tid in seen_ids:
                continue
            seen_ids.add(tid)

            track_days = [d for d in days if d["track_id"] == tid]
            start_day = track_days[0]["day_num"] if track_days else 0
            end_day = track_days[-1]["day_num"] if track_days else 0

            tracks.append(
                {
                    "id": tid,
                    "name": track["name"],
                    "topics": track["topics"],
                    "start_day": start_day,
                    "end_day": end_day,
                }
            )

        # Add interview-prep track if present
        ip_days = [d for d in days if d["track_id"] == "interview-prep"]
        if ip_days and "interview-prep" not in seen_ids:
            tracks.append(
                {
                    "id": "interview-prep",
                    "name": "Interview Prep",
                    "topics": ["Mock interviews", "Technical review"],
                    "start_day": ip_days[0]["day_num"],
                    "end_day": ip_days[-1]["day_num"],
                }
            )

        return tracks

    def _build_milestones(
        self,
        days: list[dict[str, Any]],
        tracks: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Generate milestones at track boundaries and key points."""
        milestones: list[dict[str, Any]] = []

        for track in tracks:
            if track["end_day"]:
                milestones.append(
                    {
                        "day": track["end_day"],
                        "description": f"Complete track: {track['name']}",
                    }
                )

        # Mid-point milestone
        if days:
            mid = len(days) // 2
            milestones.append(
                {
                    "day": days[mid]["day_num"],
                    "description": "Halfway checkpoint — review all tracks",
                }
            )

        milestones.sort(key=lambda m: m["day"])
        return milestones

    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_date(s: str) -> date:
        """Parse an ISO-format date string."""
        return datetime.strptime(s, "%Y-%m-%d").date()
