"""
Start or continue a study session.

Can run standalone (showing knowledge pack and resources) or with an
AI-assisted interactive session via AIBridge.
"""

import click
import sys


@click.command("study")
@click.option("--with-ai", is_flag=True, default=False, help="Launch an AI-assisted study session.")
@click.option("--topic", type=str, default=None, help="Override today's topic with a specific one.")
@click.option("--weak", is_flag=True, default=False, help="Study your weakest topic based on quiz scores.")
def study_cmd(with_ai, topic, weak):
    """Start a study session for today's topic (or a custom topic)."""
    try:
        from prep_agent.core.tracker import Tracker
        from prep_agent.core.config import load_config
        from prep_agent.core.knowledge import KnowledgeBase
        from prep_agent.integrations.ai_bridge import AIBridge
        from prep_agent.utils.display import (
            success, info, warning, error,
            print_agent_recommendations, print_reasoning_trace,
        )
        from prep_agent.utils.file_ops import get_prep_dir
    except ImportError as exc:
        click.echo(f"Error: Missing dependency — {exc}", err=True)
        sys.exit(1)

    prep_dir = get_prep_dir()
    if not prep_dir.exists():
        error("No workspace found. Run 'prep init' first.")
        sys.exit(1)

    cfg = load_config()
    tracker = Tracker()
    tracker.load()

    # --weak mode: auto-select weakest topic
    if weak:
        from prep_agent.core.quiz_engine import QuizEngine
        engine = QuizEngine()
        weak_topics = engine.suggest_review_topics()
        if not weak_topics:
            info("No weak areas identified yet. Take some quizzes first!")
            info("Try: prep quiz --topic <topic>")
            return
        topic = weak_topics[0]
        info(f"Weakest topic: {topic}")

    # Determine topic
    if topic:
        study_topic = topic
        today_entry = None
        info(f"Studying custom topic: {study_topic}")
    else:
        today_entry = tracker.get_today()
        if today_entry is None:
            warning("No study session scheduled for today.")
            info("Use --topic to study a specific topic, or check 'prep today'.")
            return
        study_topic = today_entry.get("topic", "General")
        if today_entry.get("done"):
            if not click.confirm("Today's session is already marked done. Study again?", default=False):
                return

    click.echo()
    info(f"Topic: {study_topic}")
    click.echo("=" * 60)

    # ------------------------------------------------------------------
    # Agent-powered session adaptation
    # ------------------------------------------------------------------
    approach = ""
    try:
        from prep_agent.agents.orchestrator import Orchestrator
        from prep_agent.agents.context import build_agent_context

        ctx = build_agent_context(tracker.load(), cfg, today_entry)
        ctx["topic"] = study_topic  # ensure custom topic overrides
        orchestrator = Orchestrator(cfg)
        agent_result = orchestrator.handle_session("study", ctx)

        session_info = agent_result.get("session", {})
        approach = session_info.get("approach", "")
        if approach:
            info(f"Approach: {approach}")
            trace = session_info.get("reasoning_trace", [])
            print_reasoning_trace(trace)
            click.echo()
    except Exception:
        pass  # Agent integration is best-effort

    # ------------------------------------------------------------------
    # AI-assisted session
    # ------------------------------------------------------------------
    if with_ai:
        try:
            from rich.console import Console
            console = Console()
        except ImportError:
            console = None

        info("Starting AI-assisted study session...")
        bridge = AIBridge(config=cfg)

        tracker_state = tracker.load()
        # Pass approach hint to prompt builder
        if approach:
            tracker_state["approach"] = approach

        if console:
            with console.status("[bold green]Generating session..."):
                session_text = bridge.generate_session(
                    topic=study_topic,
                    tracker_data=tracker_state,
                )
        else:
            session_text = bridge.generate_session(
                topic=study_topic,
                tracker_data=tracker_state,
            )

        if session_text:
            click.echo()
            click.echo(session_text)
            click.echo()
            success("AI session ready. Good luck!")

            # Log session for future reference
            try:
                import os
                from datetime import date
                sessions_dir = os.path.join(str(prep_dir), "sessions")
                os.makedirs(sessions_dir, exist_ok=True)
                slug = study_topic.lower().replace(" ", "-")[:40]
                session_path = os.path.join(sessions_dir, f"{date.today().isoformat()}-{slug}.md")
                with open(session_path, "w") as f:
                    f.write(f"# Study Session: {study_topic}\n\n{session_text}")
            except Exception:
                pass
        else:
            error("Could not generate AI session. Try again or study without --with-ai.")
        return

    # ------------------------------------------------------------------
    # Standalone session — show knowledge pack + resources
    # ------------------------------------------------------------------
    kb = KnowledgeBase()

    # Show knowledge pack content
    topic_content = kb.get_topic(study_topic)
    if topic_content:
        click.echo()
        info("Knowledge Pack:")
        click.echo(topic_content)
    else:
        info(f"No knowledge pack found for '{study_topic}'. Add notes with 'prep note add'.")

    # Show study guide from the entry
    if today_entry:
        guide = today_entry.get("guide")
        if guide:
            click.echo()
            info("Study Guide:")
            click.echo(guide)

        resources = today_entry.get("resources", [])
        if resources:
            click.echo()
            info("Resources:")
            for r in resources:
                click.echo(f"  - {r}")

        tasks = today_entry.get("tasks", [])
        if tasks:
            click.echo()
            info("Tasks:")
            for i, task in enumerate(tasks, 1):
                click.echo(f"  [ ] {i}. {task}")

    click.echo()
    click.echo("-" * 60)
    info("When finished, run 'prep done' to log your progress.")
