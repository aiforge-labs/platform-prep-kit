"""Study plan routes — timeline view and day details."""

from __future__ import annotations

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse

router = APIRouter(prefix="/study")


@router.get("", response_class=HTMLResponse)
async def study_timeline(request: Request, track: str | None = None):
    from prep_agent.web.services import get_study_days, get_tracks

    days = get_study_days(track_id=track)
    tracks = get_tracks()

    # Compute "Day X of Y" for repeated topics
    topic_counts: dict[str, int] = {}
    for d in days:
        topic_counts[d["topic"]] = topic_counts.get(d["topic"], 0) + 1

    topic_seen: dict[str, int] = {}
    for d in days:
        topic = d["topic"]
        topic_seen[topic] = topic_seen.get(topic, 0) + 1
        total_for_topic = topic_counts[topic]
        if total_for_topic > 1:
            d["topic_day"] = topic_seen[topic]
            d["topic_total"] = total_for_topic
            # Add focus hint for multi-day topics
            if topic_seen[topic] == 1:
                d["focus_hint"] = "Theory & concepts"
            elif topic_seen[topic] == total_for_topic:
                d["focus_hint"] = "Review & practice"
            else:
                d["focus_hint"] = "Deep dive & exercises"

    # Group by week
    weeks: dict[int, list] = {}
    for d in days:
        w = d.get("week", 1)
        weeks.setdefault(w, []).append(d)

    templates = request.app.state.templates
    return templates.TemplateResponse(request, "pages/study_timeline.html", {
        "weeks": weeks,
        "tracks": tracks,
        "selected_track": track,
        "total_days": len(days),
        "done_days": sum(1 for d in days if d["status"] == "done"),
    })


@router.get("/day/{day_num}", response_class=HTMLResponse)
async def day_detail(request: Request, day_num: int):
    from prep_agent.web.services import get_study_days

    days = get_study_days()
    entry = None
    prev_entry = None
    next_entry = None
    for i, d in enumerate(days):
        if d["day_num"] == day_num:
            entry = d
            if i > 0:
                prev_entry = days[i - 1]
            if i < len(days) - 1:
                next_entry = days[i + 1]
            break

    # Find matching knowledge pack and quiz bank
    knowledge_slug = None
    knowledge_content = None
    quiz_bank_id = None
    if entry:
        knowledge_slug, knowledge_content = _find_knowledge_pack(
            entry.get("topic", ""), entry.get("track_id", "")
        )
        quiz_bank_id = _find_quiz_bank(
            entry.get("topic", ""), entry.get("track_id", "")
        )

    # Render knowledge content to HTML
    knowledge_html = None
    if knowledge_content:
        try:
            import markdown
            knowledge_html = markdown.markdown(
                knowledge_content,
                extensions=["toc", "tables", "fenced_code"],
            )
        except ImportError:
            knowledge_html = f"<pre>{knowledge_content[:3000]}</pre>"

    templates = request.app.state.templates
    return templates.TemplateResponse(request, "pages/day_detail.html", {
        "entry": entry,
        "prev_entry": prev_entry,
        "next_entry": next_entry,
        "knowledge_slug": knowledge_slug,
        "knowledge_html": knowledge_html,
        "quiz_bank_id": quiz_bank_id,
    })


@router.post("/day/{day_num}/done", response_class=HTMLResponse)
async def mark_day_done(
    request: Request,
    day_num: int,
    notes: str = Form(""),
    score: int | None = Form(None),
    minutes: int | None = Form(None),
):
    from prep_agent.web.services import mark_day_done as do_mark

    do_mark(day_num, notes=notes, score=score, minutes=minutes)

    # Return the updated row partial
    from prep_agent.web.services import get_study_days
    days = get_study_days()
    entry = next((d for d in days if d["day_num"] == day_num), None)
    templates = request.app.state.templates
    return templates.TemplateResponse(request, "partials/day_row.html", {
        "d": entry,
        "flash": "Day marked complete!",
    })


@router.post("/day/{day_num}/notes", response_class=HTMLResponse)
async def save_notes(request: Request, day_num: int, notes: str = Form("")):
    from prep_agent.web.services import save_day_notes

    save_day_notes(day_num, notes)
    return HTMLResponse('<span class="flash flash-success">Notes saved</span>')


# ---------------------------------------------------------------------------
# Helpers: find matching knowledge packs and quiz banks
# ---------------------------------------------------------------------------


def _find_knowledge_pack(topic: str, track_id: str) -> tuple[str | None, str | None]:
    """Find the best-matching knowledge pack for a topic/track.

    Search strategy:
    1. Exact topic slug match
    2. Track ID slug match
    3. Fuzzy: search all packs for topic keywords
    """
    import os
    from prep_agent.core.knowledge import KnowledgeBase

    kb = KnowledgeBase()

    # 1. Try exact topic slug
    content = kb.get_topic(topic)
    if content:
        return kb._topic_to_slug(topic), content

    # 2. Try track_id as slug
    content = kb.get_topic(track_id)
    if content:
        return kb._topic_to_slug(track_id), content

    # 3. Fuzzy search: find pack whose content best matches the topic
    if not os.path.isdir(kb._packs_dir):
        return None, None

    topic_lower = topic.lower()
    topic_words = set(topic_lower.replace(",", " ").replace("&", " ").split())
    # Remove common stop words
    topic_words -= {"and", "the", "of", "for", "in", "a", "an", "to", "with"}

    best_slug = None
    best_content = None
    best_score = 0

    for f in os.listdir(kb._packs_dir):
        if not f.endswith(".md"):
            continue
        slug = f[:-3]
        path = os.path.join(kb._packs_dir, f)
        try:
            with open(path) as fh:
                pack_content = fh.read()
        except OSError:
            continue

        # Score: how many topic words appear in the pack content
        pack_lower = pack_content.lower()
        score = sum(1 for w in topic_words if w in pack_lower and len(w) > 2)

        if score > best_score:
            best_score = score
            best_slug = slug
            best_content = pack_content

    if best_score >= 1:  # at least 1 meaningful keyword match
        return best_slug, best_content

    return None, None


def _find_quiz_bank(topic: str, track_id: str) -> str | None:
    """Find a matching quiz bank ID for a topic/track."""
    import os
    from prep_agent.core.quiz_engine import QuizEngine

    engine = QuizEngine()
    topic_slug = topic.lower().replace(" ", "-").replace(",", "").replace("&", "")
    track_slug = track_id.lower().replace(" ", "-")

    # Check package quiz banks
    pkg_dir = os.path.normpath(
        os.path.join(os.path.dirname(__file__), "..", "..", "..", "quiz_banks")
    )
    if not os.path.isdir(pkg_dir):
        return None

    available = [f[:-5] for f in os.listdir(pkg_dir) if f.endswith(".json")]

    # Try direct matches
    for bank_id in available:
        if bank_id in topic_slug or topic_slug in bank_id:
            return bank_id
        if bank_id in track_slug or track_slug in bank_id:
            return bank_id

    # Try keyword overlap (topic words)
    topic_words = set(topic_slug.split("-")) - {"and", "the", "of", "for", "a", "an"}
    for bank_id in available:
        bank_words = set(bank_id.split("-"))
        overlap = topic_words & bank_words
        if len(overlap) >= 2:
            return bank_id

    # Try track-based keyword overlap
    track_words = set(track_slug.split("-")) - {"and", "the", "of", "for", "a", "an"}
    for bank_id in available:
        bank_words = set(bank_id.split("-"))
        overlap = track_words & bank_words
        if len(overlap) >= 1 and len(overlap) >= len(bank_words) * 0.5:
            return bank_id

    return None
