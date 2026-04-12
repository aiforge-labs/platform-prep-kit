"""
View or regenerate the fitment analysis.

Shows how well your resume matches the target job, highlighting
strengths, gaps, and recommended focus areas.
"""

import click
import sys


@click.command("fitment")
@click.option("--with-ai", is_flag=True, default=False, help="Use AI for deeper fitment analysis.")
def fitment_cmd(with_ai):
    """View your fitment analysis (resume vs. job match)."""
    try:
        from prep_agent.core.analyzer import FitmentAnalyzer
        from prep_agent.core.config import load_config
        from prep_agent.integrations.ai_bridge import AIBridge
        from prep_agent.utils.display import print_fitment_report, info, warning, error
        from prep_agent.utils.file_ops import get_prep_dir
    except ImportError as exc:
        click.echo(f"Error: Missing dependency — {exc}", err=True)
        sys.exit(1)

    prep_dir = get_prep_dir()
    if not prep_dir.exists():
        error("No workspace found. Run 'prep init' first.")
        sys.exit(1)

    report_path = prep_dir / "fitment-analysis.md"

    # ------------------------------------------------------------------
    # AI-enhanced analysis
    # ------------------------------------------------------------------
    if with_ai:
        cfg = load_config()
        job_data = cfg.get("job")
        resume_data = cfg.get("resume")

        if not job_data or not resume_data:
            error("AI fitment requires both job and resume data.")
            info("Re-run 'prep init --job-url URL --resume PATH' to set them up.")
            return

        try:
            from rich.console import Console
            console = Console()
        except ImportError:
            console = None

        if console:
            with console.status("[bold green]Running AI-enhanced fitment analysis..."):
                analyzer = FitmentAnalyzer()
                fitment = analyzer.analyze(job_data, resume_data)
        else:
            click.echo("Running AI-enhanced fitment analysis...")
            analyzer = FitmentAnalyzer()
            fitment = analyzer.analyze(job_data, resume_data)

        if fitment:
            report_md = analyzer.generate_report_md(fitment)
            report_path.write_text(report_md, encoding="utf-8")
            print_fitment_report(fitment)
            info(f"Report saved to {report_path}")
        else:
            error("Fitment analysis failed. Check your configuration.")
        return

    # ------------------------------------------------------------------
    # Show saved analysis
    # ------------------------------------------------------------------
    if not report_path.exists():
        warning("No fitment analysis found.")
        info("Run 'prep init --job-url URL --resume PATH' to generate one,")
        info("or use 'prep fitment --with-ai' to generate with AI assistance.")
        return

    # Load and display the saved fitment
    cfg = load_config()
    fitment = cfg.get("fitment")

    if fitment:
        print_fitment_report(fitment)
    else:
        # Fall back to displaying the markdown file directly
        content = report_path.read_text(encoding="utf-8")
        click.echo(content)
