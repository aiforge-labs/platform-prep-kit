"""
Launch the local web dashboard.

Opens a Streamlit-based dashboard at localhost:8501 — fully local,
no data leaves your machine.
"""

import click
import os
import sys
import subprocess


@click.command("dashboard")
@click.option("--port", type=int, default=8501, help="Port to run the dashboard on.")
def dashboard_cmd(port):
    """Open the local web dashboard in your browser.

    NOTE: The Streamlit dashboard is deprecated. Use 'prep serve' for the
    new interactive web UI with quizzes, knowledge packs, and session tracking.
    """
    click.echo(
        click.style("NOTE ", fg="yellow", bold=True)
        + "The Streamlit dashboard is deprecated. "
        + "Use 'prep serve' for the new web UI."
    )
    try:
        import streamlit  # noqa: F401
    except ImportError:
        click.echo(
            click.style("Error: ", fg="red", bold=True)
            + "Streamlit is not installed. Install it with:\n\n"
            + "  pip install platform-prep-kit[dashboard]\n\n"
            + "Or:  pip install streamlit"
        )
        sys.exit(1)

    from prep_agent.utils.file_ops import get_prep_dir

    prep_dir = get_prep_dir()
    if not prep_dir.exists():
        click.echo(
            click.style("ERR ", fg="red", bold=True)
            + "No workspace found. Run 'prep init' first."
        )
        sys.exit(1)

    dashboard_path = os.path.join(os.path.dirname(__file__), "..", "dashboard.py")
    dashboard_path = os.path.abspath(dashboard_path)

    click.echo(
        click.style("INFO ", fg="cyan", bold=True)
        + f"Starting dashboard at http://localhost:{port}"
    )

    subprocess.run(
        [
            sys.executable, "-m", "streamlit", "run", dashboard_path,
            "--server.port", str(port),
            "--server.headless", "true",
            "--browser.gatherUsageStats", "false",
        ],
    )
