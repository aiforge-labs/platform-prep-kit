"""
Manage knowledge notes.

Add, list, view, and search personal study notes organized by topic.
"""

import click
import sys


def _load_deps():
    """Lazy-load knowledge base and display helpers."""
    try:
        from prep_agent.core.knowledge import KnowledgeBase
        from prep_agent.utils.display import success, info, warning, error
        from prep_agent.utils.file_ops import get_prep_dir
        return KnowledgeBase, success, info, warning, error, get_prep_dir
    except ImportError as exc:
        click.echo(f"Error: Missing dependency — {exc}", err=True)
        sys.exit(1)


def _ensure_workspace():
    """Check that the workspace exists."""
    _, _, _, _, error, get_prep_dir = _load_deps()
    prep_dir = get_prep_dir()
    if not prep_dir.exists():
        error("No workspace found. Run 'prep init' first.")
        sys.exit(1)


@click.group("note")
def note_cmd():
    """Manage your knowledge notes."""
    pass


@note_cmd.command("add")
@click.argument("topic", type=str)
@click.argument("content", type=str)
def note_add(topic, content):
    """Add a note to a topic.

    Example: prep note add 'System Design' 'CAP theorem: Consistency, Availability, Partition tolerance'
    """
    _ensure_workspace()
    KnowledgeBase, success, info, warning, error, _ = _load_deps()

    kb = KnowledgeBase()
    kb.add_note(topic=topic, content=content)
    success(f"Note added to '{topic}'.")


@note_cmd.command("list")
def note_list():
    """List all topics with notes."""
    _ensure_workspace()
    KnowledgeBase, success, info, warning, error, _ = _load_deps()

    kb = KnowledgeBase()
    topics = kb.list_topics()

    if not topics:
        info("No notes yet. Add one with 'prep note add TOPIC CONTENT'.")
        return

    info(f"Topics ({len(topics)}):")
    for t in sorted(topics):
        click.echo(f"  - {t}")


@note_cmd.command("show")
@click.argument("topic", type=str)
def note_show(topic):
    """Show all notes for a topic."""
    _ensure_workspace()
    KnowledgeBase, success, info, warning, error, _ = _load_deps()

    kb = KnowledgeBase()
    content = kb.get_topic(topic)

    if content is None:
        warning(f"No notes found for '{topic}'.")
        info("Use 'prep note list' to see available topics.")
        return

    info(f"Notes: {topic}")
    click.echo("=" * 60)
    click.echo(content)


@note_cmd.command("search")
@click.argument("query", type=str)
def note_search(query):
    """Search across all notes."""
    _ensure_workspace()
    KnowledgeBase, success, info, warning, error, _ = _load_deps()

    kb = KnowledgeBase()
    results = kb.search(query)

    if not results:
        info(f"No notes matching '{query}'.")
        return

    info(f"Search results for '{query}' ({len(results)} match{'es' if len(results) != 1 else ''}):")
    click.echo()
    for entry in results:
        topic = entry.get("topic", "Unknown")
        snippet = entry.get("snippet", "")
        click.echo(f"  [{topic}]")
        click.echo(f"    {snippet}")
        click.echo()
