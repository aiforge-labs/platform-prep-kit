"""Knowledge pack routes — browsing and section-level progress."""

from __future__ import annotations

import json
import re

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

router = APIRouter(prefix="/knowledge")


@router.get("", response_class=HTMLResponse)
async def knowledge_hub(request: Request):
    """List all knowledge packs with user progress."""
    packs = _list_packs_with_progress()
    templates = request.app.state.templates
    return templates.TemplateResponse(request, "pages/knowledge_hub.html", {
        "packs": packs,
    })


@router.get("/{slug}", response_class=HTMLResponse)
async def knowledge_pack(request: Request, slug: str):
    """Render a knowledge pack as HTML with section checkboxes."""
    from prep_agent.core.knowledge import KnowledgeBase

    kb = KnowledgeBase()
    content = kb.get_topic(slug)

    if not content:
        # Try with original slug (knowledge packs use file slug, not topic name)
        import os
        packs_dir = kb._packs_dir
        pack_path = os.path.join(packs_dir, f"{slug}.md")
        if os.path.isfile(pack_path):
            with open(pack_path) as f:
                content = f.read()

    if not content:
        return HTMLResponse("<h2>Knowledge pack not found</h2>", status_code=404)

    # Parse sections and render
    sections = _parse_sections(content)
    html_content = _render_markdown(content)
    completed = _get_completed_sections(slug)

    # Extract title from first heading
    title = slug.replace("-", " ").title()
    first_line = content.split("\n", 1)[0]
    if first_line.startswith("#"):
        title = first_line.lstrip("# ").strip()

    templates = request.app.state.templates
    return templates.TemplateResponse(request, "pages/knowledge_pack.html", {
        "slug": slug,
        "title": title,
        "html_content": html_content,
        "sections": sections,
        "completed": completed,
        "total_sections": len(sections),
        "done_sections": sum(1 for s in sections if s["id"] in completed),
    })


@router.post("/{slug}/section/{section_id}/complete", response_class=HTMLResponse)
async def toggle_section(request: Request, slug: str, section_id: str):
    """Toggle a section's completion status."""
    from prep_agent.web.database import get_db

    with get_db() as conn:
        existing = conn.execute(
            "SELECT completed FROM knowledge_progress WHERE knowledge_pack = ? AND section_id = ?",
            (slug, section_id),
        ).fetchone()

        if existing:
            new_val = 0 if existing["completed"] else 1
            conn.execute(
                """UPDATE knowledge_progress
                   SET completed = ?, completed_at = CASE WHEN ? = 1 THEN datetime('now') ELSE NULL END
                   WHERE knowledge_pack = ? AND section_id = ?""",
                (new_val, new_val, slug, section_id),
            )
        else:
            conn.execute(
                """INSERT INTO knowledge_progress (knowledge_pack, section_id, section_title, completed, completed_at)
                   VALUES (?, ?, ?, 1, datetime('now'))""",
                (slug, section_id, section_id.replace("-", " ").title()),
            )

    checked = not existing or not existing["completed"] if existing else True
    icon = "checked" if checked else "unchecked"
    return HTMLResponse(
        f'<button hx-post="/knowledge/{slug}/section/{section_id}/complete" '
        f'hx-swap="outerHTML" class="section-check {"done" if checked else ""}">'
        f'{"[x]" if checked else "[ ]"}</button>'
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _list_packs_with_progress() -> list[dict]:
    """List all knowledge packs with section counts and user progress."""
    import os
    from prep_agent.core.knowledge import KnowledgeBase
    from prep_agent.web.database import get_db

    kb = KnowledgeBase()
    packs = []

    # Search bundled packs
    if os.path.isdir(kb._packs_dir):
        for f in sorted(os.listdir(kb._packs_dir)):
            if not f.endswith(".md"):
                continue
            slug = f[:-3]
            path = os.path.join(kb._packs_dir, f)
            with open(path) as fh:
                content = fh.read()
            first_line = content.split("\n", 1)[0]
            title = first_line.lstrip("# ").strip() if first_line.startswith("#") else slug

            sections = _parse_sections(content)
            completed = _get_completed_sections(slug)

            packs.append({
                "slug": slug,
                "title": title,
                "sections": len(sections),
                "completed": sum(1 for s in sections if s["id"] in completed),
            })

    return packs


def _parse_sections(content: str) -> list[dict]:
    """Extract ## headings as sections."""
    sections = []
    for match in re.finditer(r"^##\s+(.+)$", content, re.MULTILINE):
        title = match.group(1).strip()
        sid = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
        sections.append({"id": sid, "title": title})
    return sections


def _get_completed_sections(slug: str) -> set[str]:
    """Return set of completed section IDs for a pack."""
    from prep_agent.web.database import get_db

    with get_db() as conn:
        rows = conn.execute(
            "SELECT section_id FROM knowledge_progress WHERE knowledge_pack = ? AND completed = 1",
            (slug,),
        ).fetchall()
    return {r["section_id"] for r in rows}


def _render_markdown(content: str) -> str:
    """Convert markdown content to HTML."""
    try:
        import markdown
        return markdown.markdown(
            content,
            extensions=["toc", "tables", "fenced_code"],
        )
    except ImportError:
        # Fallback: basic escaping
        import html
        return f"<pre>{html.escape(content)}</pre>"
