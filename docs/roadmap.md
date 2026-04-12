# Career Prep Agent — Roadmap

**Created:** 2026-03-31
**Status:** ALL PHASES COMPLETE (1-6).

---

## Phase 1 — Template Expansion (COMPLETE)

**Goal:** Broad career coverage with pre-built content.

| Deliverable | Status |
|-------------|--------|
| 11 role templates (AI, Cloud, DevSecOps, SRE, etc.) | DONE |
| Knowledge packs per template | DONE |
| Quiz banks (~180 questions across 11 banks) | DONE |
| `prep pivot` — role transition recommender | DONE |
| `prep template validate/list` — YAML linter | DONE |
| `prep quiz --difficulty/--list` — difficulty filter | DONE |
| MCP server (9 tools) | DONE |
| Bug fixes: empty study plan, quiz engine, status display | DONE |

**Tracking doc:** `docs/phase1-template-expansion.md`

---

## Phase 2 — UX Polish & Data Integrity (COMPLETE)

**Goal:** Make the existing features reliable and informative. Fix what's half-wired.
**Status:** COMPLETE ✓

| # | Task | What / Why | Status |
|---|------|-----------|--------|
| 2.0 | Bug fixes | `done_cmd` wrong key names (0/0 progress), broken "already done" guard, `today_cmd` same guard bug | DONE |
| 2.1 | Per-track progress bars in `prep status` | Wired `get_progress()` to return per-track `{name, done, total}` — display already rendered it | DONE |
| 2.2 | Fix streak calculation | Rewrote `_calc_streak()` to count backwards from today, not from end of list | DONE |
| 2.3 | Show quiz performance in `prep status` | Added quizzes taken, avg score, weakest topic to dashboard | DONE |
| 2.4 | Study time tracking | `--minutes` flag on `prep done`, stored in tracker.md, summed as study_hours in status | DONE |
| 2.5 | Previous/next session context in `prep today` | Shows previous session (done/skipped) and upcoming topic | DONE |
| 2.6 | Estimated completion date in `prep status` | Last pending day's date shown in dashboard | DONE |
| 2.7 | `prep done` on rest day shows next session | Shows next study date instead of generic message | DONE |

**Tests:** 155 passing (8 new tests for Phase 2 features + backward compat).

**Exit criteria met:** `prep init → prep today → prep done --minutes 30 → prep status` shows track bars, streak, 0.5h study time, quiz stats, and estimated completion date.

---

## Phase 3 — Content Growth Engine (COMPLETE)

**Goal:** Make quiz banks and knowledge packs easy to expand — both manually and with AI.
**Status:** COMPLETE ✓

| # | Task | What / Why | Status |
|---|------|-----------|--------|
| 3.0 | Bug fixes | `quiz_cmd` passed invalid `config=` param to `generate_mock_interview_prompt` and `generate_ai_quiz_prompt` | DONE |
| 3.1 | `prep quiz --generate` | Ollama direct (auto-save) + clipboard round-trip fallback. Generates quiz bank JSON via AI prompt | DONE |
| 3.2 | `prep quiz --import-file` | Import from local JSON file or URL. Validates schema, saves to `~/.prep/quiz_banks/` | DONE |
| 3.3 | `prep update` | Pulls latest quiz banks, knowledge packs, templates from GitHub. Compares version numbers, only downloads newer | DONE |
| 3.4 | Quiz bank validation | `validate_bank()` enforces schema: required fields, MC options/answer, open key_points, difficulty values | DONE |
| 3.5 | Spaced repetition | `prep quiz --review` resurfaces previously wrong answers. Matches weak_areas from quiz history back to bank questions | DONE |
| 3.6 | Community contribution guide | Updated CONTRIBUTING.md with full JSON schema, validation command, and PR instructions | DONE |

**Tests:** 163 passing (8 new tests for Phase 3 features).

**Exit criteria met:** `prep quiz --import-file` validates and saves, `prep quiz --generate` creates AI-assisted banks, `prep quiz --review` resurfaces wrong answers, `prep update` pulls from GitHub, `prep quiz --list` shows both built-in and user banks.

---

## Phase 4 — Local Web Dashboard (COMPLETE)

**Goal:** Visual dashboard running on localhost — richer than terminal output, zero cloud dependency.
**Technology:** Streamlit (single Python file, built-in charts).
**Status:** COMPLETE ✓

| # | Task | What / Why | Status |
|---|------|-----------|--------|
| 4.1 | `prep dashboard` command | Launches Streamlit on `localhost:8501`, auto-opens browser | DONE |
| 4.2 | Overview page | Metrics (days, streak, hours, quiz avg), progress bar, track breakdown bar chart, est. completion | DONE |
| 4.3 | Quiz Analytics page | Score trend line chart, topic performance table, weakest topic callout, review suggestions | DONE |
| 4.4 | Today's Plan page | Day card with track/topic/focus, previous/next context, quick action commands | DONE |
| 4.5 | Study Timeline page | Full day-by-day table, track filter, color-coded status (green=done, blue=today) | DONE |

**Deferred to future iteration:**
- 4.6 Knowledge base browser — browse notes and knowledge packs in browser
- 4.7 Export / share — export progress report as PDF

**Tests:** 163 passing. Dashboard is a Streamlit app (not unit-testable), verified via HTTP 200 check.

**Exit criteria met:** `prep dashboard` opens browser with 4 pages: overview with charts, quiz analytics, today's plan, and study timeline. Fully local, no internet required.

---

## Phase 5 — Smart Prep (AI-Enhanced) (COMPLETE)

**Goal:** Make the agent genuinely adaptive — study sessions that respond to performance, not just a fixed schedule.
**Status:** COMPLETE ✓

| # | Task | What / Why | Status |
|---|------|-----------|--------|
| 5.1 | Adaptive study plan | Planner agent modifies tracker on quiz results: inserts review days (score <50%), compresses tracks (score >85%). Wired into `prep done` | DONE |
| 5.2 | AI study sessions | Enhanced `_build_study_prompt` with quiz history, weak areas, teaching approach hints. Session logging to `~/.prep/sessions/` | DONE |
| 5.3 | Weak area deep-dives | `prep study --weak` auto-selects weakest topic from quiz history | DONE |
| 5.5 | Progress insights | `prep insights` — pace analysis, strongest/weakest topics, consistency stats, actionable recommendations | DONE |

**Deferred:**
- 5.4 Mock interview mode — timed simulation (existing `--mock-interview` covers basic version)
- 5.6 Multi-role prep — large architectural change, separate initiative

**Tests:** 168 passing (5 new for adaptive plan + tracker mutations).

**Exit criteria met:** Plan adjusts based on quiz performance, `prep study --weak` targets weak areas, `prep insights` provides data-driven recommendations.

---

## Phase 6 — Hands-On Project Generator & Portfolio Engine (COMPLETE)

**Goal:** Bridge the gap between knowledge acquisition and demonstrable competence. Generate scoped, buildable mini-projects tailored to the user's skill gaps, with evaluation rubrics and portfolio-ready write-ups. This turns prep-agent from a study tool into a **career transition engine** — quiz scores don't get you hired, targeted portfolio projects do.
**Status:** COMPLETE ✓

**Why this is the highest-leverage next step:**
- The entire system (Phases 1–5) optimizes for knowledge recall. But career transitions are won by **proof of ability** — repos, write-ups, artifacts.
- Role templates already define required skills. Gap analysis already knows what's weak. The adaptive planner already adjusts. A `ProjectAgent` maps gaps → scoped projects naturally.
- Compounds with everything already built: quiz performance informs project difficulty, knowledge packs provide reference material, dashboard gets a Portfolio tab, insights can nudge "you've studied K8s security for 12 days but haven't built anything."

**Architecture:**
- New `ProjectAgent` (ReAct pattern, like existing agents) in `agents/project.py`
- Project templates stored as YAML in `project_templates/` (per-role, per-track)
- Project state tracked in `~/.prep/projects/` (status, rubric results, write-ups)
- New Pydantic models: `ProjectSpec`, `ProjectEntry`, `ProjectStatus`, `ProjectDifficulty`, `RubricItem`, `PortfolioSummary`
- Dashboard: new **Portfolio** tab (projects completed, skills demonstrated, hire-readiness score)

| # | Task | What / Why | Status |
|---|------|-----------|--------|
| 6.1 | Project template schema & seed data | YAML schema for project specs with rubric, scaffolding, difficulty. 9 projects seeded across 4 roles (AI Platform, Cloud SA, SRE, DevSecOps) | DONE |
| 6.2 | `prep build list` | Lists available projects ranked by gap impact (weak quiz topics score higher). Shows difficulty, hours, track, status | DONE |
| 6.3 | `prep build start <id>` | Scaffolds project directory (`~/.prep/projects/<id>/`), writes starter files, saves project state | DONE |
| 6.4 | `prep build check <id>` | Interactive rubric self-evaluation. Scores per item, auto-completes project at 100% | DONE |
| 6.5 | `prep build showcase <id>` | Generates portfolio write-up (SHOWCASE.md) with sections for decisions, skills, learnings | DONE |
| 6.6 | Portfolio dashboard tab | Streamlit page: metrics row, hire-readiness bar, project table, skills list, available projects with expandable details | DONE |
| 6.7 | `prep build status` | Portfolio summary with hire-readiness score (40% quiz + 60% project completion) | DONE |

**Deferred:**
- 6.8 `prep build list --community` — browse/import community-contributed project templates
- 6.9 AI-assisted project review — LLM evaluates code/artifacts against rubric (requires AI provider)
- 6.10 GitHub integration — auto-create repo, push scaffolding, link in portfolio

**Tests:** 193 passing (25 new for Phase 6: models, template loading, lifecycle, ranking, portfolio summary, ReAct behavior).

**Exit criteria met:** `prep build list` shows gap-ranked projects → `prep build start` scaffolds a project → user builds it → `prep build check` evaluates against rubric → `prep build showcase` generates portfolio write-up → dashboard Portfolio tab shows hire-readiness score combining quiz + project data.

---

## Dependency Graph

```
Phase 1 (DONE)
    │
    ▼
Phase 2 (UX Polish)  ← do this first, foundation for everything else
    │
    ├──────────────────┐
    ▼                  ▼
Phase 3 (Content)   Phase 4 (Dashboard)  ← can run in parallel
    │                  │
    └────────┬─────────┘
             ▼
      Phase 5 (Smart Prep)  ← benefits from both content + dashboard
             │
             ▼
      Phase 6 (Portfolio Engine)  ← leverages gaps, quizzes, adaptive plan, dashboard
```

---

## Principles

1. **Offline-first** — everything works without internet or API keys
2. **AI is optional** — LLM features enhance but never gate core functionality
3. **Privacy-first** — all data stays in `~/.prep/`, nothing phones home
4. **Generic** — no company-specific content, useful for anyone
5. **Showcase-worthy** — every phase demonstrates a real agentic AI pattern (ReAct, MCP, RAG, evaluation)
