"""
Start the MCP server for IDE integration.

Allows any MCP-compatible client (Claude Code, Cursor, VS Code, etc.)
to interact with the career prep agent through standard MCP tools.
"""

import click
import sys


@click.command("mcp")
@click.option(
    "--transport",
    type=click.Choice(["stdio", "sse"]),
    default="stdio",
    help="MCP transport protocol (default: stdio).",
)
def mcp_cmd(transport):
    """Start the MCP server for IDE integration."""
    try:
        from prep_agent.mcp_server import mcp
    except ImportError as exc:
        click.echo(
            f"Error: MCP dependencies not installed. "
            f"Run: pip install career-prep-agent[mcp]\n({exc})",
            err=True,
        )
        sys.exit(1)

    click.echo(f"Starting Career Prep Agent MCP server ({transport})...", err=True)
    mcp.run(transport=transport)
