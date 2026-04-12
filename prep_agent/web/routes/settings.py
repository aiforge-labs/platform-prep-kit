"""Settings routes — config editor and content updates."""

from __future__ import annotations

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse

router = APIRouter(prefix="/settings")


@router.get("", response_class=HTMLResponse)
async def settings_page(request: Request):
    from prep_agent.web.services import get_config

    cfg = get_config()
    templates = request.app.state.templates
    return templates.TemplateResponse(request, "pages/settings.html", {
        "config": cfg,
        "target_role": cfg.get("target", {}).get("role", ""),
        "template": cfg.get("template", ""),
        "weeks": cfg.get("timeline", {}).get("weeks", 8),
        "hours_per_day": cfg.get("timeline", {}).get("hours_per_day", 2.0),
        "ai_provider": cfg.get("ai_integration", {}).get("provider", "none"),
    })


@router.post("/config", response_class=HTMLResponse)
async def update_config(
    request: Request,
    ai_provider: str = Form("none"),
    morning_time: str = Form("08:00"),
    evening_time: str = Form("20:00"),
):
    """Update config settings."""
    from prep_agent.core.config import load_config, save_config
    from prep_agent.web.migrate import run_migration, snapshot_tracker_mtime

    cfg = load_config()
    cfg.setdefault("ai_integration", {})["provider"] = ai_provider
    cfg.setdefault("reminders", {})["morning_time"] = morning_time
    cfg.setdefault("reminders", {})["evening_time"] = evening_time
    save_config(cfg)

    # Re-sync to SQLite
    run_migration()
    snapshot_tracker_mtime()

    templates = request.app.state.templates
    return templates.TemplateResponse(request, "pages/settings.html", {
        "config": cfg,
        "target_role": cfg.get("target", {}).get("role", ""),
        "template": cfg.get("template", ""),
        "weeks": cfg.get("timeline", {}).get("weeks", 8),
        "hours_per_day": cfg.get("timeline", {}).get("hours_per_day", 2.0),
        "ai_provider": ai_provider,
        "flash": "Settings updated.",
        "flash_type": "success",
    })
