"""
Initialize a new career prep workspace.

Handles job URL parsing, resume parsing, fitment analysis, study plan
generation, reminder setup, and workspace creation.
"""

import click
import sys
from pathlib import Path


def _check_deps():
    """Lazy-import core modules, returning them or exiting gracefully."""
    try:
        from prep_agent.core.config import (
            load_config, save_config, create_default_config, validate_config,
        )
        from prep_agent.core.planner import StudyPlanner
        from prep_agent.core.tracker import Tracker
        from prep_agent.core.analyzer import FitmentAnalyzer
        from prep_agent.integrations.job_fetcher import JobFetcher
        from prep_agent.integrations.resume_parser import ResumeParser
        from prep_agent.integrations.scheduler import Scheduler
        from prep_agent.utils.display import (
            print_banner, print_fitment_report, success, warning, error, info,
        )
        from prep_agent.utils.file_ops import get_prep_dir, ensure_prep_dir
        return {
            "load_config": load_config,
            "save_config": save_config,
            "create_default_config": create_default_config,
            "validate_config": validate_config,
            "StudyPlanner": StudyPlanner,
            "Tracker": Tracker,
            "FitmentAnalyzer": FitmentAnalyzer,
            "JobFetcher": JobFetcher,
            "ResumeParser": ResumeParser,
            "Scheduler": Scheduler,
            "print_banner": print_banner,
            "print_fitment_report": print_fitment_report,
            "success": success,
            "warning": warning,
            "error": error,
            "info": info,
            "get_prep_dir": get_prep_dir,
            "ensure_prep_dir": ensure_prep_dir,
        }
    except ImportError as exc:
        click.echo(f"Error: Missing dependency — {exc}", err=True)
        sys.exit(1)


@click.command("init")
@click.option("--job-url", type=str, default=None, help="URL of the job posting to prepare for.")
@click.option("--resume", type=click.Path(exists=True), default=None, help="Path to your resume (PDF/DOCX).")
@click.option("--template", type=str, default=None, help="Use a predefined study template (e.g. 'backend-sde', 'frontend').")
@click.option("--interactive/--no-interactive", default=True, help="Run in interactive mode (default: true).")
@click.option("--config", type=click.Path(exists=True), default=None, help="Path to an existing config YAML to import.")
@click.option("--minimal", is_flag=True, default=False, help="Create a minimal workspace without fitment analysis.")
def init_cmd(job_url, resume, template, interactive, config, minimal):
    """Initialize a new career-prep workspace.

    Sets up ~/.prep with study plan, tracker, and optional reminders.
    """
    deps = _check_deps()

    try:
        from rich.console import Console
        from rich.status import Status
        console = Console()
    except ImportError:
        console = None

    deps["print_banner"]()

    # ------------------------------------------------------------------
    # 1. Ensure workspace directory
    # ------------------------------------------------------------------
    prep_dir = deps["get_prep_dir"]()
    if prep_dir.exists():
        if interactive and not click.confirm(
            f"Workspace already exists at {prep_dir}. Reinitialize?", default=False
        ):
            deps["info"]("Aborted. Existing workspace left untouched.")
            return
    deps["ensure_prep_dir"]()

    # ------------------------------------------------------------------
    # 2. Bootstrap or import config
    # ------------------------------------------------------------------
    if config:
        cfg = deps["load_config"](config)
        deps["info"](f"Loaded config from {config}")
    else:
        if interactive and not minimal:
            target_role = click.prompt("Target role", type=str, default="")
            company = click.prompt("Target company", type=str, default="")
            weeks = click.prompt("Timeline (weeks)", type=int, default=8)
            hours = click.prompt("Study hours per week", type=int, default=15)
        else:
            target_role = "Career Transition"
            company = ""
            weeks = 8
            hours = 15
        cfg = deps["create_default_config"](
            target_role=target_role,
            company=company,
            timeline_weeks=weeks,
            hours_per_week=hours,
        )

    # ------------------------------------------------------------------
    # 2b. Apply template — convert tracks → gaps for the planner
    # ------------------------------------------------------------------
    if template:
        try:
            from prep_agent.core.templates import TemplateLoader
            tl = TemplateLoader()
            tmpl = tl.load_template(template)

            if not cfg.get("target", {}).get("role"):
                cfg.setdefault("target", {})["role"] = tmpl.get("name", template)

            # Derive timeline from suggested_timeline if not already set
            if not cfg.get("timeline", {}).get("weeks"):
                raw_timeline = tmpl.get("suggested_timeline", "")
                import re
                m = re.search(r"(\d+)", raw_timeline)
                if m:
                    cfg.setdefault("timeline", {})["weeks"] = int(m.group(1))

            # Convert template tracks → gaps list for planner
            gaps = []
            for track in tmpl.get("tracks", []):
                topic_names = [t.get("name", t.get("id", "")) for t in track.get("topics", [])]
                total_hours = sum(
                    t.get("estimated_hours", 4) for t in track.get("topics", [])
                )
                # Map template priority levels to planner priority levels
                priorities = [t.get("priority", "medium") for t in track.get("topics", [])]
                if "high" in priorities or "critical" in priorities:
                    priority = "high"
                elif "low" in priorities and all(p == "low" for p in priorities):
                    priority = "low"
                else:
                    priority = "moderate"

                track_name = track.get("name", track.get("id", ""))
                gaps.append({
                    "id": track.get("id", ""),
                    "name": track_name,
                    "topic": track_name,      # Pydantic Gap model requires singular "topic"
                    "topics": topic_names,
                    "estimated_hours": total_hours,
                    "priority": priority,
                })
            cfg["gaps"] = gaps
            cfg["template"] = template
            deps["success"](f"Template '{template}' loaded ({len(gaps)} tracks).")
        except Exception as exc:
            deps["warning"](f"Could not load template '{template}': {exc}")

    # ------------------------------------------------------------------
    # 3. Parse job URL
    # ------------------------------------------------------------------
    job_data = None
    if job_url:
        if console:
            with console.status("[bold green]Fetching job details..."):
                fetcher = deps["JobFetcher"]()
                job_data = fetcher.fetch_with_fallback(job_url)
        else:
            click.echo("Fetching job details...")
            fetcher = deps["JobFetcher"]()
            job_data = fetcher.fetch_with_fallback(job_url)

        if job_data:
            deps["success"](f"Parsed job: {job_data.get('title', 'Unknown Role')}")
            cfg["job"] = job_data
        else:
            deps["warning"]("Could not parse job URL. You can add job details later.")
    elif interactive and not minimal:
        if click.confirm("Do you have a job posting URL?", default=False):
            url = click.prompt("Job URL")
            fetcher = deps["JobFetcher"]()
            job_data = fetcher.fetch_with_fallback(url)
            if job_data:
                deps["success"](f"Parsed job: {job_data.get('title', 'Unknown Role')}")
                cfg["job"] = job_data

    # ------------------------------------------------------------------
    # 4. Parse resume
    # ------------------------------------------------------------------
    resume_data = None
    if resume:
        if console:
            with console.status("[bold green]Parsing resume..."):
                parser = deps["ResumeParser"]()
                resume_data = parser.parse(resume)
        else:
            click.echo("Parsing resume...")
            parser = deps["ResumeParser"]()
            resume_data = parser.parse(resume)

        if resume_data:
            deps["success"]("Resume parsed successfully.")
            cfg["resume"] = resume_data
        else:
            deps["warning"]("Could not parse resume. You can add it later.")
    elif interactive and not minimal:
        if click.confirm("Do you have a resume file to import?", default=False):
            path = click.prompt("Resume path (PDF or DOCX)")
            path = Path(path).expanduser()
            if path.exists():
                parser = deps["ResumeParser"]()
                resume_data = parser.parse(str(path))
                if resume_data:
                    deps["success"]("Resume parsed successfully.")
                    cfg["resume"] = resume_data
            else:
                deps["warning"](f"File not found: {path}")

    # ------------------------------------------------------------------
    # 5. Fitment analysis
    # ------------------------------------------------------------------
    fitment = None
    if not minimal and job_data and resume_data:
        if console:
            with console.status("[bold green]Running fitment analysis..."):
                analyzer = deps["FitmentAnalyzer"]()
                fitment = analyzer.analyze(job_data, resume_data)
        else:
            click.echo("Running fitment analysis...")
            analyzer = deps["FitmentAnalyzer"]()
            fitment = analyzer.analyze(job_data, resume_data)

        if fitment:
            report_md = analyzer.generate_report_md(fitment)
            report_path = prep_dir / "fitment-analysis.md"
            report_path.write_text(report_md, encoding="utf-8")
            deps["print_fitment_report"](fitment)
            cfg["fitment"] = fitment

    # ------------------------------------------------------------------
    # 6. Interactive gap / timeline questions
    # ------------------------------------------------------------------
    if interactive and not minimal and not template:
        click.echo()
        deps["info"]("Let's customize your study plan.")

        gaps = cfg.get("gaps", [])
        if not gaps:
            raw = click.prompt(
                "What are your key skill gaps? (comma-separated, or press Enter to skip)",
                default="",
            )
            if raw.strip():
                gap_names = [g.strip() for g in raw.split(",") if g.strip()]
                cfg["gaps"] = [
                    {
                        "id": name.lower().replace(" ", "-"),
                        "name": name,
                        "topic": name,
                        "topics": [name],
                        "estimated_hours": 8,
                        "priority": "high",
                    }
                    for name in gap_names
                ]

        weeks = click.prompt(
            "How many weeks do you want to prepare?", type=int, default=4
        )
        cfg.setdefault("timeline", {})["weeks"] = weeks
        from datetime import date, timedelta
        cfg["timeline"]["end_date"] = (
            date.today() + timedelta(weeks=weeks)
        ).isoformat()

        daily_hours = click.prompt(
            "Hours per day you can dedicate?", type=float, default=2.0
        )
        cfg["timeline"]["hours_per_day"] = daily_hours
        # Remove hours_per_week so planner uses hours_per_day directly
        cfg["timeline"].pop("hours_per_week", None)

    # ------------------------------------------------------------------
    # 7. Generate study plan
    # ------------------------------------------------------------------
    if console:
        with console.status("[bold green]Generating study plan..."):
            planner = deps["StudyPlanner"]()
            plan = planner.generate(cfg)
    else:
        click.echo("Generating study plan...")
        planner = deps["StudyPlanner"]()
        plan = planner.generate(cfg)

    plan_md = planner.generate_plan_md(plan, cfg)
    plan_path = prep_dir / "study-plan.md"
    plan_path.write_text(plan_md, encoding="utf-8")
    deps["success"](f"Study plan saved to {plan_path}")

    # ------------------------------------------------------------------
    # 8. Initialize tracker
    # ------------------------------------------------------------------
    tracker = deps["Tracker"]()
    tracker.initialize(plan, cfg)
    deps["success"]("Progress tracker initialized.")

    # ------------------------------------------------------------------
    # 9. Set up reminders
    # ------------------------------------------------------------------
    setup_reminders = False
    if interactive:
        setup_reminders = click.confirm("Set up daily study reminders?", default=True)
    if setup_reminders:
        morning = click.prompt("Morning reminder time (HH:MM)", default="08:00")
        evening = click.prompt("Evening reminder time (HH:MM)", default="20:00")
        scheduler = deps["Scheduler"]()
        scheduler.install(morning_time=morning, evening_time=evening)
        cfg["reminders"] = {"morning": morning, "evening": evening}
        deps["success"](f"Reminders set for {morning} and {evening}.")

    # ------------------------------------------------------------------
    # 10. Save config & finalize
    # ------------------------------------------------------------------
    deps["validate_config"](cfg)
    deps["save_config"](cfg)

    # Pydantic boundary validation (supplementary, non-fatal)
    try:
        from prep_agent.models import validate_config_dict

        _model, errors = validate_config_dict(cfg)
        if errors:
            deps["warning"](f"Pydantic validation notes ({len(errors)}):")
            for err in errors[:5]:
                click.echo(f"  - {err}")
    except Exception:
        pass  # Pydantic validation is optional

    deps["success"](f"Workspace created at {prep_dir}")
    click.echo()
    deps["info"]("Next steps:")
    click.echo("  prep today     — see what to study today")
    click.echo("  prep status    — view your dashboard")
    click.echo("  prep study     — start a study session")
