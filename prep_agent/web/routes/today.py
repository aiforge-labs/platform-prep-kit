"""Today routes — current day's study card and mark-done action."""

from __future__ import annotations

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse

router = APIRouter(prefix="/today")


@router.get("", response_class=HTMLResponse)
async def today_page(request: Request):
    from prep_agent.web.services import get_today, get_progress
    from prep_agent.web.routes.study import _find_knowledge_pack

    entry = get_today()
    progress = get_progress()
    knowledge_slug = None
    if entry:
        knowledge_slug, _ = _find_knowledge_pack(
            entry.get("topic", ""), entry.get("track_id", "")
        )
    templates = request.app.state.templates
    return templates.TemplateResponse(request, "pages/today.html", {
        "entry": entry,
        "progress": progress,
        "next_study_day": progress.get("next_study_day"),
        "knowledge_slug": knowledge_slug,
    })


@router.post("/done", response_class=HTMLResponse)
async def mark_today_done(
    request: Request,
    notes: str = Form(""),
    score: int | None = Form(None),
    minutes: int | None = Form(None),
):
    from prep_agent.web.services import get_today, mark_day_done

    entry = get_today()
    if entry:
        mark_day_done(entry["day_num"], notes=notes, score=score, minutes=minutes)

    # Return updated today card via HTMX
    entry = get_today()
    from prep_agent.web.services import get_progress
    from prep_agent.web.routes.study import _find_knowledge_pack
    progress = get_progress()
    knowledge_slug = None
    if entry:
        knowledge_slug, _ = _find_knowledge_pack(
            entry.get("topic", ""), entry.get("track_id", "")
        )
    templates = request.app.state.templates
    return templates.TemplateResponse(request, "pages/today.html", {
        "entry": entry,
        "progress": progress,
        "next_study_day": progress.get("next_study_day"),
        "knowledge_slug": knowledge_slug,
        "flash": "Session marked complete!",
        "flash_type": "success",
    })
