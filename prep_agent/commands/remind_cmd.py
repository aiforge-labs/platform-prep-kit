"""
Manage daily study reminders.

Provides subcommands to view, pause, resume, set, and skip reminders.
"""

import click
import sys
from datetime import datetime, timedelta


def _load_scheduler():
    """Lazy-load the Scheduler and display helpers."""
    try:
        from prep_agent.integrations.scheduler import Scheduler
        from prep_agent.utils.display import success, info, warning, error
        from prep_agent.utils.file_ops import get_prep_dir
        return Scheduler, success, info, warning, error, get_prep_dir
    except ImportError as exc:
        click.echo(f"Error: Missing dependency — {exc}", err=True)
        sys.exit(1)


def _ensure_workspace():
    """Check that the workspace exists, exit if not."""
    _, _, _, _, error, get_prep_dir = _load_scheduler()
    prep_dir = get_prep_dir()
    if not prep_dir.exists():
        error("No workspace found. Run 'prep init' first.")
        sys.exit(1)


@click.group("remind")
def remind_cmd():
    """Manage daily study reminders."""
    pass


@remind_cmd.command("status")
def remind_status():
    """Show the current reminder schedule."""
    _ensure_workspace()
    Scheduler, success, info, warning, error, _ = _load_scheduler()

    scheduler = Scheduler()
    status = scheduler.get_status()

    if status is None:
        info("No reminders configured. Use 'prep remind set' to set them up.")
        return

    info("Reminder Schedule:")
    click.echo(f"  Morning : {status.get('morning', 'not set')}")
    click.echo(f"  Evening : {status.get('evening', 'not set')}")
    click.echo(f"  Status  : {status.get('state', 'unknown')}")

    if status.get("paused_until"):
        click.echo(f"  Paused until: {status['paused_until']}")


@remind_cmd.command("pause")
@click.option("--until", "until_date", type=str, default=None, help="Pause until date (YYYY-MM-DD).")
@click.option("--hours", type=int, default=None, help="Pause for N hours.")
def remind_pause(until_date, hours):
    """Pause reminders temporarily."""
    _ensure_workspace()
    Scheduler, success, info, warning, error, _ = _load_scheduler()

    scheduler = Scheduler()

    if until_date:
        try:
            dt = datetime.strptime(until_date, "%Y-%m-%d")
        except ValueError:
            error("Invalid date format. Use YYYY-MM-DD.")
            sys.exit(1)
        scheduler.pause(until=dt)
        success(f"Reminders paused until {until_date}.")
    elif hours:
        resume_at = datetime.now() + timedelta(hours=hours)
        scheduler.pause(until=resume_at)
        success(f"Reminders paused for {hours} hour{'s' if hours != 1 else ''}.")
    else:
        scheduler.pause()
        success("Reminders paused indefinitely. Use 'prep remind resume' to restart.")


@remind_cmd.command("resume")
def remind_resume():
    """Resume paused reminders."""
    _ensure_workspace()
    Scheduler, success, info, warning, error, _ = _load_scheduler()

    scheduler = Scheduler()
    scheduler.resume()
    success("Reminders resumed.")


@remind_cmd.command("set")
@click.argument("morning_time", type=str)
@click.argument("evening_time", type=str)
def remind_set(morning_time, evening_time):
    """Set reminder times (e.g. 'prep remind set 08:00 20:00')."""
    _ensure_workspace()
    Scheduler, success, info, warning, error, _ = _load_scheduler()

    # Validate time format
    for label, t in [("Morning", morning_time), ("Evening", evening_time)]:
        try:
            datetime.strptime(t, "%H:%M")
        except ValueError:
            error(f"Invalid {label.lower()} time '{t}'. Use HH:MM format (e.g. 08:00).")
            sys.exit(1)

    scheduler = Scheduler()
    scheduler.update_time(morning_time=morning_time, evening_time=evening_time)
    success(f"Reminders set: morning at {morning_time}, evening at {evening_time}.")


@remind_cmd.command("skip")
def remind_skip():
    """Skip reminders for today only."""
    _ensure_workspace()
    Scheduler, success, info, warning, error, _ = _load_scheduler()

    scheduler = Scheduler()
    tomorrow = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
    scheduler.pause(until=tomorrow)
    success("Reminders skipped for today. They'll resume tomorrow.")
