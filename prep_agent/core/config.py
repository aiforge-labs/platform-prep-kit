"""Configuration management for career prep agent."""

import os
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Optional

import yaml

DEFAULT_CONFIG_DIR = Path.home() / ".prep"
DEFAULT_CONFIG_PATH = DEFAULT_CONFIG_DIR / "config.yml"

CONFIG_SCHEMA: dict[str, dict[str, Any]] = {
    "version": {"type": int, "required": True},
    "profile": {
        "type": dict,
        "required": False,
        "fields": {
            "name": {"type": str, "required": False},
            "current_role": {"type": str, "required": False},
        },
    },
    "target": {
        "type": dict,
        "required": True,
        "fields": {
            "role": {"type": str, "required": True},
            "company": {"type": str, "required": True},
            "job_url": {"type": str, "required": False},
            "location": {"type": str, "required": False},
        },
    },
    "timeline": {
        "type": dict,
        "required": False,
        "fields": {
            "start_date": {"type": str, "required": False},
            "end_date": {"type": str, "required": False},
            "weeks": {"type": int, "required": False},
            "hours_per_week": {"type": int, "required": False},
            "study_days": {"type": list, "required": False},
        },
    },
    "reminders": {
        "type": dict,
        "required": False,
        "fields": {
            "enabled": {"type": bool, "required": False},
            "morning_time": {"type": str, "required": False},
            "evening_time": {"type": str, "required": False},
            "method": {"type": str, "required": False},
        },
    },
    "strengths": {"type": list, "required": False},
    "gaps": {"type": list, "required": False},
    "certifications": {"type": list, "required": False},
    "content_plan": {"type": list, "required": False},
    "ai_integration": {
        "type": dict,
        "required": False,
        "fields": {
            "provider": {"type": str, "required": False},
        },
    },
}

DEFAULTS: dict[str, Any] = {
    "version": 1,
    "profile": {
        "name": "",
        "current_role": "",
    },
    "target": {
        "role": "",
        "company": "",
        "job_url": "",
        "location": "",
    },
    "timeline": {
        "start_date": "",
        "end_date": "",
        "weeks": 8,
        "hours_per_week": 15,
        "study_days": ["mon", "tue", "wed", "thu", "sat", "sun"],
    },
    "reminders": {
        "enabled": True,
        "morning_time": "07:00",
        "evening_time": "19:00",
        "method": "desktop",
    },
    "strengths": [],
    "gaps": [],
    "certifications": [],
    "content_plan": [],
    "ai_integration": {
        "provider": "none",
    },
}

VALID_DAYS = {"mon", "tue", "wed", "thu", "fri", "sat", "sun"}
VALID_PRIORITIES = {"critical", "high", "moderate"}
VALID_REMINDER_METHODS = {"desktop", "email", "slack", "none"}


def _deep_merge(base: dict, override: dict) -> dict:
    """Recursively merge override into base, returning a new dict."""
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def _validate_time_format(value: str, field_name: str) -> Optional[str]:
    """Validate HH:MM time format. Returns error string or None."""
    try:
        datetime.strptime(value, "%H:%M")
        return None
    except ValueError:
        return f"{field_name} must be in HH:MM format, got '{value}'"


def _validate_date_format(value: str, field_name: str) -> Optional[str]:
    """Validate YYYY-MM-DD date format. Returns error string or None."""
    if not value:
        return None
    try:
        datetime.strptime(value, "%Y-%m-%d")
        return None
    except ValueError:
        return f"{field_name} must be in YYYY-MM-DD format, got '{value}'"


def validate_config(config: dict) -> list[str]:
    """Validate a config dict against the schema.

    Returns a list of validation errors. An empty list means the config is valid.
    """
    errors: list[str] = []

    if not isinstance(config, dict):
        return ["Config must be a dictionary"]

    # Check version
    if "version" not in config:
        errors.append("Missing required field: version")
    elif not isinstance(config["version"], int):
        errors.append("version must be an integer")
    elif config["version"] != 1:
        errors.append(f"Unsupported config version: {config['version']} (supported: 1)")

    # Check required top-level sections
    for field, schema in CONFIG_SCHEMA.items():
        if schema.get("required") and field not in config:
            errors.append(f"Missing required field: {field}")

    # Validate target section
    target = config.get("target", {})
    if isinstance(target, dict):
        if not target.get("role"):
            errors.append("target.role is required and cannot be empty")
        # company is optional — user may not have a specific target company yet
    elif "target" in config:
        errors.append("target must be a dictionary")

    # Validate timeline section
    timeline = config.get("timeline", {})
    if isinstance(timeline, dict):
        weeks = timeline.get("weeks")
        if weeks is not None and (not isinstance(weeks, int) or weeks < 1):
            errors.append("timeline.weeks must be a positive integer")

        hours = timeline.get("hours_per_week")
        if hours is not None and (not isinstance(hours, int) or hours < 1):
            errors.append("timeline.hours_per_week must be a positive integer")

        study_days = timeline.get("study_days", [])
        if isinstance(study_days, list):
            for day in study_days:
                if day not in VALID_DAYS:
                    errors.append(
                        f"Invalid study day '{day}'; valid values: {sorted(VALID_DAYS)}"
                    )
        elif study_days is not None:
            errors.append("timeline.study_days must be a list")

        start_err = _validate_date_format(
            timeline.get("start_date", ""), "timeline.start_date"
        )
        if start_err:
            errors.append(start_err)

        end_err = _validate_date_format(
            timeline.get("end_date", ""), "timeline.end_date"
        )
        if end_err:
            errors.append(end_err)

    # Validate reminders section
    reminders = config.get("reminders", {})
    if isinstance(reminders, dict):
        morning = reminders.get("morning_time", "")
        if morning:
            err = _validate_time_format(morning, "reminders.morning_time")
            if err:
                errors.append(err)

        evening = reminders.get("evening_time", "")
        if evening:
            err = _validate_time_format(evening, "reminders.evening_time")
            if err:
                errors.append(err)

        method = reminders.get("method", "desktop")
        if method not in VALID_REMINDER_METHODS:
            errors.append(
                f"Invalid reminder method '{method}'; valid values: {sorted(VALID_REMINDER_METHODS)}"
            )

    # Validate gaps entries
    gaps = config.get("gaps", [])
    if isinstance(gaps, list):
        for i, gap in enumerate(gaps):
            if not isinstance(gap, dict):
                errors.append(f"gaps[{i}] must be a dictionary")
                continue
            priority = gap.get("priority", "")
            if priority and priority not in VALID_PRIORITIES:
                errors.append(
                    f"gaps[{i}].priority '{priority}' invalid; "
                    f"valid values: {sorted(VALID_PRIORITIES)}"
                )
            est = gap.get("estimated_hours")
            if est is not None and (not isinstance(est, (int, float)) or est < 0):
                errors.append(f"gaps[{i}].estimated_hours must be a non-negative number")

    # Validate strengths is a list
    strengths = config.get("strengths")
    if strengths is not None and not isinstance(strengths, list):
        errors.append("strengths must be a list")

    # Validate certifications is a list
    certs = config.get("certifications")
    if certs is not None and not isinstance(certs, list):
        errors.append("certifications must be a list")

    return errors


def load_config(path: Optional[str] = None) -> dict:
    """Load config from YAML file, merge with defaults, and validate.

    Args:
        path: Path to config file. Defaults to ~/.prep/config.yml.

    Returns:
        Merged and validated config dict.

    Raises:
        FileNotFoundError: If config file does not exist.
        ValueError: If config has validation errors.
    """
    config_path = Path(path) if path else DEFAULT_CONFIG_PATH

    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path, "r") as f:
        raw = yaml.safe_load(f)

    if raw is None:
        raw = {}

    config = _deep_merge(DEFAULTS, raw)

    errors = validate_config(config)
    if errors:
        raise ValueError(
            f"Config validation failed with {len(errors)} error(s):\n"
            + "\n".join(f"  - {e}" for e in errors)
        )

    return config


def save_config(config: dict, path: Optional[str] = None) -> None:
    """Save config dict to a YAML file.

    Args:
        config: Config dict to save.
        path: Target file path. Defaults to ~/.prep/config.yml.
    """
    config_path = Path(path) if path else DEFAULT_CONFIG_PATH
    config_path.parent.mkdir(parents=True, exist_ok=True)

    with open(config_path, "w") as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False, width=120)


def create_default_config(
    target_role: str,
    company: str,
    timeline_weeks: int = 8,
    hours_per_week: int = 15,
    strengths: Optional[list[str]] = None,
    gaps: Optional[list[dict[str, Any]]] = None,
) -> dict:
    """Create a new config from user inputs, pre-filled with defaults.

    Args:
        target_role: The role being targeted.
        company: Target company name.
        timeline_weeks: Number of weeks for preparation.
        hours_per_week: Hours per week available for study.
        strengths: List of strength areas.
        gaps: List of gap dicts with id, topic, priority, estimated_hours.

    Returns:
        A complete config dict ready to save.
    """
    today = date.today()
    end_date = today + timedelta(weeks=timeline_weeks)

    config = _deep_merge(DEFAULTS, {})
    config["target"]["role"] = target_role
    config["target"]["company"] = company
    config["timeline"]["start_date"] = today.isoformat()
    config["timeline"]["end_date"] = end_date.isoformat()
    config["timeline"]["weeks"] = timeline_weeks
    config["timeline"]["hours_per_week"] = hours_per_week
    config["strengths"] = strengths or []
    config["gaps"] = gaps or []

    return config
