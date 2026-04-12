"""MCP Server — exposes career prep agent capabilities as MCP tools.

Any MCP-compatible client (Claude Code, Cursor, VS Code, etc.) can
discover and invoke these tools to interact with the agent system.

Start with:  prep mcp --transport stdio
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    "career-prep-agent",
    instructions=(
        "Career Prep Agent — a privacy-first CLI that turns job postings "
        "into personalized study plans.  Use these tools to check today's "
        "plan, start study sessions, take quizzes, manage notes, and "
        "review progress."
    ),
)


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def _load_state() -> tuple[dict, dict, dict | None]:
    """Load tracker state, config, and today's entry.

    Returns:
        (tracker_state, config, today_entry_or_None)
    """
    from prep_agent.core.tracker import Tracker
    from prep_agent.core.config import load_config

    cfg = load_config()
    tracker = Tracker()
    state = tracker.load()
    today_entry = tracker.get_today()
    return state, cfg, today_entry


def _build_context(state: dict, cfg: dict, today_entry: dict | None = None) -> dict:
    """Build agent context from core state."""
    from prep_agent.agents.context import build_agent_context

    return build_agent_context(state, cfg, today_entry)


# ------------------------------------------------------------------
# Tools
# ------------------------------------------------------------------


@mcp.tool()
def get_today() -> dict:
    """Get today's study plan with agent recommendations.

    Returns today's topic, morning/evening focus, progress metrics,
    and any agent-generated adjustments or recommendations.
    """
    from prep_agent.agents.orchestrator import Orchestrator

    state, cfg, today_entry = _load_state()

    if today_entry is None:
        return {"status": "no_session", "message": "No study session scheduled for today."}

    ctx = _build_context(state, cfg, today_entry)
    orchestrator = Orchestrator(cfg)
    result = orchestrator.handle_session("today", ctx)

    return {
        "today": today_entry,
        "plan": result.get("plan"),
        "review": result.get("review"),
        "agents_invoked": result.get("agents_invoked", []),
    }


@mcp.tool()
def start_study(topic: str | None = None) -> dict:
    """Start a study session with agent-adapted approach.

    The agent analyzes your progress and recommends the optimal
    teaching approach (fundamentals, analogy-based, deep-dive, or review).

    Args:
        topic: Override today's topic with a specific one.
    """
    from prep_agent.agents.orchestrator import Orchestrator

    state, cfg, today_entry = _load_state()
    ctx = _build_context(state, cfg, today_entry)

    if topic:
        ctx["topic"] = topic
    elif not ctx.get("topic") and today_entry:
        ctx["topic"] = today_entry.get("topic", "General")

    orchestrator = Orchestrator(cfg)
    result = orchestrator.handle_session("study", ctx)

    return {
        "topic": ctx.get("topic", ""),
        "session": result.get("session"),
        "plan": result.get("plan"),
        "agents_invoked": result.get("agents_invoked", []),
    }


@mcp.tool()
def take_quiz(topic: str | None = None, num: int = 5) -> dict:
    """Get quiz parameters adapted to your mastery level.

    The agent evaluates your quiz history and recommends the
    optimal difficulty and number of questions.

    Args:
        topic: Quiz topic (defaults to today's topic).
        num: Number of questions (may be adjusted by agent).
    """
    from prep_agent.agents.orchestrator import Orchestrator

    state, cfg, today_entry = _load_state()
    ctx = _build_context(state, cfg, today_entry)

    if topic:
        ctx["topic"] = topic
    elif not ctx.get("topic") and today_entry:
        ctx["topic"] = today_entry.get("topic", "General")

    orchestrator = Orchestrator(cfg)
    result = orchestrator.handle_session("quiz", ctx)

    return {
        "topic": ctx.get("topic", ""),
        "quiz": result.get("quiz"),
        "agents_invoked": result.get("agents_invoked", []),
    }


@mcp.tool()
def add_note(topic: str, content: str) -> dict:
    """Add a knowledge note to your personal study library.

    Args:
        topic: Topic name (e.g., "OWASP LLM Top 10").
        content: Note content to add.
    """
    from prep_agent.core.knowledge import KnowledgeBase

    kb = KnowledgeBase()
    path = kb.add_note(topic, content)
    return {"status": "ok", "topic": topic, "path": str(path)}


@mcp.tool()
def get_progress() -> dict:
    """Get current progress dashboard data.

    Returns days completed, percentage, tracks, quiz average,
    streak count, and agent-generated review recommendations.
    """
    from prep_agent.core.tracker import Tracker

    tracker = Tracker()
    tracker.load()
    progress = tracker.get_progress()

    # Try to add agent recommendations
    try:
        from prep_agent.agents.orchestrator import Orchestrator
        from prep_agent.core.config import load_config

        state = tracker.load()
        cfg = load_config()
        ctx = _build_context(state, cfg)
        orchestrator = Orchestrator(cfg)
        result = orchestrator.handle_session("review", ctx)
        progress["agent_review"] = result.get("review")
    except Exception:
        pass

    return progress


@mcp.tool()
def get_fitment() -> dict:
    """Get fitment analysis comparing your resume to the target role.

    Returns the overall score, strengths, gaps, and recommendations
    from the most recent fitment analysis.
    """
    import os

    from prep_agent.core.config import load_config
    from prep_agent.utils.file_ops import get_prep_dir

    cfg = load_config()
    fitment = cfg.get("fitment")
    if fitment:
        return fitment

    # Try to read saved fitment markdown
    prep_dir = get_prep_dir()
    fitment_path = os.path.join(str(prep_dir), "fitment-analysis.md")
    if os.path.exists(fitment_path):
        with open(fitment_path) as f:
            return {"format": "markdown", "content": f.read()}

    return {"error": "No fitment data. Run 'prep init' with --job-url and --resume."}


@mcp.tool()
def pivot_roles(from_role: str, top_n: int = 5) -> dict:
    """Recommend role transitions ranked by skill overlap and ramp time.

    Uses bridge_from metadata across all templates to score each target
    role based on how much of the source role's skill set transfers.

    Args:
        from_role: Current role slug (e.g. 'software_engineering',
                   'devops_sre', 'ml_engineering', 'cloud_engineering').
        top_n: Number of top pivot targets to return (default 5).

    Returns:
        List of ranked pivot targets with overlap_pct, ramp_weeks,
        strengths, gaps, recommended_start, and quick_start command.
    """
    from prep_agent.commands.pivot_cmd import _normalise_role, _score_pivot
    from prep_agent.core.templates import TemplateLoader

    normalised = _normalise_role(from_role)
    tl = TemplateLoader()
    results = []

    for meta in tl.list_templates():
        tmpl_id = meta["id"]
        if tmpl_id == "custom":
            continue
        try:
            tmpl = tl.load_template(tmpl_id)
        except Exception:
            continue
        scored = _score_pivot(normalised, tmpl, tmpl_id)
        if scored:
            results.append(scored)

    results.sort(key=lambda r: (-r["score"], r["ramp_weeks"]))
    top = results[:top_n]

    return {
        "from_role": from_role,
        "normalised_as": normalised,
        "recommendations": top,
        "quick_start": f"prep init --template {top[0]['template_id']}" if top else None,
    }


@mcp.tool()
def list_templates() -> dict:
    """List all available role templates with metadata.

    Returns each template's id, name, suggested timeline, and the
    source roles it supports for bridging (bridge_from keys).
    """
    from prep_agent.core.templates import TemplateLoader

    tl = TemplateLoader()
    items = []

    for meta in tl.list_templates():
        tmpl_id = meta["id"]
        if tmpl_id == "custom":
            continue
        try:
            tmpl = tl.load_template(tmpl_id)
            items.append({
                "id": tmpl_id,
                "name": tmpl.get("name", tmpl_id),
                "timeline": tmpl.get("suggested_timeline", ""),
                "tracks": len(tmpl.get("tracks", [])),
                "bridge_from_roles": list(tmpl.get("bridge_from", {}).keys()),
            })
        except Exception:
            items.append({"id": tmpl_id, "error": "failed to load"})

    return {"templates": items, "count": len(items)}


@mcp.tool()
def list_quiz_banks() -> dict:
    """List all available quiz banks with question counts and difficulty breakdown.

    Returns bank ids, titles, total questions, and counts per difficulty
    level so callers can pick the right bank for a study session.
    """
    import json
    import os

    banks_dir = os.path.normpath(
        os.path.join(os.path.dirname(__file__), "..", "quiz_banks")
    )
    banks = []
    if os.path.isdir(banks_dir):
        for fname in sorted(os.listdir(banks_dir)):
            if not fname.endswith(".json"):
                continue
            bank_id = fname[:-5]
            try:
                with open(os.path.join(banks_dir, fname)) as f:
                    data = json.load(f)
                questions = data.get("questions", [])
                banks.append({
                    "id": bank_id,
                    "title": data.get("title", bank_id),
                    "total": len(questions),
                    "easy": sum(1 for q in questions if q.get("difficulty") == "easy"),
                    "medium": sum(1 for q in questions if q.get("difficulty") == "medium"),
                    "hard": sum(1 for q in questions if q.get("difficulty") == "hard"),
                })
            except Exception:
                banks.append({"id": bank_id, "error": "failed to load"})

    return {"banks": banks, "count": len(banks)}
