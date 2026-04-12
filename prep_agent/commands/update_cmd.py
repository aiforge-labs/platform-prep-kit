"""
Pull latest content (quiz banks, knowledge packs, templates) from GitHub.

Compares version numbers and only downloads newer content. Saves updates
to the user's local directory (~/.prep/) without overwriting package files.
"""

import click
import json
import os
import sys
import urllib.request
import urllib.error

_REPO = "aiforge-labs/career-prep-agent"
_API_BASE = f"https://api.github.com/repos/{_REPO}/contents"
_TIMEOUT = 15


@click.command("update")
def update_cmd():
    """Pull latest content updates from GitHub."""
    try:
        from prep_agent.utils.display import success, info, warning, error
    except ImportError as exc:
        click.echo(f"Error: Missing dependency — {exc}", err=True)
        sys.exit(1)

    prep_dir = os.path.expanduser("~/.prep")
    stats = {"updated": 0, "new": 0, "unchanged": 0, "errors": 0}

    info("Checking for content updates...")

    # Quiz banks
    _update_content(
        remote_path="quiz_banks",
        local_dir=os.path.join(prep_dir, "quiz_banks"),
        package_dir=os.path.normpath(
            os.path.join(os.path.dirname(__file__), "..", "..", "quiz_banks")
        ),
        ext=".json",
        version_key="version",
        stats=stats,
    )

    # Knowledge packs
    _update_content(
        remote_path="knowledge_packs",
        local_dir=os.path.join(prep_dir, "knowledge"),
        package_dir=os.path.normpath(
            os.path.join(os.path.dirname(__file__), "..", "..", "knowledge_packs")
        ),
        ext=".md",
        version_key=None,  # Markdown files don't have version fields
        stats=stats,
    )

    # Templates
    _update_content(
        remote_path="templates",
        local_dir=os.path.join(prep_dir, "templates"),
        package_dir=os.path.normpath(
            os.path.join(os.path.dirname(__file__), "..", "..", "templates")
        ),
        ext=".yml",
        version_key="version",
        stats=stats,
    )

    click.echo()
    if stats["new"] or stats["updated"]:
        success(
            f"Update complete: {stats['new']} new, {stats['updated']} updated, "
            f"{stats['unchanged']} unchanged"
        )
    else:
        info("Everything is up to date.")
    if stats["errors"]:
        warning(f"{stats['errors']} file(s) could not be updated.")


def _update_content(
    remote_path: str,
    local_dir: str,
    package_dir: str,
    ext: str,
    version_key: str | None,
    stats: dict,
) -> None:
    """Fetch a directory listing from GitHub and update local content."""
    from prep_agent.utils.display import info, warning

    url = f"{_API_BASE}/{remote_path}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "career-prep-agent"})
        with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:
            listing = json.loads(resp.read())
    except (urllib.error.URLError, OSError) as exc:
        warning(f"Could not fetch {remote_path}: {exc}")
        stats["errors"] += 1
        return

    if not isinstance(listing, list):
        return

    os.makedirs(local_dir, exist_ok=True)

    for entry in listing:
        name = entry.get("name", "")
        if not name.endswith(ext) or name.startswith("_"):
            continue

        download_url = entry.get("download_url")
        if not download_url:
            continue

        # Determine local version
        local_version = _get_local_version(name, local_dir, package_dir, version_key, ext)

        # Download remote file
        try:
            req = urllib.request.Request(download_url, headers={"User-Agent": "career-prep-agent"})
            with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:
                raw = resp.read().decode("utf-8")
        except (urllib.error.URLError, OSError):
            stats["errors"] += 1
            continue

        # Compare versions for structured files (JSON/YAML)
        remote_version = 0
        if version_key and ext == ".json":
            try:
                data = json.loads(raw)
                remote_version = data.get(version_key, 0)
            except json.JSONDecodeError:
                stats["errors"] += 1
                continue
        elif version_key and ext == ".yml":
            try:
                import yaml
                data = yaml.safe_load(raw)
                remote_version = data.get(version_key, 0) if isinstance(data, dict) else 0
            except Exception:
                stats["errors"] += 1
                continue
        else:
            # For markdown, always update if file doesn't exist locally
            remote_version = 1

        if remote_version > local_version:
            dest = os.path.join(local_dir, name)
            with open(dest, "w") as f:
                f.write(raw)
            if local_version == 0:
                stats["new"] += 1
                info(f"  New: {name}")
            else:
                stats["updated"] += 1
                info(f"  Updated: {name} (v{local_version} → v{remote_version})")
        else:
            stats["unchanged"] += 1


def _get_local_version(
    name: str, local_dir: str, package_dir: str, version_key: str | None, ext: str
) -> int:
    """Get the version of a local file (user dir first, then package dir)."""
    for directory in [local_dir, package_dir]:
        path = os.path.join(directory, name)
        if not os.path.isfile(path):
            continue

        if not version_key:
            return 1  # File exists but has no version field

        try:
            with open(path) as f:
                if ext == ".json":
                    data = json.load(f)
                    return data.get(version_key, 0)
                elif ext == ".yml":
                    import yaml
                    data = yaml.safe_load(f)
                    return data.get(version_key, 0) if isinstance(data, dict) else 0
        except Exception:
            return 0

    return 0  # File not found locally
