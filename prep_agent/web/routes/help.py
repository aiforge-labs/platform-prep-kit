"""Help & Support routes — in-app guide to running and contributing."""

from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

router = APIRouter(prefix="/help")


@router.get("", response_class=HTMLResponse)
async def help_page(request: Request):
    templates = request.app.state.templates
    return templates.TemplateResponse(request, "pages/help.html", {})
