"""
Streamlit-based local web dashboard for Career Prep Agent.

Launch via: prep dashboard
Runs on localhost:8501 — fully local, no data leaves your machine.
"""

import os
import sys
from datetime import date

import streamlit as st

# Ensure the package is importable when run via `streamlit run`
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from prep_agent.core.tracker import Tracker
from prep_agent.core.quiz_engine import QuizEngine

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Career Prep Agent",
    page_icon="📚",
    layout="wide",
)

# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

PREP_DIR = os.path.expanduser("~/.prep")


def _workspace_exists() -> bool:
    return os.path.isdir(PREP_DIR) and os.path.isfile(
        os.path.join(PREP_DIR, "tracker.md")
    )


@st.cache_data(ttl=5)
def load_progress():
    tracker = Tracker()
    return tracker.get_progress()


@st.cache_data(ttl=5)
def load_state():
    tracker = Tracker()
    return tracker.load()


@st.cache_data(ttl=5)
def load_today():
    tracker = Tracker()
    return tracker.get_today()


@st.cache_data(ttl=5)
def load_quiz_history():
    engine = QuizEngine()
    return engine.get_history(limit=100)


@st.cache_data(ttl=5)
def load_review_topics():
    engine = QuizEngine()
    return engine.suggest_review_topics()


# ---------------------------------------------------------------------------
# Sidebar navigation
# ---------------------------------------------------------------------------

if not _workspace_exists():
    st.error("No workspace found. Run `prep init` first.")
    st.stop()

page = st.sidebar.radio(
    "Navigation",
    ["Overview", "Quiz Analytics", "Today's Plan", "Study Timeline", "Portfolio"],
    index=0,
)

st.sidebar.divider()
st.sidebar.caption("Career Prep Agent v0.1.0")
st.sidebar.caption("All data stays local in ~/.prep/")

# ---------------------------------------------------------------------------
# Page: Overview
# ---------------------------------------------------------------------------

if page == "Overview":
    st.title("Preparation Overview")

    progress = load_progress()

    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Days Completed", f"{progress['completed_days']} / {progress['total_days']}")
    col2.metric("Current Streak", f"{progress['streak']} days")
    study_h = progress.get("study_hours")
    col3.metric("Study Hours", f"{study_h}h" if study_h else "—")
    avg = progress.get("avg_score", 0)
    col4.metric("Avg Quiz Score", f"{avg:.0f}%" if progress.get("quizzes_taken") else "—")

    # Progress bar
    pct = progress.get("pct", 0)
    st.progress(min(pct / 100, 1.0), text=f"Overall progress: {pct:.0f}%")

    # Estimated completion
    est = progress.get("est_end_date")
    if est:
        st.info(f"Estimated completion: **{est}**")

    # Track breakdown chart
    tracks = progress.get("tracks", [])
    if tracks:
        st.subheader("Track Breakdown")
        import pandas as pd

        df = pd.DataFrame(tracks)
        df["remaining"] = df["total"] - df["done"]
        chart_df = df.set_index("name")[["done", "remaining"]]
        st.bar_chart(chart_df, horizontal=True, color=["#4CAF50", "#E0E0E0"])

    # Topics & weeks
    st.divider()
    c1, c2, c3 = st.columns(3)
    c1.metric("Topics Covered", f"{progress.get('topics_done', 0)} / {progress.get('topics_total', '—')}")
    c2.metric("Current Week", f"{progress.get('current_week', '—')} / {progress.get('total_weeks', '—')}")
    c3.metric("Quizzes Taken", str(progress.get("quizzes_taken", 0)))

# ---------------------------------------------------------------------------
# Page: Quiz Analytics
# ---------------------------------------------------------------------------

elif page == "Quiz Analytics":
    st.title("Quiz Analytics")

    history = load_quiz_history()

    if not history:
        st.info("No quiz history yet. Run `prep quiz --topic <topic>` to get started.")
        st.stop()

    import pandas as pd

    df = pd.DataFrame(history)

    # Score trend
    st.subheader("Score Trend")
    if "timestamp" in df.columns and "percentage" in df.columns:
        trend = df[["timestamp", "percentage"]].copy()
        trend["timestamp"] = pd.to_datetime(trend["timestamp"])
        trend = trend.set_index("timestamp").sort_index()
        st.line_chart(trend, y="percentage", color="#2196F3")

    # Topic performance table
    st.subheader("Performance by Topic")
    if "topic" in df.columns and "percentage" in df.columns:
        topic_stats = (
            df.groupby("topic")["percentage"]
            .agg(["mean", "count", "last"])
            .round(1)
            .sort_values("mean")
        )
        topic_stats.columns = ["Avg Score %", "Attempts", "Last Score %"]
        st.dataframe(topic_stats, use_container_width=True)

    # Weakest topic
    progress = load_progress()
    weakest = progress.get("weakest_topic")
    if weakest:
        st.warning(f"Weakest topic: **{weakest}** — run `prep quiz --review` to practice")

    # Review suggestions
    review_topics = load_review_topics()
    if review_topics:
        st.subheader("Topics to Review")
        for t in review_topics:
            st.markdown(f"- {t}")

# ---------------------------------------------------------------------------
# Page: Today's Plan
# ---------------------------------------------------------------------------

elif page == "Today's Plan":
    st.title("Today's Plan")

    today_entry = load_today()
    state = load_state()
    progress = load_progress()

    if today_entry is None:
        next_day = progress.get("next_study_day")
        if next_day:
            st.info(f"No session today. Next study day: **{next_day}**")
        else:
            st.success("All sessions complete!")
        st.stop()

    # Today card
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Day", f"{today_entry.get('day_num', '?')} / {progress.get('total_days', '?')}")
        st.metric("Track", today_entry.get("track_id", "—"))
        st.metric("Topic", today_entry.get("topic", "—"))
    with col2:
        st.metric("Morning Focus", today_entry.get("morning_focus", "Study"))
        st.metric("Evening Focus", today_entry.get("evening_focus", "Practice"))
        status = today_entry.get("status", "pending")
        if status == "done":
            st.success("Session completed!")
        else:
            st.warning("Session pending")

    # Previous / next context
    today_str = date.today().isoformat()
    days = state.get("days", [])
    prev_entry = None
    next_entry = None
    for d in days:
        if d["date"] < today_str:
            prev_entry = d
        elif d["date"] > today_str and next_entry is None:
            next_entry = d

    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        if prev_entry:
            p_status = "done" if prev_entry.get("status") == "done" else "skipped"
            st.caption(f"Previous: {prev_entry['topic']} ({p_status})")
    with c2:
        if next_entry:
            st.caption(f"Up next: {next_entry['topic']}")

    # Quick actions
    st.divider()
    st.subheader("Quick Actions")
    st.code("prep study                  # Study guide for today's topic", language="bash")
    st.code("prep quiz --topic <bank>    # Quiz yourself", language="bash")
    st.code("prep done --minutes 30      # Mark today complete", language="bash")

# ---------------------------------------------------------------------------
# Page: Study Timeline
# ---------------------------------------------------------------------------

elif page == "Study Timeline":
    st.title("Study Timeline")

    state = load_state()
    days = state.get("days", [])

    if not days:
        st.info("No study plan found. Run `prep init` first.")
        st.stop()

    import pandas as pd

    df = pd.DataFrame(days)

    # Filter by track
    track_ids = sorted(df["track_id"].unique()) if "track_id" in df.columns else []
    if track_ids:
        selected = st.selectbox("Filter by track", ["All"] + track_ids)
        if selected != "All":
            df = df[df["track_id"] == selected]

    # Display columns
    display_cols = ["day_num", "date", "track_id", "topic", "status"]
    if "score" in df.columns:
        display_cols.append("score")
    if "minutes" in df.columns:
        display_cols.append("minutes")
    if "notes" in df.columns:
        display_cols.append("notes")

    available = [c for c in display_cols if c in df.columns]
    view = df[available].copy()

    # Color-code status
    today_str = date.today().isoformat()

    def style_status(row):
        status = row.get("status", "")
        d = row.get("date", "")
        if status == "done":
            return ["background-color: #C8E6C9"] * len(row)
        elif d == today_str:
            return ["background-color: #BBDEFB"] * len(row)
        return [""] * len(row)

    styled = view.style.apply(style_status, axis=1)
    st.dataframe(styled, use_container_width=True, height=600)

    # Summary
    done_count = sum(1 for d in days if d.get("status") == "done")
    st.caption(f"{done_count} / {len(days)} sessions completed")

# ---------------------------------------------------------------------------
# Page: Portfolio
# ---------------------------------------------------------------------------

elif page == "Portfolio":
    st.title("Portfolio & Hire Readiness")

    from prep_agent.agents.project import ProjectAgent

    agent = ProjectAgent()

    # Get quiz avg for hire-readiness
    progress = load_progress()
    quiz_avg = progress.get("avg_score", 0.0)
    summary = agent.get_portfolio_summary(quiz_avg)

    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Projects Completed", summary["projects_completed"])
    col2.metric("In Progress", summary["projects_in_progress"])
    col3.metric("Avg Rubric Score", f"{summary['avg_rubric_score']}%" if summary["avg_rubric_score"] is not None else "—")

    hr = summary["hire_readiness_pct"]
    col4.metric("Hire Readiness", f"{hr:.0f}%")

    # Hire readiness bar
    st.progress(min(hr / 100, 1.0), text=f"Hire readiness: {hr:.0f}%  (40% quiz performance + 60% project completion)")

    # User projects table
    user_projects = agent.list_user_projects()
    if user_projects:
        st.subheader("Your Projects")
        import pandas as pd

        rows = []
        for p in user_projects:
            rubric = p.get("rubric_results", [])
            met = sum(1 for r in rubric if r.get("met"))
            total = len(rubric)
            rows.append({
                "Title": p.get("title", p.get("id", "—")),
                "Status": p.get("status", "—"),
                "Rubric": f"{met}/{total}" if total else "—",
                "Score": f"{p.get('rubric_score', 0)}%" if p.get("rubric_score") is not None else "—",
                "Started": p.get("started_at", "—")[:10],
                "Completed": p.get("completed_at", "—")[:10] if p.get("completed_at") else "—",
            })
        df = pd.DataFrame(rows)

        def style_project_status(row):
            status = row.get("Status", "")
            if status == "completed":
                return ["background-color: #C8E6C9"] * len(row)
            elif status == "in_progress":
                return ["background-color: #FFF9C4"] * len(row)
            return [""] * len(row)

        styled = df.style.apply(style_project_status, axis=1)
        st.dataframe(styled, use_container_width=True)
    else:
        st.info("No projects started yet. Run `prep build list` to see available projects.")

    # Skills demonstrated
    skills = summary.get("skills_demonstrated", [])
    if skills:
        st.subheader("Skills Demonstrated")
        for s in skills:
            st.markdown(f"- {s}")

    # Available projects
    templates = agent.load_project_templates()
    completed_ids = {p["id"] for p in user_projects if p.get("status") == "completed"}
    available = [t for t in templates if t["id"] not in completed_ids]
    if available:
        st.subheader("Available Projects")
        for t in available:
            with st.expander(f"{t['title']} ({t.get('difficulty', '—')}, ~{t.get('estimated_hours', '?')}h)"):
                st.write(t.get("description", ""))
                rubric = t.get("rubric", [])
                if rubric:
                    st.caption("Rubric:")
                    for r in rubric:
                        st.markdown(f"- [ ] {r['description']}")
                st.code(f"prep build start {t['id']}", language="bash")
