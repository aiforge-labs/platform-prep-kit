"""
prep pivot — Role transition recommender.

Reads bridge_from metadata across all templates and ranks pivot targets
by skill overlap and estimated ramp time for the user's current role.
"""

from __future__ import annotations

import re
import sys

import click


# ---------------------------------------------------------------------------
# Scoring helpers
# ---------------------------------------------------------------------------

# Canonical aliases: normalise variants to a single key
_ROLE_ALIASES: dict[str, str] = {
    # software / backend
    "software_engineering": "software_engineering",
    "software_engineer": "software_engineering",
    "backend_engineering": "backend_engineering",
    "backend_engineer": "backend_engineering",
    "web_development": "web_development",
    "web_developer": "web_development",
    # cloud
    "cloud_engineering": "cloud_engineering",
    "cloud_engineer": "cloud_engineering",
    # devops / sre — treat devops_engineer and devops_sre as the same bucket
    "devops_sre": "devops_sre",
    "devops_engineer": "devops_sre",
    "sre": "devops_sre",
    "site_reliability_engineer": "devops_sre",
    # infrastructure
    "infrastructure_engineering": "infrastructure_engineering",
    "infrastructure_engineer": "infrastructure_engineering",
    "system_administration": "system_administration",
    "sysadmin": "system_administration",
    # security
    "security_engineering": "security_engineering",
    "security_engineer": "security_engineering",
    "cloud_security": "cloud_security",
    "penetration_testing": "penetration_testing",
    "pentester": "penetration_testing",
    "network_security": "network_security",
    "security_operations": "security_operations",
    "soc_analyst": "security_operations",
    # ML / data — treat ml_engineer and ml_engineering as the same
    "ml_engineering": "ml_engineering",
    "ml_engineer": "ml_engineering",
    "data_engineering": "data_engineering",
    "data_engineer": "data_engineering",
    "data_scientist": "data_scientist",
    # compliance / audit
    "audit_compliance": "audit_compliance",
    # customer-facing
    "customer_success": "customer_success",
    "technical_support": "technical_support",
    "network_engineering": "network_engineering",
    "network_engineer": "network_engineering",
}


def _normalise_role(role: str) -> str:
    key = role.lower().replace("-", "_").replace(" ", "_")
    return _ROLE_ALIASES.get(key, key)


def _parse_timeline_weeks(timeline: str) -> float:
    """Extract the midpoint number of weeks from strings like '8-10 weeks'."""
    nums = re.findall(r"\d+", timeline or "")
    if not nums:
        return 10.0
    values = [int(n) for n in nums]
    return sum(values) / len(values)


def _score_pivot(
    source_role: str,
    template: dict,
    template_id: str = "",
) -> dict | None:
    """Score a single template as a pivot target for source_role.

    Returns a result dict or None if the template has no bridge_from entry
    for the source role.

    Scoring:
    - skill_overlap (0–100): strengths count / (strengths + gaps) × 100
    - gap_count: number of skill gaps to close
    - ramp_weeks: adjusted from suggested_timeline, reduced by overlap %
    - score: composite (overlap% × 2 - gap_count × 3), higher = better pivot
    """
    bridge = template.get("bridge_from", {})
    if not bridge:
        return None

    # Normalise the query role, then try against all normalised bridge keys
    norm_source = _normalise_role(source_role)
    entry = None
    for key, val in bridge.items():
        if _normalise_role(key) == norm_source:
            entry = val
            break
    if not entry:
        return None

    strengths = entry.get("strengths", [])
    gaps = entry.get("gaps", [])
    total = len(strengths) + len(gaps)
    overlap_pct = round(len(strengths) / total * 100) if total > 0 else 0

    base_weeks = _parse_timeline_weeks(template.get("suggested_timeline", ""))
    # Ramp time shrinks as overlap grows (min 40% of base)
    ramp_weeks = round(base_weeks * max(0.4, 1 - overlap_pct / 200), 1)

    score = overlap_pct * 2 - len(gaps) * 3

    return {
        "template_id": template_id or template.get("id", ""),
        "template_name": template.get("name", template_id),
        "overlap_pct": overlap_pct,
        "strengths": strengths,
        "gaps": gaps,
        "ramp_weeks": ramp_weeks,
        "recommended_start": entry.get("recommended_start", ""),
        "score": score,
    }


# ---------------------------------------------------------------------------
# CLI command
# ---------------------------------------------------------------------------

@click.command("pivot")
@click.option(
    "--from", "source_role",
    required=True,
    help="Your current role (e.g. software_engineering, cloud_engineering, devops_sre).",
)
@click.option(
    "--top", "top_n",
    default=5,
    show_default=True,
    help="Number of pivot targets to show.",
)
@click.option(
    "--all", "show_all",
    is_flag=True,
    default=False,
    help="Show all templates, not just those with a bridge_from match.",
)
def pivot_cmd(source_role: str, top_n: int, show_all: bool) -> None:
    """Recommend role transitions ranked by skill overlap and ramp time.

    Uses bridge_from metadata in prep templates to score each target role
    based on how much of your current skill set transfers.

    \b
    Examples:
      prep pivot --from software_engineering
      prep pivot --from cloud_engineering --top 3
      prep pivot --from devops_sre --all
    """
    try:
        from prep_agent.core.templates import TemplateLoader
        from prep_agent.utils.display import info, warning, success, error
    except ImportError as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)

    normalised = _normalise_role(source_role)

    tl = TemplateLoader()
    template_metas = tl.list_templates()

    results: list[dict] = []
    unmatched: list[str] = []

    for meta in template_metas:
        tmpl_id = meta["id"]
        if tmpl_id == "custom":
            continue
        try:
            tmpl = tl.load_template(tmpl_id)
        except Exception:
            continue

        scored = _score_pivot(normalised, tmpl, tmpl_id)
        if scored:
            results.append(scored)
        elif show_all:
            unmatched.append(tmpl.get("name", tmpl_id))

    if not results:
        warning(f"No templates have a bridge_from entry for '{source_role}'.")
        click.echo()
        click.echo("Known source roles:")
        for alias in sorted(set(_ROLE_ALIASES.values())):
            click.echo(f"  {alias}")
        return

    # Sort: highest score first, then by ramp_weeks ascending as tiebreaker
    results.sort(key=lambda r: (-r["score"], r["ramp_weeks"]))
    display = results[:top_n]

    click.echo()
    click.echo(click.style("=" * 65, fg="cyan"))
    click.echo(
        click.style(
            f"  Role Pivot Recommendations — from: {source_role}",
            fg="cyan",
            bold=True,
        )
    )
    click.echo(click.style("=" * 65, fg="cyan"))

    for rank, r in enumerate(display, start=1):
        overlap = r["overlap_pct"]

        # Colour-code overlap
        if overlap >= 60:
            overlap_style = click.style(f"{overlap}%", fg="green", bold=True)
        elif overlap >= 40:
            overlap_style = click.style(f"{overlap}%", fg="yellow", bold=True)
        else:
            overlap_style = click.style(f"{overlap}%", fg="red", bold=True)

        click.echo()
        click.echo(
            click.style(f"  #{rank}  {r['template_name']}", bold=True)
            + f"  [{r['template_id']}]"
        )
        click.echo(
            f"       Skill overlap : {overlap_style}"
            f"   |   Est. ramp time : {r['ramp_weeks']} weeks"
        )

        if r["strengths"]:
            click.echo(
                "       "
                + click.style("Transfers well: ", fg="green")
                + "; ".join(r["strengths"][:2])
                + ("..." if len(r["strengths"]) > 2 else "")
            )

        if r["gaps"]:
            click.echo(
                "       "
                + click.style("Key gaps:       ", fg="yellow")
                + "; ".join(r["gaps"][:2])
                + ("..." if len(r["gaps"]) > 2 else "")
            )

        if r["recommended_start"]:
            click.echo(
                "       "
                + click.style("Start with:     ", fg="cyan")
                + r["recommended_start"]
            )

    click.echo()
    click.echo(click.style("-" * 65, fg="bright_black"))

    # Quick start hint
    if display:
        best = display[0]
        click.echo(
            click.style("  Quick start: ", bold=True)
            + f"prep init --template {best['template_id']}"
        )

    if unmatched:
        click.echo()
        click.echo(
            click.style("  Templates without a bridge entry for this role: ", fg="bright_black")
            + ", ".join(unmatched)
        )

    click.echo()
