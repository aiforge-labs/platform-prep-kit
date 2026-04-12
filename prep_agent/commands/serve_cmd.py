"""Launch the Career Prep Agent web UI server."""

import click
import sys


@click.command("serve")
@click.option("--port", default=8080, show_default=True, help="Port to bind to.")
@click.option("--host", default="127.0.0.1", show_default=True, help="Host to bind to.")
@click.option("--no-open", is_flag=True, default=False, help="Don't open browser on startup.")
@click.option("--reload", is_flag=True, default=False, help="Enable auto-reload (development).")
def serve_cmd(port: int, host: str, no_open: bool, reload: bool) -> None:
    """Start the local web dashboard at http://localhost:8080."""
    try:
        from prep_agent.web.server import run
    except ImportError as exc:
        click.echo(
            click.style(
                f"Error: Web UI dependencies not installed. "
                f"Run: pip install career-prep-agent[ui]\n"
                f"  Missing: {exc}",
                fg="red",
            ),
            err=True,
        )
        sys.exit(1)

    click.echo(
        click.style(
            f"Starting Career Prep Agent web UI at http://{host}:{port}",
            fg="green",
        )
    )
    run(host=host, port=port, reload=reload, open_browser=not no_open)
