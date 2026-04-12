"""Quiz routes — quiz hub, interactive sessions, history."""

from __future__ import annotations

import json
import uuid

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

router = APIRouter(prefix="/quiz")


@router.get("", response_class=HTMLResponse)
async def quiz_hub(request: Request):
    from prep_agent.web.services import get_quiz_history

    # List available quiz banks
    banks = _list_banks()
    history = get_quiz_history(limit=20)

    templates = request.app.state.templates
    return templates.TemplateResponse(request, "pages/quiz_hub.html", {
        "banks": banks,
        "history": history,
    })


@router.get("/start", response_class=HTMLResponse)
async def start_quiz(
    request: Request,
    topic: str = "",
    num: int = 5,
    difficulty: str = "",
):
    """Create a new quiz session and redirect to it."""
    from prep_agent.core.quiz_engine import QuizEngine
    from prep_agent.web.database import get_db

    engine = QuizEngine()
    questions = engine.get_questions(topic, num_questions=num, difficulty=difficulty or None)

    if not questions:
        templates = request.app.state.templates
        return templates.TemplateResponse(request, "pages/quiz_hub.html", {
            "banks": _list_banks(),
            "history": [],
            "flash": f"No questions found for '{topic}'.",
            "flash_type": "error",
        })

    session_id = str(uuid.uuid4())
    state = {
        "topic": topic,
        "questions": questions,
        "current_index": 0,
        "answers": [],
        "score": 0,
        "total": len(questions),
    }

    with get_db() as conn:
        conn.execute(
            "INSERT INTO sessions (id, session_type, topic, state) VALUES (?, 'quiz', ?, ?)",
            (session_id, topic, json.dumps(state, default=str)),
        )

    return RedirectResponse(url=f"/quiz/session/{session_id}", status_code=302)


@router.get("/session/{session_id}", response_class=HTMLResponse)
async def quiz_session(request: Request, session_id: str):
    """Render the current question — this is the resume point."""
    from prep_agent.web.database import get_db

    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM sessions WHERE id = ?", (session_id,)
        ).fetchone()

    if not row:
        return RedirectResponse(url="/quiz", status_code=302)

    state = json.loads(row["state"])
    idx = state["current_index"]
    questions = state["questions"]

    if idx >= len(questions):
        return RedirectResponse(url=f"/quiz/session/{session_id}/results", status_code=302)

    question = questions[idx]
    templates = request.app.state.templates
    return templates.TemplateResponse(request, "pages/quiz_session.html", {
        "session_id": session_id,
        "question": question,
        "question_num": idx + 1,
        "total_questions": len(questions),
        "topic": state["topic"],
        "score_so_far": state["score"],
    })


@router.post("/session/{session_id}/answer", response_class=HTMLResponse)
async def submit_answer(
    request: Request,
    session_id: str,
    answer: str = Form(""),
    self_score: int | None = Form(None),
):
    """Evaluate answer, store result, show feedback."""
    from prep_agent.web.database import get_db

    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM sessions WHERE id = ?", (session_id,)
        ).fetchone()

    if not row:
        return RedirectResponse(url="/quiz", status_code=302)

    state = json.loads(row["state"])
    idx = state["current_index"]
    question = state["questions"][idx]

    # Evaluate
    correct = False
    if question.get("type") == "multiple_choice":
        correct = answer.strip().upper() == question.get("answer", "").strip().upper()
    elif question.get("type") == "open":
        correct = (self_score or 0) >= 3  # 3+ out of 5 counts as correct

    if correct:
        state["score"] += 1

    state["answers"].append({
        "question_id": question.get("id", ""),
        "user_answer": answer,
        "correct": correct,
        "self_score": self_score,
    })
    state["current_index"] = idx + 1

    # Save session state
    with get_db() as conn:
        conn.execute(
            "UPDATE sessions SET state = ?, updated_at = datetime('now') WHERE id = ?",
            (json.dumps(state, default=str), session_id),
        )

    templates = request.app.state.templates
    return templates.TemplateResponse(request, "partials/quiz_feedback.html", {
        "session_id": session_id,
        "question": question,
        "correct": correct,
        "user_answer": answer,
        "has_more": state["current_index"] < len(state["questions"]),
        "score_so_far": state["score"],
        "question_num": idx + 1,
        "total_questions": len(state["questions"]),
    })


@router.get("/session/{session_id}/results", response_class=HTMLResponse)
async def quiz_results(request: Request, session_id: str):
    """Show final quiz results and log them."""
    from prep_agent.web.database import get_db
    from prep_agent.web.services import log_quiz_result

    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM sessions WHERE id = ?", (session_id,)
        ).fetchone()

    if not row:
        return RedirectResponse(url="/quiz", status_code=302)

    state = json.loads(row["state"])

    # Log result if not already completed
    if not row["completed_at"]:
        weak_areas = []
        for i, a in enumerate(state.get("answers", [])):
            if not a.get("correct") and i < len(state["questions"]):
                q = state["questions"][i]
                weak_areas.append(q.get("question", "")[:60])

        log_quiz_result(
            topic=state["topic"],
            score=state["score"],
            total=state["total"],
            weak_areas=weak_areas,
        )

        with get_db() as conn:
            conn.execute(
                "UPDATE sessions SET completed_at = datetime('now') WHERE id = ?",
                (session_id,),
            )

    pct = round(state["score"] / state["total"] * 100, 1) if state["total"] else 0
    templates = request.app.state.templates
    return templates.TemplateResponse(request, "pages/quiz_results.html", {
        "topic": state["topic"],
        "score": state["score"],
        "total": state["total"],
        "percentage": pct,
        "answers": state.get("answers", []),
        "questions": state.get("questions", []),
    })


@router.get("/history", response_class=HTMLResponse)
async def quiz_history_page(request: Request):
    from prep_agent.web.services import get_quiz_history

    history = get_quiz_history(limit=100)
    templates = request.app.state.templates
    return templates.TemplateResponse(request, "pages/quiz_history.html", {
        "history": history,
    })


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _list_banks() -> list[dict]:
    """List available quiz banks with metadata."""
    import os
    from prep_agent.core.quiz_engine import QuizEngine

    engine = QuizEngine()
    banks = []

    # Search package quiz_banks directory
    pkg_dir = os.path.normpath(
        os.path.join(os.path.dirname(__file__), "..", "..", "..", "quiz_banks")
    )
    for search_dir in [pkg_dir, os.path.join(engine.prep_dir, "quiz_banks")]:
        if not os.path.isdir(search_dir):
            continue
        for f in sorted(os.listdir(search_dir)):
            if not f.endswith(".json"):
                continue
            topic_id = f[:-5]
            if any(b["topic_id"] == topic_id for b in banks):
                continue
            bank = engine.load_quiz_bank(topic_id)
            if bank:
                banks.append({
                    "topic_id": topic_id,
                    "title": bank.get("title", topic_id),
                    "total": len(bank.get("questions", [])),
                })
    return banks
