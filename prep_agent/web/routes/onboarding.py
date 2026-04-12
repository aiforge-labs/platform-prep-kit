"""Onboarding wizard routes — web-based init/intake flow.

Flow:
  Step 1: Profile (name, current role)
  Step 2: Template selection
  Step 3: Job URL + Resume upload (optional)
  Step 4: Timeline configuration
  Step 5: Confirm and create
"""

from __future__ import annotations

import json
import os
import re
import uuid
from pathlib import Path

from fastapi import APIRouter, Form, Request, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse

router = APIRouter(prefix="/onboarding")

# File upload constraints
_ALLOWED_EXTENSIONS = {".pdf", ".docx", ".doc", ".txt", ".md"}
_MAX_UPLOAD_BYTES = 10 * 1024 * 1024  # 10 MB


@router.get("", response_class=HTMLResponse)
async def onboarding_start(request: Request):
    from prep_agent.utils.file_ops import get_prep_dir

    if (get_prep_dir() / "config.yml").exists():
        return RedirectResponse(url="/", status_code=302)

    templates = request.app.state.templates
    return templates.TemplateResponse(request, "pages/onboarding/start.html", {})


# ------------------------------------------------------------------
# Step 1 -> Step 2: Profile done, show template selection
# ------------------------------------------------------------------

@router.post("/step/template", response_class=HTMLResponse)
async def step_template(
    request: Request,
    name: str = Form(""),
    current_role: str = Form(""),
):
    from prep_agent.core.templates import TemplateLoader

    tl = TemplateLoader()
    available = tl.list_templates()

    session_id = str(uuid.uuid4())
    _save_session(session_id, {
        "profile": {"name": name, "current_role": current_role},
    })

    templates = request.app.state.templates
    return templates.TemplateResponse(request, "pages/onboarding/step_template.html", {
        "templates": available,
        "session_id": session_id,
    })


# ------------------------------------------------------------------
# Step 2 -> Step 3: Template selected, show job URL + resume upload
# ------------------------------------------------------------------

@router.post("/step/job-resume", response_class=HTMLResponse)
async def step_job_resume(
    request: Request,
    session_id: str = Form(""),
    template_id: str = Form(""),
):
    state = _load_session(session_id)
    state["template_id"] = template_id

    # Load template name
    if template_id:
        try:
            from prep_agent.core.templates import TemplateLoader
            tl = TemplateLoader()
            tmpl = tl.load_template(template_id)
            state["template_name"] = tmpl.get("name", template_id)
        except Exception:
            state["template_name"] = template_id

    _save_session(session_id, state)

    templates = request.app.state.templates
    return templates.TemplateResponse(request, "pages/onboarding/step_job_resume.html", {
        "session_id": session_id,
        "template_name": state.get("template_name", template_id),
    })


# ------------------------------------------------------------------
# Step 3 -> Step 4 (or fitment): Process job URL + resume, show timeline
# ------------------------------------------------------------------

@router.post("/step/timeline", response_class=HTMLResponse)
async def step_timeline(
    request: Request,
    session_id: str = Form(""),
    job_url: str = Form(""),
    resume: UploadFile | None = File(None),
):
    state = _load_session(session_id)
    template_id = state.get("template_id", "")

    # --- Parse job URL ---
    job_data = None
    if job_url and job_url.strip():
        try:
            from prep_agent.integrations.job_fetcher import JobFetcher
            fetcher = JobFetcher()
            job_data = fetcher.fetch_with_fallback(job_url.strip())
            if job_data:
                state["job"] = job_data
                state["job_url"] = job_url.strip()
        except Exception:
            pass

    # --- Parse resume upload ---
    resume_data = None
    if resume and resume.filename:
        ext = Path(resume.filename).suffix.lower()
        if ext not in _ALLOWED_EXTENSIONS:
            state["resume_error"] = f"Unsupported file type: {ext}. Allowed: {', '.join(_ALLOWED_EXTENSIONS)}"
        else:
            contents = await resume.read()
            if len(contents) > _MAX_UPLOAD_BYTES:
                state["resume_error"] = "File too large (max 10MB)"
            else:
                # Save to temp location, parse, then delete
                from prep_agent.utils.file_ops import get_prep_dir
                uploads_dir = get_prep_dir() / "uploads"
                uploads_dir.mkdir(exist_ok=True)

                # Sanitize filename
                safe_name = Path(resume.filename).name
                temp_path = uploads_dir / f"{uuid.uuid4().hex}_{safe_name}"
                try:
                    temp_path.write_bytes(contents)

                    from prep_agent.integrations.resume_parser import ResumeParser
                    parser = ResumeParser()
                    resume_data = parser.parse(str(temp_path))
                    if resume_data:
                        state["resume"] = resume_data
                except Exception:
                    pass
                finally:
                    # Always delete the uploaded file
                    temp_path.unlink(missing_ok=True)

    # --- Run fitment analysis if both job + resume available ---
    fitment = None
    if job_data and resume_data:
        try:
            from prep_agent.core.analyzer import FitmentAnalyzer
            analyzer = FitmentAnalyzer()
            fitment = analyzer.analyze(job_data, resume_data)
            if fitment:
                state["fitment"] = fitment
        except Exception:
            pass

    _save_session(session_id, state)

    # If fitment was generated, show it before timeline
    if fitment:
        templates = request.app.state.templates
        return templates.TemplateResponse(request, "pages/onboarding/step_fitment.html", {
            "session_id": session_id,
            "fitment": fitment,
            "job_title": job_data.get("title", "Unknown Role") if job_data else "",
        })

    # Otherwise skip to timeline
    return _render_timeline_step(request, session_id, state)


# ------------------------------------------------------------------
# Step 3b -> Step 4: Fitment shown, now show timeline
# ------------------------------------------------------------------

@router.post("/step/timeline-from-fitment", response_class=HTMLResponse)
async def step_timeline_from_fitment(
    request: Request,
    session_id: str = Form(""),
):
    state = _load_session(session_id)
    return _render_timeline_step(request, session_id, state)


def _render_timeline_step(request: Request, session_id: str, state: dict):
    """Render the timeline configuration step."""
    template_id = state.get("template_id", "")
    suggested_weeks = 8

    if template_id:
        try:
            from prep_agent.core.templates import TemplateLoader
            tl = TemplateLoader()
            tmpl = tl.load_template(template_id)
            raw = tmpl.get("suggested_timeline", "")
            m = re.search(r"(\d+)", raw)
            if m:
                suggested_weeks = int(m.group(1))
        except Exception:
            pass

    templates = request.app.state.templates
    return templates.TemplateResponse(request, "pages/onboarding/step_timeline.html", {
        "session_id": session_id,
        "suggested_weeks": suggested_weeks,
        "template_name": state.get("template_name", template_id),
        "has_job": bool(state.get("job")),
        "has_resume": bool(state.get("resume")),
        "has_fitment": bool(state.get("fitment")),
    })


# ------------------------------------------------------------------
# Step 4 -> Step 5: Timeline done, show confirmation
# ------------------------------------------------------------------

@router.post("/step/confirm", response_class=HTMLResponse)
async def step_confirm(
    request: Request,
    session_id: str = Form(""),
    weeks: int = Form(8),
    hours_per_day: float = Form(2.0),
    study_days: str = Form("mon,tue,wed,thu,fri"),
):
    state = _load_session(session_id)
    state["timeline"] = {
        "weeks": weeks,
        "hours_per_day": hours_per_day,
        "study_days": [d.strip() for d in study_days.split(",") if d.strip()],
    }
    _save_session(session_id, state)

    templates = request.app.state.templates
    return templates.TemplateResponse(request, "pages/onboarding/step_confirm.html", {
        "session_id": session_id,
        "state": state,
    })


# ------------------------------------------------------------------
# Step 5: Create workspace
# ------------------------------------------------------------------

@router.post("/create", response_class=HTMLResponse)
async def create_workspace(request: Request, session_id: str = Form("")):
    """Execute the full init sequence and redirect to dashboard."""
    from datetime import date, timedelta
    from prep_agent.core.config import create_default_config, save_config, validate_config
    from prep_agent.core.planner import StudyPlanner
    from prep_agent.core.tracker import Tracker
    from prep_agent.utils.file_ops import ensure_prep_dir, get_prep_dir

    state = _load_session(session_id)
    profile = state.get("profile", {})
    timeline = state.get("timeline", {})
    template_id = state.get("template_id", "")

    ensure_prep_dir()

    # Create config
    cfg = create_default_config(
        target_role=state.get("template_name", profile.get("current_role", "")),
        company="",
        timeline_weeks=timeline.get("weeks", 8),
        hours_per_week=int(timeline.get("hours_per_day", 2) * 5),
    )

    cfg["timeline"]["hours_per_day"] = timeline.get("hours_per_day", 2.0)
    cfg["timeline"].pop("hours_per_week", None)
    cfg["timeline"]["study_days"] = timeline.get("study_days", ["mon", "tue", "wed", "thu", "fri"])
    cfg["timeline"]["end_date"] = (
        date.today() + timedelta(weeks=timeline.get("weeks", 8))
    ).isoformat()

    if profile.get("name"):
        cfg.setdefault("profile", {})["name"] = profile["name"]
    if profile.get("current_role"):
        cfg.setdefault("profile", {})["current_role"] = profile["current_role"]

    # Store job data if provided
    if state.get("job"):
        cfg["job"] = state["job"]
    if state.get("job_url"):
        cfg.setdefault("target", {})["job_url"] = state["job_url"]

    # Store resume data if provided
    if state.get("resume"):
        cfg["resume"] = state["resume"]

    # Store fitment if computed
    if state.get("fitment"):
        cfg["fitment"] = state["fitment"]
        # Save fitment report
        try:
            from prep_agent.core.analyzer import FitmentAnalyzer
            analyzer = FitmentAnalyzer()
            report_md = analyzer.generate_report_md(state["fitment"])
            prep_dir = get_prep_dir()
            (prep_dir / "fitment-analysis.md").write_text(report_md, encoding="utf-8")
        except Exception:
            pass

    # Apply template
    if template_id:
        try:
            from prep_agent.core.templates import TemplateLoader
            tl = TemplateLoader()
            tmpl = tl.load_template(template_id)

            cfg.setdefault("target", {})["role"] = tmpl.get("name", template_id)

            gaps = []
            for track in tmpl.get("tracks", []):
                topic_names = [t.get("name", t.get("id", "")) for t in track.get("topics", [])]
                total_hours = sum(t.get("estimated_hours", 4) for t in track.get("topics", []))
                priorities = [t.get("priority", "medium") for t in track.get("topics", [])]
                if "high" in priorities or "critical" in priorities:
                    priority = "high"
                elif all(p == "low" for p in priorities):
                    priority = "low"
                else:
                    priority = "moderate"

                track_name = track.get("name", track.get("id", ""))
                gaps.append({
                    "id": track.get("id", ""),
                    "name": track_name,
                    "topic": track_name,
                    "topics": topic_names,
                    "estimated_hours": total_hours,
                    "priority": priority,
                })
            cfg["gaps"] = gaps
            cfg["template"] = template_id
        except Exception:
            pass

    # Generate plan
    planner = StudyPlanner()
    plan = planner.generate(cfg)
    plan_md = planner.generate_plan_md(plan, cfg)

    prep_dir = get_prep_dir()
    (prep_dir / "study-plan.md").write_text(plan_md, encoding="utf-8")

    # Initialize tracker
    tracker = Tracker()
    tracker.initialize(plan, cfg)

    # Validate and save config
    validate_config(cfg)
    save_config(cfg)

    # Migrate to SQLite
    from prep_agent.web.database import ensure_db
    from prep_agent.web.migrate import run_migration, snapshot_tracker_mtime

    ensure_db()
    run_migration()
    snapshot_tracker_mtime()

    # Clean up session
    _delete_session(session_id)

    return RedirectResponse(url="/", status_code=302)


# ---------------------------------------------------------------------------
# Session helpers (SQLite-backed)
# ---------------------------------------------------------------------------


def _save_session(session_id: str, state: dict) -> None:
    from prep_agent.web.database import get_db, init_schema

    with get_db() as conn:
        init_schema(conn)  # ensure tables exist for fresh workspaces
        existing = conn.execute("SELECT id FROM sessions WHERE id = ?", (session_id,)).fetchone()
        if existing:
            conn.execute(
                "UPDATE sessions SET state = ?, updated_at = datetime('now') WHERE id = ?",
                (json.dumps(state, default=str), session_id),
            )
        else:
            conn.execute(
                "INSERT INTO sessions (id, session_type, state) VALUES (?, 'onboarding', ?)",
                (session_id, json.dumps(state, default=str)),
            )


def _load_session(session_id: str) -> dict:
    from prep_agent.web.database import get_db, init_schema

    with get_db() as conn:
        init_schema(conn)
        row = conn.execute("SELECT state FROM sessions WHERE id = ?", (session_id,)).fetchone()
    if row:
        return json.loads(row["state"])
    return {}


def _delete_session(session_id: str) -> None:
    from prep_agent.web.database import get_db

    with get_db() as conn:
        conn.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
