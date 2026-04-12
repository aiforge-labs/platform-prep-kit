"""FastAPI application factory for the Career Prep Agent web UI."""

from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from prep_agent.utils.file_ops import get_prep_dir

_WEB_DIR = Path(__file__).parent
_STATIC_DIR = _WEB_DIR / "static"
_TEMPLATES_DIR = _WEB_DIR / "templates"


@asynccontextmanager
async def _lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Ensure the database exists and migrate on startup."""
    from prep_agent.web.database import ensure_db
    from prep_agent.web.migrate import needs_migration, run_migration, snapshot_tracker_mtime

    ensure_db()
    prep_dir = get_prep_dir()
    if (prep_dir / "tracker.md").exists() and needs_migration():
        run_migration()
    snapshot_tracker_mtime()
    yield


def create_app() -> FastAPI:
    """Build and return the configured FastAPI application."""

    app = FastAPI(
        title="Career Prep Agent",
        version="0.1.0",
        docs_url=None,
        redoc_url=None,
        lifespan=_lifespan,
    )

    # Static files
    app.mount("/static", StaticFiles(directory=str(_STATIC_DIR)), name="static")

    # Jinja2 templates
    templates = Jinja2Templates(directory=str(_TEMPLATES_DIR))
    app.state.templates = templates

    # CSRF middleware
    from prep_agent.web.csrf import CSRFMiddleware
    app.add_middleware(CSRFMiddleware)

    # Security headers
    @app.middleware("http")
    async def security_headers(request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; script-src 'self'; "
            "style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'"
        )
        return response

    # CLI sync middleware
    @app.middleware("http")
    async def cli_sync(request: Request, call_next):
        from prep_agent.web.migrate import check_cli_sync
        check_cli_sync()
        return await call_next(request)

    # Register routers
    from prep_agent.web.routes.dashboard import router as dashboard_router
    from prep_agent.web.routes.today import router as today_router
    from prep_agent.web.routes.study import router as study_router
    from prep_agent.web.routes.quiz import router as quiz_router
    from prep_agent.web.routes.knowledge import router as knowledge_router
    from prep_agent.web.routes.onboarding import router as onboarding_router
    from prep_agent.web.routes.settings import router as settings_router
    from prep_agent.web.routes.portfolio import router as portfolio_router

    app.include_router(dashboard_router)
    app.include_router(today_router)
    app.include_router(study_router)
    app.include_router(quiz_router)
    app.include_router(knowledge_router)
    app.include_router(onboarding_router)
    app.include_router(settings_router)
    app.include_router(portfolio_router)

    # Health check
    @app.get("/health")
    async def health():
        return {"status": "ok", "version": "0.1.0"}

    return app
