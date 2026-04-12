"""
prep template — Template management commands.

Subcommands:
  validate  Lint a template YAML file against the schema.
  list      List all available templates (alias for display).
"""

from __future__ import annotations

import os
import sys
from typing import Any

import click


# ---------------------------------------------------------------------------
# Canonical bridge_from keys (matches pivot_cmd._ROLE_ALIASES canonical set)
# ---------------------------------------------------------------------------
_CANONICAL_BRIDGE_KEYS = {
    "software_engineering", "backend_engineering", "web_development",
    "cloud_engineering", "devops_sre", "infrastructure_engineering",
    "system_administration", "security_engineering", "cloud_security",
    "penetration_testing", "network_security", "security_operations",
    "ml_engineering", "data_engineering", "data_scientist",
    "audit_compliance", "customer_success", "technical_support",
    "network_engineering",
}

_VALID_PRIORITIES = {"high", "medium", "low"}
_VALID_RESOURCE_TYPES = {"course", "article", "video", "book", "documentation"}
_VALID_CONTENT_TYPES = {"blog_post", "threat_model", "open_source", "presentation", "project"}


# ---------------------------------------------------------------------------
# Validation logic
# ---------------------------------------------------------------------------

class ValidationError:
    def __init__(self, path: str, message: str, level: str = "error"):
        self.path = path
        self.message = message
        self.level = level  # "error" | "warning"

    def __str__(self) -> str:
        icon = "✗" if self.level == "error" else "⚠"
        return f"  {icon} [{self.path}] {self.message}"


def _validate_template(data: dict) -> list[ValidationError]:
    issues: list[ValidationError] = []

    # --- Top-level required fields ---
    for field in ("name", "description", "version", "tracks"):
        if field not in data:
            issues.append(ValidationError("root", f"Missing required field: '{field}'"))

    if "version" in data and data["version"] != 1:
        issues.append(ValidationError("root.version", f"Expected version 1, got {data['version']!r}", "warning"))

    if "name" in data and not isinstance(data["name"], str):
        issues.append(ValidationError("root.name", "Must be a string"))

    if "tracks" in data and not isinstance(data["tracks"], list):
        issues.append(ValidationError("root.tracks", "Must be a list"))
        return issues  # can't validate tracks further

    # --- Tracks ---
    track_ids: set[str] = set()
    topic_ids: set[str] = set()

    for ti, track in enumerate(data.get("tracks", [])):
        tpath = f"tracks[{ti}]"

        if not isinstance(track, dict):
            issues.append(ValidationError(tpath, "Track must be a mapping"))
            continue

        for field in ("id", "name", "topics"):
            if field not in track:
                issues.append(ValidationError(tpath, f"Missing required field: '{field}'"))

        tid = track.get("id", "")
        if tid:
            if tid in track_ids:
                issues.append(ValidationError(f"{tpath}.id", f"Duplicate track id: '{tid}'"))
            track_ids.add(tid)

        if not isinstance(track.get("topics", []), list):
            issues.append(ValidationError(f"{tpath}.topics", "Must be a list"))
            continue

        # --- Topics ---
        for qi, topic in enumerate(track.get("topics", [])):
            qpath = f"{tpath}.topics[{qi}]"

            if not isinstance(topic, dict):
                issues.append(ValidationError(qpath, "Topic must be a mapping"))
                continue

            for field in ("id", "name", "estimated_hours", "priority"):
                if field not in topic:
                    issues.append(ValidationError(qpath, f"Missing required field: '{field}'"))

            topic_id = topic.get("id", "")
            if topic_id:
                if topic_id in topic_ids:
                    issues.append(ValidationError(f"{qpath}.id", f"Duplicate topic id: '{topic_id}'"))
                topic_ids.add(topic_id)

            priority = topic.get("priority", "")
            if priority and priority not in _VALID_PRIORITIES:
                issues.append(ValidationError(
                    f"{qpath}.priority",
                    f"Invalid priority '{priority}'. Must be one of: {sorted(_VALID_PRIORITIES)}",
                ))

            hours = topic.get("estimated_hours")
            if hours is not None and not isinstance(hours, (int, float)):
                issues.append(ValidationError(f"{qpath}.estimated_hours", "Must be a number"))
            elif isinstance(hours, (int, float)) and hours <= 0:
                issues.append(ValidationError(f"{qpath}.estimated_hours", "Must be > 0", "warning"))

            # --- Resources ---
            for ri, res in enumerate(topic.get("resources", [])):
                rpath = f"{qpath}.resources[{ri}]"
                if not isinstance(res, dict):
                    issues.append(ValidationError(rpath, "Resource must be a mapping"))
                    continue
                for field in ("title", "url"):
                    if field not in res:
                        issues.append(ValidationError(rpath, f"Missing required field: '{field}'"))
                rtype = res.get("type", "")
                if rtype and rtype not in _VALID_RESOURCE_TYPES:
                    issues.append(ValidationError(
                        f"{rpath}.type",
                        f"Unknown type '{rtype}'. Known types: {sorted(_VALID_RESOURCE_TYPES)}",
                        "warning",
                    ))

    # --- bridge_from ---
    bridge = data.get("bridge_from", {})
    if bridge and not isinstance(bridge, dict):
        issues.append(ValidationError("bridge_from", "Must be a mapping"))
    elif isinstance(bridge, dict):
        for key, entry in bridge.items():
            bpath = f"bridge_from.{key}"
            if key not in _CANONICAL_BRIDGE_KEYS:
                issues.append(ValidationError(
                    bpath,
                    f"Non-canonical key '{key}'. See CONTRIBUTING.md for the canonical list. "
                    "This reduces prep pivot coverage.",
                    "warning",
                ))
            if not isinstance(entry, dict):
                issues.append(ValidationError(bpath, "Entry must be a mapping"))
                continue
            for field in ("strengths", "gaps", "recommended_start"):
                if field not in entry:
                    issues.append(ValidationError(bpath, f"Missing field: '{field}'", "warning"))
            if entry.get("recommended_start") and topic_ids and track_ids:
                rec = entry["recommended_start"]
                if rec not in topic_ids and rec not in track_ids:
                    issues.append(ValidationError(
                        f"{bpath}.recommended_start",
                        f"'{rec}' not found in any track id or topic id",
                        "warning",
                    ))

    # --- interview_questions ---
    iq = data.get("interview_questions", {})
    if iq and not isinstance(iq, dict):
        issues.append(ValidationError("interview_questions", "Must be a mapping"))
    elif isinstance(iq, dict):
        for key in ("technical", "leadership"):
            if key in iq and not isinstance(iq[key], list):
                issues.append(ValidationError(f"interview_questions.{key}", "Must be a list"))

    # --- content_suggestions ---
    for ci, cs in enumerate(data.get("content_suggestions", [])):
        cpath = f"content_suggestions[{ci}]"
        if not isinstance(cs, dict):
            issues.append(ValidationError(cpath, "Must be a mapping"))
            continue
        for field in ("type", "title", "description"):
            if field not in cs:
                issues.append(ValidationError(cpath, f"Missing field: '{field}'", "warning"))
        ctype = cs.get("type", "")
        if ctype and ctype not in _VALID_CONTENT_TYPES:
            issues.append(ValidationError(
                f"{cpath}.type",
                f"Unknown type '{ctype}'. Known types: {sorted(_VALID_CONTENT_TYPES)}",
                "warning",
            ))

    return issues


# ---------------------------------------------------------------------------
# CLI commands
# ---------------------------------------------------------------------------

@click.group("template")
def template_cmd() -> None:
    """Template management commands."""


@template_cmd.command("validate")
@click.argument("path", type=click.Path(exists=True, dir_okay=False))
@click.option("--strict", is_flag=True, default=False,
              help="Treat warnings as errors.")
def validate_cmd(path: str, strict: bool) -> None:
    """Validate a template YAML file against the schema.

    \b
    Examples:
      prep template validate templates/my-role.yml
      prep template validate templates/my-role.yml --strict
    """
    try:
        import yaml
    except ImportError:
        click.echo("Error: PyYAML is required. Run: pip install pyyaml", err=True)
        sys.exit(1)

    try:
        with open(path) as f:
            data = yaml.safe_load(f)
    except Exception as exc:
        click.echo(click.style(f"✗ Failed to parse YAML: {exc}", fg="red"))
        sys.exit(1)

    if not isinstance(data, dict):
        click.echo(click.style("✗ Template must be a YAML mapping at the top level.", fg="red"))
        sys.exit(1)

    issues = _validate_template(data)
    errors = [i for i in issues if i.level == "error"]
    warnings = [i for i in issues if i.level == "warning"]

    fname = os.path.basename(path)
    click.echo()

    if not issues:
        click.echo(click.style(f"  ✓ {fname} — valid", fg="green", bold=True))
        click.echo()
        _print_summary(data)
        sys.exit(0)

    if errors:
        click.echo(click.style(f"  ✗ {fname} — {len(errors)} error(s), {len(warnings)} warning(s)", fg="red", bold=True))
    else:
        click.echo(click.style(f"  ⚠ {fname} — 0 errors, {len(warnings)} warning(s)", fg="yellow", bold=True))

    click.echo()
    if errors:
        click.echo(click.style("  Errors:", fg="red"))
        for e in errors:
            click.echo(click.style(str(e), fg="red"))
    if warnings:
        click.echo(click.style("  Warnings:", fg="yellow"))
        for w in warnings:
            click.echo(click.style(str(w), fg="yellow"))

    click.echo()
    _print_summary(data)

    if errors or (strict and warnings):
        sys.exit(1)
    sys.exit(0)


@template_cmd.command("list")
def list_cmd() -> None:
    """List all available templates."""
    try:
        from prep_agent.core.templates import TemplateLoader
    except ImportError as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)

    tl = TemplateLoader()
    templates = tl.list_templates()

    click.echo()
    click.echo(click.style(f"  {'Template ID':<35} {'Name':<35} {'Timeline'}", bold=True))
    click.echo("  " + "-" * 80)
    for meta in templates:
        tid = meta["id"]
        if tid == "custom":
            continue
        try:
            t = tl.load_template(tid)
            name = t.get("name", tid)
            timeline = t.get("suggested_timeline", "-")
            click.echo(f"  {tid:<35} {name:<35} {timeline}")
        except Exception:
            click.echo(f"  {tid:<35} (failed to load)")
    click.echo()


def _print_summary(data: dict) -> None:
    """Print a compact summary of the validated template."""
    name = data.get("name", "Unknown")
    tracks = data.get("tracks", [])
    topic_count = sum(len(t.get("topics", [])) for t in tracks)
    bridge_keys = list(data.get("bridge_from", {}).keys())
    timeline = data.get("suggested_timeline", "-")

    click.echo(click.style("  Summary:", bold=True))
    click.echo(f"    Name        : {name}")
    click.echo(f"    Timeline    : {timeline}")
    click.echo(f"    Tracks      : {len(tracks)}")
    click.echo(f"    Topics      : {topic_count}")
    if bridge_keys:
        click.echo(f"    bridge_from : {', '.join(bridge_keys)}")
    else:
        click.echo(click.style("    bridge_from : (none — prep pivot will not suggest this template)", fg="yellow"))
    click.echo()
