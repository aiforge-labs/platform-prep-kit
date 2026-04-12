"""Tests for configuration management."""
import os
import tempfile
import pytest
import yaml


def get_fixture_path(name: str) -> str:
    return os.path.join(os.path.dirname(__file__), "fixtures", name)


class TestConfigLoad:
    def test_load_sample_config(self):
        from prep_agent.core.config import load_config
        config = load_config(get_fixture_path("sample-config.yml"))
        assert config["version"] == 1
        assert config["profile"]["name"] == "Jane Doe"
        assert config["target"]["role"] == "Cloud Security Lead"
        assert len(config["gaps"]) == 3

    def test_config_has_defaults(self):
        from prep_agent.core.config import load_config
        config = load_config(get_fixture_path("sample-config.yml"))
        assert "reminders" in config
        assert config["reminders"]["enabled"] is True

    def test_validate_valid_config(self):
        from prep_agent.core.config import load_config, validate_config
        config = load_config(get_fixture_path("sample-config.yml"))
        errors = validate_config(config)
        assert len(errors) == 0

    def test_validate_missing_fields(self):
        from prep_agent.core.config import validate_config
        errors = validate_config({"version": 1})
        assert len(errors) > 0

    def test_create_default_config(self):
        from prep_agent.core.config import create_default_config
        config = create_default_config(
            target_role="Test Role",
            company="Test Corp",
            timeline_weeks=4,
            hours_per_week=10,
            strengths=["Python", "AWS"],
            gaps=[{"id": "test", "topic": "Test Topic", "priority": "high", "estimated_hours": 5}],
        )
        assert config["target"]["role"] == "Test Role"
        assert config["timeline"]["weeks"] == 4
        assert len(config["gaps"]) == 1

    def test_save_and_reload_config(self):
        from prep_agent.core.config import create_default_config, save_config, load_config
        config = create_default_config(
            target_role="Test Role",
            company="Test Corp",
            timeline_weeks=4,
            hours_per_week=10,
        )
        with tempfile.NamedTemporaryFile(suffix=".yml", delete=False, mode="w") as f:
            save_config(config, f.name)
            reloaded = load_config(f.name)
            assert reloaded["target"]["role"] == "Test Role"
            os.unlink(f.name)


class TestConfigValidation:
    def test_invalid_priority(self):
        from prep_agent.core.config import validate_config
        config = {
            "version": 1,
            "profile": {"name": "Test"},
            "target": {"role": "Test"},
            "timeline": {"start_date": "2026-01-01", "end_date": "2026-03-01", "weeks": 8, "hours_per_week": 10, "study_days": ["mon"]},
            "gaps": [{"id": "x", "topic": "X", "priority": "invalid", "estimated_hours": 5}],
        }
        errors = validate_config(config)
        assert any("priority" in e.lower() for e in errors)


class TestPydanticBoundaryValidation:
    """Test the Pydantic boundary adapter in models.py."""

    def test_validates_good_config(self):
        from prep_agent.models import validate_config_dict
        config = {
            "version": 1,
            "profile": {"name": "Jane Doe"},
            "target": {"role": "Cloud Security Lead"},
            "timeline": {
                "start_date": "2026-01-01",
                "end_date": "2026-03-01",
                "weeks": 8,
                "hours_per_week": 10,
                "study_days": ["Monday", "Wednesday"],
            },
            "strengths": ["Python", "AWS"],
            "gaps": [
                {"id": "g1", "topic": "K8s", "priority": "high", "estimated_hours": 10},
            ],
        }
        model, errors = validate_config_dict(config)
        assert model is not None
        assert errors == []
        assert model.profile.name == "Jane Doe"
        assert model.target.role == "Cloud Security Lead"

    def test_rejects_bad_config(self):
        from prep_agent.models import validate_config_dict
        # Missing required fields: profile, target, timeline, strengths, gaps
        model, errors = validate_config_dict({"version": 1})
        assert model is None
        assert len(errors) > 0

    def test_rejects_invalid_priority(self):
        from prep_agent.models import validate_config_dict
        config = {
            "version": 1,
            "profile": {"name": "Test"},
            "target": {"role": "Test"},
            "timeline": {
                "start_date": "2026-01-01",
                "end_date": "2026-03-01",
                "weeks": 8,
                "hours_per_week": 10,
                "study_days": ["Monday"],
            },
            "strengths": [],
            "gaps": [
                {"id": "g1", "topic": "X", "priority": "banana", "estimated_hours": 5},
            ],
        }
        model, errors = validate_config_dict(config)
        assert model is None
        assert any("priority" in e.lower() for e in errors)
