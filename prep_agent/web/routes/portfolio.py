"""Portfolio routes — projects, rubrics, hire-readiness."""

from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

router = APIRouter(prefix="/portfolio")


@router.get("", response_class=HTMLResponse)
async def portfolio_hub(request: Request):
    """Portfolio overview with projects and hire-readiness score."""
    from prep_agent.web.services import get_config

    cfg = get_config()
    template_id = cfg.get("template", "")

    projects = []
    user_projects = []
    hire_readiness = 0

    try:
        from prep_agent.agents.project import ProjectAgent
        agent = ProjectAgent(cfg)

        # Available project templates
        all_projects = agent.load_project_templates(template_id)
        if all_projects:
            projects = all_projects

        # User's started/completed projects
        user_projects = agent.list_user_projects()

        # Hire readiness
        summary = agent.get_portfolio_summary()
        if summary:
            hire_readiness = summary.get("hire_readiness_pct", 0)
    except Exception:
        pass

    templates = request.app.state.templates
    return templates.TemplateResponse(request, "pages/portfolio.html", {
        "projects": projects,
        "user_projects": user_projects,
        "hire_readiness": hire_readiness,
        "template_id": template_id,
    })
