"""Tests for study plan generation."""
import os
import pytest


def get_fixture_path(name: str) -> str:
    return os.path.join(os.path.dirname(__file__), "fixtures", name)


class TestStudyPlanner:
    def _get_sample_config(self):
        from prep_agent.core.config import load_config
        return load_config(get_fixture_path("sample-config.yml"))

    def test_generate_plan(self):
        from prep_agent.core.planner import StudyPlanner
        config = self._get_sample_config()
        planner = StudyPlanner()
        plan = planner.generate(config)
        assert "days" in plan
        assert "total_days" in plan
        assert len(plan["days"]) > 0

    def test_plan_covers_critical_gaps(self):
        from prep_agent.core.planner import StudyPlanner
        config = self._get_sample_config()
        planner = StudyPlanner()
        plan = planner.generate(config)
        plan_topic_ids = {d.get("track_id") for d in plan["days"] if d.get("track_id")}
        # Critical gaps must appear in the plan
        critical_gaps = {g["id"] for g in config["gaps"] if g["priority"] == "critical"}
        for gap_id in critical_gaps:
            assert gap_id in plan_topic_ids, f"Critical gap {gap_id} not in plan"

    def test_plan_mostly_respects_study_days(self):
        from prep_agent.core.planner import StudyPlanner
        config = self._get_sample_config()
        planner = StudyPlanner()
        plan = planner.generate(config)
        # Most planned dates should fall on configured study days
        # (planner may include occasional buffer days on off-days)
        study_days = config["timeline"]["study_days"]
        day_names = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
        on_study_day = 0
        total = 0
        for day in plan["days"]:
            if "date" in day:
                from datetime import datetime
                dt = datetime.strptime(day["date"], "%Y-%m-%d")
                day_name = day_names[dt.weekday()]
                total += 1
                if day_name in study_days:
                    on_study_day += 1
        # At least 80% of days should be on configured study days
        assert total > 0
        assert on_study_day / total >= 0.8, f"Only {on_study_day}/{total} days on study days"

    def test_plan_has_review_days(self):
        from prep_agent.core.planner import StudyPlanner
        config = self._get_sample_config()
        planner = StudyPlanner()
        plan = planner.generate(config)
        review_days = [d for d in plan["days"] if d.get("is_review_day")]
        assert len(review_days) > 0, "Plan should include review days"

    def test_generate_plan_md(self):
        from prep_agent.core.planner import StudyPlanner
        config = self._get_sample_config()
        planner = StudyPlanner()
        plan = planner.generate(config)
        md = planner.generate_plan_md(plan, config)
        assert "# Study Plan" in md
        assert "Week 1" in md

    def test_critical_gaps_scheduled_first(self):
        from prep_agent.core.planner import StudyPlanner
        config = self._get_sample_config()
        planner = StudyPlanner()
        plan = planner.generate(config)
        # First non-review day should be a critical topic
        first_topic_day = next(d for d in plan["days"] if d.get("track_id") and not d.get("is_review_day"))
        gap_priority = {g["id"]: g["priority"] for g in config["gaps"]}
        assert gap_priority.get(first_topic_day["track_id"]) == "critical"


class TestPlannerEdgeCases:
    def test_single_gap(self):
        from prep_agent.core.planner import StudyPlanner
        from prep_agent.core.config import create_default_config
        config = create_default_config(
            target_role="Test",
            company="Test",
            timeline_weeks=2,
            hours_per_week=10,
            gaps=[{"id": "only-gap", "topic": "Only Topic", "priority": "critical", "estimated_hours": 10}],
        )
        planner = StudyPlanner()
        plan = planner.generate(config)
        assert len(plan["days"]) > 0

    def test_many_gaps_short_timeline(self):
        from prep_agent.core.planner import StudyPlanner
        from prep_agent.core.config import create_default_config
        gaps = [
            {"id": f"gap-{i}", "topic": f"Topic {i}", "priority": "high", "estimated_hours": 10}
            for i in range(10)
        ]
        config = create_default_config(
            target_role="Test",
            company="Test",
            timeline_weeks=2,
            hours_per_week=5,
            gaps=gaps,
        )
        planner = StudyPlanner()
        plan = planner.generate(config)
        # Should still generate a plan even if not all gaps fit
        assert len(plan["days"]) > 0
