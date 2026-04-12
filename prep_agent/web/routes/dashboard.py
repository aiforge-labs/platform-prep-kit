"""Dashboard routes — overview metrics and progress."""

from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    from prep_agent.utils.file_ops import get_prep_dir
    from fastapi.responses import RedirectResponse

    if not (get_prep_dir() / "config.yml").exists():
        return RedirectResponse(url="/onboarding", status_code=302)

    from prep_agent.web.services import get_progress

    data = get_progress()
    templates = request.app.state.templates
    return templates.TemplateResponse(request, "pages/dashboard.html", {
        "completed_days": data["completed_days"],
        "total_days": data["total_days"],
        "progress_pct": data["progress_pct"],
        "streak": data["streak"],
        "study_hours": data["study_hours"],
        "avg_score": data["avg_score"],
        "quizzes_taken": data["quizzes_taken"],
        "tracks": data["tracks"],
        "track_progress": data["track_progress"],
        "days": data["days"],
        "quiz_history": data["quiz_history"],
    })


@router.get("/api/progress")
async def progress_api():
    from prep_agent.web.services import get_progress
    return get_progress()
