"""
Hands-on project generator and portfolio engine.

Manage portfolio projects that demonstrate your skills to interviewers.
"""

import sys

import click


@click.group("build")
def build_cmd():
    """Portfolio projects — build, evaluate, and showcase."""
    pass


# ---------------------------------------------------------------------------
# prep build (list available projects)
# ---------------------------------------------------------------------------


@build_cmd.command("list")
@click.option("--role", type=str, default=None, help="Filter by role template (e.g. ai-platform-engineer).")
def build_list(role):
    """List available portfolio projects ranked by gap impact."""
    try:
        from prep_agent.agents.project import ProjectAgent
        from prep_agent.core.tracker import Tracker
        from prep_agent.utils.display import console, info, warning
        from prep_agent.utils.file_ops import get_prep_dir
    except ImportError as exc:
        click.echo(f"Error: Missing dependency — {exc}", err=True)
        sys.exit(1)

    agent = ProjectAgent()
    templates = agent.load_project_templates(role)

    if not templates:
        warning("No project templates found." + (" Try without --role." if role else ""))
        return

    # Get quiz history for ranking
    quiz_history = []
    prep_dir = get_prep_dir()
    if prep_dir.exists():
        try:
            tracker = Tracker()
            state = tracker.load()
            quiz_history = state.get("quiz_history", [])
        except Exception:
            pass

    # Get completed project IDs
    completed_ids = {
        p["id"]
        for p in agent.list_user_projects()
        if p.get("status") == "completed"
    }
    in_progress_ids = {
        p["id"]
        for p in agent.list_user_projects()
        if p.get("status") == "in_progress"
    }

    ranked = agent.rank_projects(templates, quiz_history, completed_ids)

    from rich.table import Table

    table = Table(title="Available Projects")
    table.add_column("#", style="dim", width=3)
    table.add_column("ID", style="bold")
    table.add_column("Title")
    table.add_column("Difficulty")
    table.add_column("Hours", justify="right")
    table.add_column("Track")
    table.add_column("Status")

    for i, p in enumerate(ranked, 1):
        pid = p["id"]
        if pid in completed_ids:
            status = "[green]completed[/green]"
        elif pid in in_progress_ids:
            status = "[yellow]in progress[/yellow]"
        else:
            status = "[dim]available[/dim]"

        diff = p.get("difficulty", "—")
        diff_style = {"starter": "green", "intermediate": "yellow", "advanced": "red"}.get(diff, "white")

        table.add_row(
            str(i),
            pid,
            p.get("title", "—"),
            f"[{diff_style}]{diff}[/{diff_style}]",
            str(p.get("estimated_hours", "—")),
            p.get("track_id", "—"),
            status,
        )

    console.print(table)
    info(f"{len(ranked)} projects available, {len(completed_ids)} completed, {len(in_progress_ids)} in progress")


# ---------------------------------------------------------------------------
# prep build start <id>
# ---------------------------------------------------------------------------


@build_cmd.command("start")
@click.argument("project_id")
def build_start(project_id):
    """Scaffold a project and start working on it."""
    try:
        from prep_agent.agents.project import ProjectAgent
        from prep_agent.utils.display import success, info, warning, error
    except ImportError as exc:
        click.echo(f"Error: Missing dependency — {exc}", err=True)
        sys.exit(1)

    agent = ProjectAgent()

    # Check if already started
    existing = agent.get_user_project(project_id)
    if existing:
        warning(f"Project '{project_id}' already exists (status: {existing['status']}).")
        if not click.confirm("Reset and start fresh?", default=False):
            return

    # Find the template
    templates = agent.load_project_templates()
    spec = None
    for t in templates:
        if t["id"] == project_id:
            spec = t
            break

    if not spec:
        error(f"Project template '{project_id}' not found.")
        info("Run 'prep build list' to see available projects.")
        return

    entry = agent.start_project(spec)
    proj_dir = agent._projects_dir / project_id

    click.echo()
    success(f"Project scaffolded: {spec['title']}")
    info(f"Directory: {proj_dir}")
    info(f"Difficulty: {spec.get('difficulty', '—')} | Estimated: {spec.get('estimated_hours', '?')}h")

    click.echo()
    info("Starter files created:")
    for filename in spec.get("starter_files", {}):
        click.echo(f"  {filename}")

    rubric = spec.get("rubric", [])
    if rubric:
        click.echo()
        info(f"Rubric ({len(rubric)} items):")
        for i, r in enumerate(rubric):
            click.echo(f"  [ ] {r['description']}")

    click.echo()
    info("When done, run: prep build check " + project_id)


# ---------------------------------------------------------------------------
# prep build check <id>
# ---------------------------------------------------------------------------


@build_cmd.command("check")
@click.argument("project_id")
def build_check(project_id):
    """Self-evaluate a project against its rubric."""
    try:
        from prep_agent.agents.project import ProjectAgent
        from prep_agent.utils.display import success, info, warning, error, console
    except ImportError as exc:
        click.echo(f"Error: Missing dependency — {exc}", err=True)
        sys.exit(1)

    agent = ProjectAgent()
    entry = agent.get_user_project(project_id)

    if not entry:
        error(f"Project '{project_id}' not found. Run 'prep build start {project_id}' first.")
        return

    rubric = entry.get("rubric_results", [])
    if not rubric:
        warning("No rubric items for this project.")
        return

    click.echo()
    info(f"Rubric check for: {entry['title']}")
    click.echo()

    met_indices: list[int] = []
    for i, item in enumerate(rubric):
        done = click.confirm(f"  {item['description']}", default=item.get("met", False))
        if done:
            met_indices.append(i)

    updated = agent.check_project(project_id, met_indices)

    score = updated.get("rubric_score", 0)
    met_count = len(met_indices)
    total = len(rubric)

    click.echo()
    colour = "green" if score >= 80 else "yellow" if score >= 50 else "red"

    from rich.panel import Panel
    from rich.text import Text

    console.print(Panel(
        Text(f"{met_count}/{total} items met  ({score}%)", style=f"bold {colour}"),
        title="Rubric Score",
        border_style=colour,
        expand=False,
    ))

    if updated.get("status") == "completed":
        click.echo()
        success("Project complete! Run 'prep build showcase " + project_id + "' to generate a portfolio write-up.")
    else:
        remaining = [r for r in updated.get("rubric_results", []) if not r.get("met")]
        if remaining:
            click.echo()
            info("Remaining items:")
            for r in remaining:
                click.echo(f"  [ ] {r['description']}")


# ---------------------------------------------------------------------------
# prep build showcase <id>
# ---------------------------------------------------------------------------


@build_cmd.command("showcase")
@click.argument("project_id")
def build_showcase(project_id):
    """Generate a portfolio write-up for a project."""
    try:
        from prep_agent.agents.project import ProjectAgent
        from prep_agent.utils.display import success, info, warning, error
    except ImportError as exc:
        click.echo(f"Error: Missing dependency — {exc}", err=True)
        sys.exit(1)

    agent = ProjectAgent()
    entry = agent.get_user_project(project_id)

    if not entry:
        error(f"Project '{project_id}' not found.")
        return

    content = agent.generate_showcase(project_id)
    if not content:
        error("Could not generate showcase.")
        return

    showcase_path = agent._projects_dir / project_id / "SHOWCASE.md"

    click.echo()
    success(f"Portfolio write-up generated: {showcase_path}")
    info("Edit the SHOWCASE.md to fill in your descriptions, then share it!")

    click.echo()
    click.echo(content)


# ---------------------------------------------------------------------------
# prep build status
# ---------------------------------------------------------------------------


@build_cmd.command("status")
def build_status():
    """Show portfolio summary and hire-readiness score."""
    try:
        from prep_agent.agents.project import ProjectAgent
        from prep_agent.core.tracker import Tracker
        from prep_agent.utils.display import console, info
        from prep_agent.utils.file_ops import get_prep_dir
    except ImportError as exc:
        click.echo(f"Error: Missing dependency — {exc}", err=True)
        sys.exit(1)

    agent = ProjectAgent()

    # Get quiz avg for hire-readiness calculation
    quiz_avg = 0.0
    prep_dir = get_prep_dir()
    if prep_dir.exists():
        try:
            tracker = Tracker()
            progress = tracker.get_progress()
            quiz_avg = progress.get("avg_score", 0.0)
        except Exception:
            pass

    summary = agent.get_portfolio_summary(quiz_avg)

    from rich.panel import Panel
    from rich.table import Table

    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("metric", style="bold cyan")
    table.add_column("value")

    table.add_row("Projects Completed", str(summary["projects_completed"]))
    table.add_row("Projects In Progress", str(summary["projects_in_progress"]))
    table.add_row("Total Available", str(summary["total_projects_available"]))

    if summary["avg_rubric_score"] is not None:
        table.add_row("Avg Rubric Score", f"{summary['avg_rubric_score']}%")

    hr = summary["hire_readiness_pct"]
    hr_colour = "green" if hr >= 70 else "yellow" if hr >= 40 else "red"
    table.add_row("Hire Readiness", f"[{hr_colour}]{hr}%[/{hr_colour}]")

    console.print(Panel(table, title="Portfolio Summary", border_style="bright_blue", expand=False))

    skills = summary.get("skills_demonstrated", [])
    if skills:
        click.echo()
        info(f"Skills demonstrated ({len(skills)}):")
        for s in skills[:10]:
            click.echo(f"  + {s}")
        if len(skills) > 10:
            click.echo(f"  ... and {len(skills) - 10} more")
