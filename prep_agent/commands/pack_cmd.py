"""
prep pack — Browse and read transition packs shipped with the kit.

Packs are self-contained, 12-week curricula that combine a structured plan,
STAR interview prompts, mock exercises, and rubrics. Each pack lives under
``packs/<pack-id>/`` at the repo root.

Subcommands:
  list          List all available packs.
  show          Display a pack's README.
  weeks         List the weeks in a pack's plan.
  week          Display a specific week's content.
  stories       List the STAR prompt categories in a pack.
  mocks         List the mock exercises in a pack.
"""

from __future__ import annotations

import os
import re
import sys

import click


# ---------------------------------------------------------------------------
# Path resolution
# ---------------------------------------------------------------------------

def _packs_root() -> str:
    """Return the absolute path to the packs/ directory shipped with the kit."""
    return os.path.normpath(
        os.path.join(os.path.dirname(__file__), "..", "..", "packs")
    )


def _resolve_pack(pack_id: str) -> str | None:
    """Return the absolute path to a pack directory, or None if not found."""
    root = _packs_root()
    path = os.path.join(root, pack_id)
    return path if os.path.isdir(path) else None


def _list_packs() -> list[str]:
    """Return the ids of all packs present on disk."""
    root = _packs_root()
    if not os.path.isdir(root):
        return []
    return sorted(
        d for d in os.listdir(root)
        if os.path.isdir(os.path.join(root, d)) and not d.startswith(".")
    )


def _pack_title(pack_path: str) -> str:
    """Extract the first-line title from a pack's README, or fall back to the id."""
    readme = os.path.join(pack_path, "README.md")
    if os.path.isfile(readme):
        try:
            with open(readme) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("# "):
                        return line[2:].strip()
        except OSError:
            pass
    return os.path.basename(pack_path)


def _week_files(pack_path: str) -> list[tuple[int, str]]:
    """Return list of (week_number, filename) tuples sorted by week number."""
    weeks_dir = os.path.join(pack_path, "weeks")
    if not os.path.isdir(weeks_dir):
        return []
    pattern = re.compile(r"^week-(\d+)-.*\.md$")
    result: list[tuple[int, str]] = []
    for fname in os.listdir(weeks_dir):
        m = pattern.match(fname)
        if m:
            result.append((int(m.group(1)), fname))
    result.sort()
    return result


def _story_files(pack_path: str) -> list[str]:
    stories_dir = os.path.join(pack_path, "stories")
    if not os.path.isdir(stories_dir):
        return []
    return sorted(
        f for f in os.listdir(stories_dir)
        if f.endswith(".md") and f != "README.md"
    )


def _mock_files(pack_path: str) -> list[str]:
    mocks_dir = os.path.join(pack_path, "mock")
    if not os.path.isdir(mocks_dir):
        return []
    return sorted(
        f for f in os.listdir(mocks_dir)
        if f.endswith(".md") and f != "README.md"
    )


def _read_title(path: str) -> str:
    """Read the first '# ' heading from a markdown file."""
    try:
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line.startswith("# "):
                    return line[2:].strip()
    except OSError:
        pass
    return os.path.basename(path)


def _print_file(path: str) -> None:
    """Stream a file's contents to stdout (unpaged)."""
    try:
        with open(path) as f:
            click.echo(f.read())
    except OSError as exc:
        click.echo(click.style(f"Error reading {path}: {exc}", fg="red"), err=True)
        sys.exit(1)


# ---------------------------------------------------------------------------
# Click group
# ---------------------------------------------------------------------------

@click.group("pack")
def pack_cmd() -> None:
    """Browse transition packs (structured 12-week curricula)."""


@pack_cmd.command("list")
def list_packs() -> None:
    """List all packs shipped with the kit."""
    packs = _list_packs()
    if not packs:
        click.echo("No packs found. Expected directory: packs/<pack-id>/")
        return

    click.echo()
    click.echo(click.style("  Pack ID".ljust(38) + "Title", bold=True))
    click.echo("  " + "-" * 72)
    for pid in packs:
        path = _resolve_pack(pid)
        if not path:
            continue
        title = _pack_title(path)
        click.echo(f"  {pid:<36}  {title}")
    click.echo()
    click.echo(f"  {len(packs)} pack(s). Use: prep pack show <pack-id>")
    click.echo()


@pack_cmd.command("show")
@click.argument("pack_id")
def show_pack(pack_id: str) -> None:
    """Display the pack's README."""
    path = _resolve_pack(pack_id)
    if not path:
        _pack_not_found(pack_id)

    readme = os.path.join(path, "README.md")
    if not os.path.isfile(readme):
        click.echo(f"Pack '{pack_id}' has no README.md")
        sys.exit(1)
    _print_file(readme)


@pack_cmd.command("weeks")
@click.argument("pack_id")
def list_weeks(pack_id: str) -> None:
    """List the weeks in a pack."""
    path = _resolve_pack(pack_id)
    if not path:
        _pack_not_found(pack_id)

    weeks = _week_files(path)
    if not weeks:
        click.echo(f"Pack '{pack_id}' has no weeks/ directory.")
        return

    click.echo()
    click.echo(click.style(f"  Weeks in '{pack_id}'", bold=True))
    click.echo("  " + "-" * 72)
    weeks_dir = os.path.join(path, "weeks")
    for num, fname in weeks:
        title = _read_title(os.path.join(weeks_dir, fname))
        click.echo(f"  {num:>2}. {title}")
    click.echo()
    click.echo(f"  {len(weeks)} week(s). Use: prep pack week {pack_id} <n>")
    click.echo()


@pack_cmd.command("week")
@click.argument("pack_id")
@click.argument("week_num", type=int)
@click.option("--quiz", "quiz_only", is_flag=True, default=False,
              help="Print the week's quiz command instead of the full content.")
def show_week(pack_id: str, week_num: int, quiz_only: bool) -> None:
    """Display a specific week's content (or its quiz command with --quiz)."""
    path = _resolve_pack(pack_id)
    if not path:
        _pack_not_found(pack_id)

    weeks = _week_files(path)
    match = next((f for n, f in weeks if n == week_num), None)
    if not match:
        available = ", ".join(str(n) for n, _ in weeks)
        click.echo(f"Week {week_num} not found in '{pack_id}'. Available: {available}")
        sys.exit(1)

    week_path = os.path.join(path, "weeks", match)

    if quiz_only:
        cmd = _extract_quiz_command(week_path)
        if cmd:
            click.echo(cmd)
        else:
            click.echo(f"No `prep quiz` command found in {match}", err=True)
            sys.exit(1)
        return

    _print_file(week_path)


def _extract_quiz_command(week_path: str) -> str | None:
    """Return the first `prep quiz ...` line in a week file, or None."""
    try:
        with open(week_path) as f:
            content = f.read()
    except OSError:
        return None
    match = re.search(r"^prep quiz[^\n]*", content, flags=re.MULTILINE)
    return match.group(0) if match else None


@pack_cmd.command("stories")
@click.argument("pack_id")
def list_stories(pack_id: str) -> None:
    """List the STAR prompt categories in a pack."""
    path = _resolve_pack(pack_id)
    if not path:
        _pack_not_found(pack_id)

    stories = _story_files(path)
    if not stories:
        click.echo(f"Pack '{pack_id}' has no stories/ directory.")
        return

    click.echo()
    click.echo(click.style(f"  STAR prompt categories in '{pack_id}'", bold=True))
    click.echo("  " + "-" * 72)
    stories_dir = os.path.join(path, "stories")
    for fname in stories:
        title = _read_title(os.path.join(stories_dir, fname))
        click.echo(f"  {fname:<40}  {title}")
    click.echo()


@pack_cmd.command("mocks")
@click.argument("pack_id")
def list_mocks(pack_id: str) -> None:
    """List the mock exercises in a pack."""
    path = _resolve_pack(pack_id)
    if not path:
        _pack_not_found(pack_id)

    mocks = _mock_files(path)
    if not mocks:
        click.echo(f"Pack '{pack_id}' has no mock/ directory.")
        return

    click.echo()
    click.echo(click.style(f"  Mock exercises in '{pack_id}'", bold=True))
    click.echo("  " + "-" * 72)
    mocks_dir = os.path.join(path, "mock")
    for fname in mocks:
        title = _read_title(os.path.join(mocks_dir, fname))
        click.echo(f"  {fname:<40}  {title}")
    click.echo()
    click.echo("  Use: prep pack mock <pack-id> <file> to display one")
    click.echo()


@pack_cmd.command("mock")
@click.argument("pack_id")
@click.argument("mock_file")
def show_mock(pack_id: str, mock_file: str) -> None:
    """Display a specific mock exercise file."""
    path = _resolve_pack(pack_id)
    if not path:
        _pack_not_found(pack_id)

    # Accept either "mock-1-idp-design.md" or "mock-1-idp-design" or "1"
    candidates = [mock_file]
    if not mock_file.endswith(".md"):
        candidates.append(f"{mock_file}.md")
    if mock_file.isdigit():
        mocks = _mock_files(path)
        n = int(mock_file)
        match = next((f for f in mocks if f.startswith(f"mock-{n}-")), None)
        if match:
            candidates.insert(0, match)

    mocks_dir = os.path.join(path, "mock")
    for cand in candidates:
        p = os.path.join(mocks_dir, cand)
        if os.path.isfile(p):
            _print_file(p)
            return

    click.echo(f"Mock '{mock_file}' not found in '{pack_id}'.")
    click.echo(f"Use: prep pack mocks {pack_id}")
    sys.exit(1)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _pack_not_found(pack_id: str) -> "None":  # never returns; exits
    click.echo(click.style(f"Pack '{pack_id}' not found.", fg="red"), err=True)
    packs = _list_packs()
    if packs:
        click.echo(f"Available: {', '.join(packs)}", err=True)
    click.echo("Use: prep pack list", err=True)
    sys.exit(1)
