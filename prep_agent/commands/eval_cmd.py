"""
Evaluate agent system reliability and learning effectiveness.

Exposes the AgentEvaluator through CLI subcommands: report, scenarios,
learning, and reliability.
"""

import click
import sys


@click.group("eval")
def eval_cmd():
    """Evaluate agent system reliability and learning effectiveness."""


def _get_evaluator():
    """Lazy-load and return an AgentEvaluator instance."""
    from prep_agent.agents.evaluation import AgentEvaluator

    return AgentEvaluator()


@eval_cmd.command("report")
@click.option("--output", "-o", type=click.Path(), default=None, help="Write report to file.")
def eval_report(output):
    """Generate a full evaluation report."""
    try:
        from prep_agent.utils.display import success, info, error
    except ImportError:
        success = info = error = click.echo

    evaluator = _get_evaluator()
    report = evaluator.generate_report()

    if output:
        with open(output, "w") as f:
            f.write(report)
        success(f"Report written to {output}")
    else:
        click.echo(report)


@eval_cmd.command("scenarios")
def eval_scenarios():
    """Run test scenarios and display pass/fail results."""
    try:
        from rich.console import Console
        from rich.table import Table

        console = Console()
    except ImportError:
        console = None

    evaluator = _get_evaluator()
    results = evaluator.run_test_scenarios()

    passed = sum(1 for s in results if s["passed"])
    total = len(results)

    if console:
        table = Table(title=f"Agent Test Scenarios ({passed}/{total} passed)")
        table.add_column("Scenario", style="bold")
        table.add_column("Expected")
        table.add_column("Actual")
        table.add_column("Status")

        for s in results:
            status = "[green]PASS[/green]" if s["passed"] else "[red]FAIL[/red]"
            actual = str(s["actual"])
            if len(actual) > 50:
                actual = actual[:47] + "..."
            table.add_row(s["scenario"], s["expected"], actual, status)

        console.print(table)
    else:
        click.echo(f"Agent Test Scenarios: {passed}/{total} passed\n")
        for s in results:
            status = "PASS" if s["passed"] else "FAIL"
            click.echo(f"  [{status}] {s['scenario']}: expected={s['expected']}, actual={s['actual']}")


@eval_cmd.command("learning")
@click.option("--topic", type=str, default=None, help="Filter by topic.")
def eval_learning(topic):
    """Show learning curve analysis."""
    try:
        from prep_agent.utils.display import info
    except ImportError:
        info = click.echo

    evaluator = _get_evaluator()
    curve = evaluator.get_learning_curve(topic)

    info(f"Learning Curve: {curve['topic']}")
    click.echo(f"  Trend: {curve['trend']}")
    click.echo(f"  Current mastery: {curve['mastery_pct']:.0f}%")
    click.echo(f"  Data points: {len(curve['scores_over_time'])}")

    if curve["scores_over_time"]:
        scores = curve["scores_over_time"]
        click.echo(f"  Scores: {', '.join(f'{s:.0f}' for s in scores[-10:])}")


@eval_cmd.command("reliability")
def eval_reliability():
    """Show agent decision reliability metrics."""
    try:
        from prep_agent.utils.display import info
    except ImportError:
        info = click.echo

    evaluator = _get_evaluator()
    rel = evaluator.get_agent_reliability()

    info("Agent Reliability")
    click.echo(f"  Total decisions: {rel['total_decisions']}")
    click.echo(f"  Error rate: {rel['error_rate']:.1%}")
    if rel["most_common_actions"]:
        click.echo("  Most common actions:")
        for action, count in rel["most_common_actions"].items():
            click.echo(f"    {action}: {count}")
