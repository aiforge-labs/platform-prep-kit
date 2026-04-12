"""Uvicorn server launcher for the Career Prep Agent web UI.

Called by ``prep serve`` — binds to localhost:8080 by default.
"""

from __future__ import annotations


def run(
    host: str = "127.0.0.1",
    port: int = 8080,
    reload: bool = False,
    open_browser: bool = True,
) -> None:
    """Start the web UI server.

    Parameters
    ----------
    host : bind address (default: localhost only — never exposed to network)
    port : TCP port (default: 8080)
    reload : enable auto-reload for development
    open_browser : open the dashboard in the default browser on startup
    """
    import uvicorn

    if host != "127.0.0.1" and host != "localhost":
        import click

        click.echo(
            click.style(
                f"WARNING: Binding to {host} exposes the server beyond localhost. "
                "This tool is designed for local use only.",
                fg="yellow",
            ),
            err=True,
        )

    if open_browser:
        import threading
        import time
        import webbrowser

        def _open():
            time.sleep(1.5)
            webbrowser.open(f"http://{host}:{port}")

        threading.Thread(target=_open, daemon=True).start()

    uvicorn.run(
        "prep_agent.web.app:create_app",
        host=host,
        port=port,
        reload=reload,
        factory=True,
        log_level="info",
    )
