"""
Run quizzes and mock interviews.

Supports local quiz banks, AI-generated quiz prompts, and mock interview
prompts. Results are logged to the tracker for progress analysis.
"""

import click
import sys


@click.command("quiz")
@click.option("--topic", type=str, default=None, help="Quiz topic or quiz bank id (defaults to today's topic).")
@click.option("--difficulty", type=click.Choice(["easy", "medium", "hard"]), default=None,
              help="Filter questions by difficulty level.")
@click.option("--tag", type=str, default=None,
              help="Filter questions by tag (e.g., 'gitops', 'devex'). Use --list-tags to discover.")
@click.option("--list", "list_banks", is_flag=True, default=False,
              help="List all available quiz banks with question counts.")
@click.option("--list-tags", "list_tags_flag", is_flag=True, default=False,
              help="List tags available in the selected --topic bank.")
@click.option("--mock-interview", is_flag=True, default=False, help="Generate a mock interview prompt instead.")
@click.option("--num", type=int, default=5, help="Number of questions (default: 5).")
@click.option("--copy", is_flag=True, default=False, help="Copy AI quiz prompt to clipboard instead of running locally.")
@click.option("--generate", is_flag=True, default=False, help="Generate new quiz questions using AI and save locally.")
@click.option("--import-file", "import_file", type=str, default=None, help="Import quiz bank from a JSON file path or URL.")
@click.option("--review", is_flag=True, default=False, help="Review previously missed questions (spaced repetition).")
def quiz_cmd(topic, difficulty, tag, list_banks, list_tags_flag, mock_interview, num, copy, generate, import_file, review):
    """Run a quiz or generate a mock interview prompt."""
    try:
        from prep_agent.core.tracker import Tracker
        from prep_agent.core.quiz_engine import QuizEngine
        from prep_agent.core.config import load_config
        from prep_agent.utils.display import (
            print_quiz_result, print_agent_recommendations,
            success, info, warning, error,
        )
        from prep_agent.utils.file_ops import get_prep_dir
    except ImportError as exc:
        click.echo(f"Error: Missing dependency — {exc}", err=True)
        sys.exit(1)

    # ------------------------------------------------------------------
    # List mode — works without an initialised workspace
    # ------------------------------------------------------------------
    if list_banks:
        _print_quiz_banks()
        return

    # ------------------------------------------------------------------
    # List tags for a bank — works without an initialised workspace
    # ------------------------------------------------------------------
    if list_tags_flag:
        if not topic:
            error("--list-tags requires --topic <bank-id>.")
            sys.exit(1)
        from prep_agent.core.quiz_engine import QuizEngine as _QE
        _print_bank_tags(topic, _QE())
        return

    # ------------------------------------------------------------------
    # Import mode — works without an initialised workspace
    # ------------------------------------------------------------------
    if import_file:
        _handle_import(import_file)
        return

    prep_dir = get_prep_dir()
    if not prep_dir.exists():
        error("No workspace found. Run 'prep init' first.")
        sys.exit(1)

    cfg = load_config()
    tracker = Tracker()
    tracker.load()

    # Determine topic
    if topic is None:
        today_entry = tracker.get_today()
        if today_entry:
            topic = today_entry.get("topic", "General")
        else:
            topic = "General"
        info(f"Using topic: {topic}")

    engine = QuizEngine()

    # ------------------------------------------------------------------
    # Generate mode — create quiz questions with AI
    # ------------------------------------------------------------------
    if generate:
        _handle_generate(engine, topic, num, cfg)
        return

    # ------------------------------------------------------------------
    # Review mode — spaced repetition of missed questions
    # ------------------------------------------------------------------
    if review:
        _handle_review(engine, tracker, topic, num)
        return

    # ------------------------------------------------------------------
    # Mock interview mode
    # ------------------------------------------------------------------
    if mock_interview:
        prompt = engine.generate_mock_interview_prompt(target_role=topic)
        if copy:
            _copy_to_clipboard(prompt)
            success("Mock interview prompt copied to clipboard.")
        else:
            click.echo()
            info("Mock Interview Prompt:")
            click.echo("=" * 60)
            click.echo(prompt)
            click.echo("=" * 60)
            click.echo()
            info("Paste this into your preferred AI assistant to start the interview.")
        return

    # ------------------------------------------------------------------
    # Copy AI quiz prompt to clipboard
    # ------------------------------------------------------------------
    if copy:
        prompt = engine.generate_ai_quiz_prompt(topic=topic, num_questions=num)
        _copy_to_clipboard(prompt)
        success(f"AI quiz prompt for '{topic}' ({num} questions) copied to clipboard.")
        return

    # ------------------------------------------------------------------
    # Agent-powered difficulty adaptation (only when --difficulty not set)
    # ------------------------------------------------------------------
    effective_difficulty = difficulty
    agent_num = num
    try:
        from prep_agent.agents.orchestrator import Orchestrator
        from prep_agent.agents.context import build_agent_context

        ctx = build_agent_context(tracker.load(), cfg)
        ctx["topic"] = topic
        orchestrator = Orchestrator(cfg)
        agent_result = orchestrator.handle_session("quiz", ctx)

        quiz_prep = agent_result.get("quiz", {})
        suggested_num = quiz_prep.get("num_questions")
        if suggested_num:
            agent_num = suggested_num
        if not effective_difficulty:
            agent_difficulty = quiz_prep.get("difficulty")
            if agent_difficulty:
                effective_difficulty = agent_difficulty
                mastery = quiz_prep.get("mastery_before", 0)
                info(f"Agent recommends {effective_difficulty} difficulty (mastery: {mastery:.0f}%)")
    except Exception:
        pass  # Agent integration is best-effort

    if effective_difficulty:
        info(f"Difficulty filter: {effective_difficulty}")
    if tag:
        info(f"Tag filter: {tag}")

    # ------------------------------------------------------------------
    # Local interactive quiz
    # ------------------------------------------------------------------
    questions = engine.get_questions(
        topic_id=topic,
        num_questions=agent_num,
        difficulty=effective_difficulty,
        tag=tag,
    )

    # If agent-suggested difficulty yields nothing, fall back to unfiltered
    if not questions and effective_difficulty and not difficulty:
        info(f"No '{effective_difficulty}' questions found — using all difficulties.")
        effective_difficulty = None
        questions = engine.get_questions(
            topic_id=topic,
            num_questions=agent_num,
            difficulty=None,
            tag=tag,
        )

    if not questions:
        if tag and difficulty:
            warning(f"No questions for topic='{topic}' tag='{tag}' difficulty='{difficulty}'.")
            info("Try --list-tags --topic {topic} to see available tags.")
        elif tag:
            warning(f"No questions tagged '{tag}' in '{topic}'.")
            info(f"Try: prep quiz --topic {topic} --list-tags")
        elif difficulty:
            warning(f"No '{difficulty}' questions found for '{topic}'.")
            info("Try without --difficulty to see all available questions.")
        else:
            warning(f"No local quiz questions found for '{topic}'.")
            info(f"Available banks: prep quiz --list")
            info("Use --copy to generate an AI quiz prompt instead.")
        return

    info(f"Starting quiz: {topic} ({len(questions)} questions)")
    click.echo("-" * 60)

    result = engine.run_interactive_quiz(questions)

    # Display result
    score = result.get("score", 0)
    total = result.get("total", 0)
    weak_areas = result.get("weak_areas", [])

    click.echo()
    print_quiz_result(
        score=score,
        total=total,
        topic=topic,
        weak_areas=weak_areas,
    )

    # Log to tracker
    engine.log_result(topic=topic, score=score, total=total, weak_areas=weak_areas or None)
    tracker.log_quiz(
        topic=topic,
        score=score,
        total=total,
        weak_areas=weak_areas or None,
    )
    pct = (score / total * 100) if total > 0 else 0

    click.echo()
    if pct >= 80:
        success(f"Great job! {score}/{total} ({pct:.0f}%)")
    elif pct >= 50:
        info(f"Good effort: {score}/{total} ({pct:.0f}%). Review the missed topics.")
    else:
        warning(f"Score: {score}/{total} ({pct:.0f}%). Consider revisiting this topic.")


def _handle_generate(engine, topic: str, num: int, cfg: dict) -> None:
    """Generate quiz questions using AI and save locally."""
    from prep_agent.utils.display import success, info, warning, error
    import json as _json

    prompt = engine.generate_quiz_bank_prompt(topic, num_questions=num)
    provider = cfg.get("ai_integration", {}).get("provider", "none")
    topic_id = topic.lower().replace(" ", "-") + "-generated"

    # Try Ollama first if configured
    if provider == "ollama":
        info("Generating questions via Ollama...")
        try:
            import urllib.request
            payload = _json.dumps({
                "model": "llama3",
                "prompt": prompt,
                "stream": False,
                "format": "json",
            }).encode()
            req = urllib.request.Request(
                "http://localhost:11434/api/generate",
                data=payload,
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(req, timeout=120) as resp:
                body = _json.loads(resp.read())
            raw_text = body.get("response", "")
            data = _json.loads(raw_text)
            errors = engine.validate_bank(data)
            if not errors:
                path = engine.save_bank(topic_id, data)
                n = len(data.get("questions", []))
                success(f"Generated {n} questions → {path}")
                info("Run: prep quiz --list  to see the new bank.")
                return
            else:
                warning(f"Ollama returned invalid JSON: {errors[0]}")
                info("Falling back to clipboard mode...")
        except Exception as exc:
            warning(f"Ollama unavailable ({exc}). Falling back to clipboard mode...")

    # Clipboard / paste-back fallback
    _copy_to_clipboard(prompt)
    info("Quiz generation prompt copied to clipboard (also shown below).")
    click.echo()
    click.echo(prompt)
    click.echo()
    info("Paste this into any AI assistant, then paste the JSON response below.")
    info("(Enter an empty line when done)")
    click.echo()

    lines = []
    while True:
        line = click.get_text_stream("stdin").readline()
        if line.strip() == "":
            if lines:
                break
            continue
        lines.append(line)

    raw = "".join(lines).strip()
    # Strip markdown fences if present
    if raw.startswith("```"):
        raw = "\n".join(raw.split("\n")[1:])
    if raw.endswith("```"):
        raw = "\n".join(raw.split("\n")[:-1])

    try:
        data = _json.loads(raw)
    except _json.JSONDecodeError as exc:
        error(f"Could not parse JSON: {exc}")
        return

    errors = engine.validate_bank(data)
    if errors:
        error("Invalid quiz bank:")
        for e in errors[:5]:
            click.echo(f"  - {e}")
        return

    tid = data.get("topic_id", topic_id)
    path = engine.save_bank(tid, data)
    n = len(data.get("questions", []))
    success(f"Saved {n} questions → {path}")
    info("Run: prep quiz --list  to see the new bank.")


def _handle_import(import_file: str) -> None:
    """Import a quiz bank from a local file or URL."""
    from prep_agent.core.quiz_engine import QuizEngine
    from prep_agent.utils.display import success, info, error
    import json as _json

    engine = QuizEngine()

    # Fetch content
    try:
        if import_file.startswith("http://") or import_file.startswith("https://"):
            import urllib.request
            info(f"Downloading {import_file}...")
            with urllib.request.urlopen(import_file, timeout=30) as resp:
                raw = resp.read().decode("utf-8")
        else:
            with open(import_file) as f:
                raw = f.read()
    except Exception as exc:
        error(f"Could not read file: {exc}")
        return

    try:
        data = _json.loads(raw)
    except _json.JSONDecodeError as exc:
        error(f"Invalid JSON: {exc}")
        return

    errors = engine.validate_bank(data)
    if errors:
        error("Invalid quiz bank:")
        for e in errors[:5]:
            click.echo(f"  - {e}")
        return

    topic_id = data.get("topic_id", "imported")
    path = engine.save_bank(topic_id, data)
    questions = data.get("questions", [])
    n = len(questions)
    easy = sum(1 for q in questions if q.get("difficulty") == "easy")
    med = sum(1 for q in questions if q.get("difficulty") == "medium")
    hard = sum(1 for q in questions if q.get("difficulty") == "hard")
    success(f"Imported {n} questions ({easy}E / {med}M / {hard}H) → {path}")


def _handle_review(engine, tracker, topic: str, num: int) -> None:
    """Run a spaced repetition review of previously missed questions."""
    from prep_agent.utils.display import print_quiz_result, success, info, warning

    questions = engine.get_review_questions(num=num)
    if not questions:
        info("No questions due for review. Keep quizzing to build your review queue!")
        return

    info(f"Review mode: {len(questions)} previously missed questions")
    click.echo("-" * 60)

    result = engine.run_interactive_quiz(questions)

    score = result.get("score", 0)
    total = result.get("total", 0)
    weak_areas = result.get("weak_areas", [])

    click.echo()
    print_quiz_result(score=score, total=total, topic="Review", weak_areas=weak_areas)

    engine.log_result(topic="review", score=score, total=total, weak_areas=weak_areas or None)
    tracker.log_quiz(topic="review", score=score, total=total, weak_areas=weak_areas or None)

    pct = (score / total * 100) if total > 0 else 0
    click.echo()
    if pct >= 80:
        success(f"Review complete! {score}/{total} ({pct:.0f}%) — great improvement!")
    else:
        info(f"Review score: {score}/{total} ({pct:.0f}%). These questions will come back for more practice.")


def _print_quiz_banks() -> None:
    """Print all available quiz banks with question counts and difficulty mix."""
    import json
    import os

    dirs = [
        os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "quiz_banks")),
        os.path.expanduser("~/.prep/quiz_banks"),
    ]

    rows = []
    seen = set()
    for banks_dir in dirs:
        if not os.path.isdir(banks_dir):
            continue
        for fname in sorted(os.listdir(banks_dir)):
            if not fname.endswith(".json"):
                continue
            bank_id = fname[:-5]
            if bank_id in seen:
                continue
            seen.add(bank_id)
            path = os.path.join(banks_dir, fname)
            try:
                with open(path) as f:
                    data = json.load(f)
                questions = data.get("questions", [])
                total = len(questions)
                easy = sum(1 for q in questions if q.get("difficulty") == "easy")
                medium = sum(1 for q in questions if q.get("difficulty") == "medium")
                hard = sum(1 for q in questions if q.get("difficulty") == "hard")
                rows.append((bank_id, total, easy, medium, hard))
            except Exception:
                rows.append((bank_id, 0, 0, 0, 0))

    if not rows:
        click.echo("No quiz banks found.")
        return

    click.echo()
    click.echo(click.style(
        f"  {'Bank ID':<35} {'Questions':>9}  {'Easy':>5} {'Med':>5} {'Hard':>5}",
        bold=True,
    ))
    click.echo("  " + "-" * 65)
    for bank_id, total, easy, medium, hard in rows:
        click.echo(
            f"  {bank_id:<35} {total:>9}  "
            + click.style(f"{easy:>5}", fg="green")
            + click.style(f"{medium:>6}", fg="yellow")
            + click.style(f"{hard:>6}", fg="red")
        )
    click.echo()
    click.echo(f"  {len(rows)} banks total. Use: prep quiz --topic <bank-id>")
    if any(r[2] + r[3] + r[4] > 0 for r in rows):
        click.echo("  Filter by difficulty: prep quiz --topic <id> --difficulty hard")
    click.echo("  Filter by tag:        prep quiz --topic <id> --tag <tag>")
    click.echo("  Discover tags:        prep quiz --topic <id> --list-tags")
    click.echo()


def _print_bank_tags(topic_id: str, engine) -> None:
    """Print the tags used in a given quiz bank, with question counts per tag."""
    bank = engine.load_quiz_bank(topic_id)
    if not bank:
        click.echo(f"Bank '{topic_id}' not found. Run 'prep quiz --list' to see available banks.")
        return

    tag_counts: dict[str, int] = {}
    untagged = 0
    for q in bank.get("questions", []):
        qtags = q.get("tags") or []
        if not qtags:
            untagged += 1
        for t in qtags:
            tag_counts[t] = tag_counts.get(t, 0) + 1

    total = len(bank.get("questions", []))
    click.echo()
    click.echo(click.style(f"  Tags in '{topic_id}' ({total} questions total)", bold=True))
    click.echo("  " + "-" * 50)
    if not tag_counts:
        click.echo("  (no tags in this bank)")
        click.echo()
        return
    for tag in sorted(tag_counts.keys()):
        click.echo(f"  {tag:<35} {tag_counts[tag]:>5} questions")
    if untagged:
        click.echo(f"  {'(untagged)':<35} {untagged:>5} questions")
    click.echo()
    click.echo(f"  Use: prep quiz --topic {topic_id} --tag <tag>")
    click.echo()


def _copy_to_clipboard(text: str):
    """Copy text to system clipboard. Works on macOS, Linux, and Windows."""
    import subprocess
    import platform

    system = platform.system()
    try:
        if system == "Darwin":
            proc = subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE)
            proc.communicate(text.encode("utf-8"))
        elif system == "Linux":
            proc = subprocess.Popen(
                ["xclip", "-selection", "clipboard"], stdin=subprocess.PIPE
            )
            proc.communicate(text.encode("utf-8"))
        elif system == "Windows":
            proc = subprocess.Popen(["clip"], stdin=subprocess.PIPE)
            proc.communicate(text.encode("utf-8"))
        else:
            click.echo(text)
            click.echo()
            click.echo("(Could not detect clipboard utility — prompt printed above.)")
    except FileNotFoundError:
        # Clipboard utility not available; fall back to printing
        click.echo(text)
        click.echo()
        click.echo("(Clipboard utility not found — prompt printed above.)")
