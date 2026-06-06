"""
platform-prep-kit CLI — Main entry point.

A terminal-based career preparation assistant that helps you
plan, track, and execute a structured study schedule.
"""

from __future__ import annotations

import importlib
import sys
from typing import Any

import click

from prep_agent import __version__

# ---------------------------------------------------------------------------
# Lazy-loading helper
# ---------------------------------------------------------------------------

def _lazy_command(module_path: str, attr: str) -> click.BaseCommand | None:
    """Import *module_path* and return ``getattr(mod, attr)``.

    Returns ``None`` when the module cannot be imported so that a missing
    command file never crashes the entire CLI.
    """
    try:
        mod = importlib.import_module(module_path)
        return getattr(mod, attr)
    except (ImportError, AttributeError) as exc:
        click.echo(
            click.style(f"Warning: could not load {module_path}.{attr} ({exc})", fg="yellow"),
            err=True,
        )
        return None


# ---------------------------------------------------------------------------
# Top-level group
# ---------------------------------------------------------------------------

@click.group()
@click.version_option(version=__version__, prog_name="platform-prep-kit")
@click.pass_context
def prep(ctx: click.Context) -> None:
    """Platform Prep Kit — your terminal study-buddy.

    Plan a preparation schedule, track daily progress, take quizzes,
    and measure fitment against a target role.
    """
    ctx.ensure_object(dict)


# ---------------------------------------------------------------------------
# Register subcommands (lazy)
# ---------------------------------------------------------------------------

_COMMANDS: list[tuple[str, str]] = [
    ("prep_agent.commands.init_cmd",    "init_cmd"),
    ("prep_agent.commands.today_cmd",   "today_cmd"),
    ("prep_agent.commands.study_cmd",   "study_cmd"),
    ("prep_agent.commands.done_cmd",    "done_cmd"),
    ("prep_agent.commands.status_cmd",  "status_cmd"),
    ("prep_agent.commands.quiz_cmd",    "quiz_cmd"),
    ("prep_agent.commands.remind_cmd",  "remind_cmd"),
    ("prep_agent.commands.note_cmd",    "note_cmd"),
    ("prep_agent.commands.fitment_cmd", "fitment_cmd"),
    ("prep_agent.commands.export_cmd",  "export_cmd"),
    ("prep_agent.commands.eval_cmd",   "eval_cmd"),
    ("prep_agent.commands.mcp_cmd",    "mcp_cmd"),
    ("prep_agent.commands.pivot_cmd",   "pivot_cmd"),
    ("prep_agent.commands.template_cmd", "template_cmd"),
    ("prep_agent.commands.update_cmd",   "update_cmd"),
    ("prep_agent.commands.dashboard_cmd", "dashboard_cmd"),
    ("prep_agent.commands.insights_cmd",  "insights_cmd"),
    ("prep_agent.commands.build_cmd",    "build_cmd"),
    ("prep_agent.commands.serve_cmd",   "serve_cmd"),
    ("prep_agent.commands.pack_cmd",    "pack_cmd"),
]


def _register_commands() -> None:
    for module_path, attr in _COMMANDS:
        cmd = _lazy_command(module_path, attr)
        if cmd is not None:
            prep.add_command(cmd)


_register_commands()


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

def main() -> None:
    """Run the CLI. Called by the console-script entry point."""
    prep(standalone_mode=True)


if __name__ == "__main__":
    main()
