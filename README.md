# Platform Prep Kit

> A privacy-first CLI that turns any job posting into a personalized study plan — with daily reminders, built-in quizzes, a growing knowledge base, and optional AI-powered study sessions.

**100% local. 100% private. Works without any AI subscription.**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-221%20passed-brightgreen.svg)](#testing)

---

## Why This Exists

Career transitions are hard. There's always too much to learn, no structure, and no accountability. Most people start strong and fade after a week.

Platform Prep Kit solves this by:
- **Analyzing the gap** between where you are (resume) and where you want to be (job posting)
- **Generating a day-by-day study plan** that adapts based on your quiz performance
- **Nudging you daily** with desktop notifications so you never miss a session
- **Testing your knowledge** with built-in quizzes, spaced repetition, and AI-generated questions
- **Generating portfolio projects** scoped to your skill gaps with rubrics and showcase write-ups
- **Building a knowledge base** that grows as you study — your personal reference library
- **Visual dashboard** on localhost with progress charts, quiz analytics, portfolio tracking, and hire-readiness score

It's built for engineers, by engineers. No web app, no login, no subscription required.

---

## Quick Start

### 1. Clone and install

```bash
git clone https://github.com/aiforge-labs/platform-prep-kit.git
cd platform-prep-kit
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[ui]"
```

> **Requirements:** Python 3.10+ and that's it. The `[ui]` extra includes the web dashboard (FastAPI, HTMX). Use `pip install -e ".[all]"` for everything (PDF parsing, job URL fetching, etc.).

### 2a. Web UI (recommended)

```bash
prep serve
```

Opens `http://localhost:8080` with a step-by-step onboarding wizard:
1. Enter your name and current role
2. Pick a role template (12 built-in career paths)
3. Paste a job posting URL and/or upload your resume (PDF/DOCX) for fitment analysis
4. Set your timeline (weeks, hours/day, study days)
5. Review and create your plan

### 2b. CLI

```bash
# Analyze a job posting + your resume
prep init --job-url "https://careers.example.com/jobs/12345" --resume ~/resume.pdf

# Or use a built-in role template
prep init --template cloud-security-lead

# Or interactive guided setup
prep init --interactive
```

The agent analyzes your profile against the job requirements, identifies gaps, and generates a personalized prep plan:

```
$ prep init --job-url "https://..." --resume ~/resume.pdf

Platform Prep Kit v1.0.0
  Job analyzed: Cloud Security Lead
  Resume parsed: 15 years experience, 4 certs
  Fitment score: 74/100
  Gaps identified: 6 topics across 3 tracks
  Study plan: 8 weeks, 50 study days
  Reminders set: 07:00 and 19:00 daily

Run `prep today` to see your first day's plan.
```

### Reinitializing (Starting Fresh)

If your workspace already exists and you want to start over — for example, switching to a different template or role — clean it up first:

```bash
# 1. Remove the workspace
rm -rf ~/.prep

# 2. (macOS only) Unload and remove any launchd reminder agents
launchctl unload ~/Library/LaunchAgents/com.platform-prep-kit.morning.plist 2>/dev/null
launchctl unload ~/Library/LaunchAgents/com.platform-prep-kit.evening.plist 2>/dev/null
rm -f ~/Library/LaunchAgents/com.platform-prep-kit.{morning,evening}.plist

# 3. Reinitialize
prep init --template ai-security-engineer
```

> On Linux the scheduler uses crontab — `prep init` automatically removes old entries before adding new ones, so no manual cleanup is needed.
> On Windows, `schtasks` entries are replaced automatically on reinit.

If you want to skip the reminder setup during testing, use `--no-interactive`:

```bash
prep init --template ai-security-engineer --no-interactive
```

---

## Daily Workflow

```bash
# Morning: see what's on today
$ prep today

  Day 5 / 50  |  Week 1  |  10% complete
  Track: AI Security Foundations
  Topic: OWASP LLM Top 10 — Vulnerabilities #6-#10
  Morning: Study vulnerabilities #6-#10
  Evening: Write 1-paragraph summaries
  ████████░░░░░░░░░░░░░░░░░░░░░░  10%

# Study (standalone or AI-powered)
$ prep study                # Shows study guide from knowledge packs
$ prep study --with-ai      # Generates AI prompt (or starts Claude Code session)
$ prep study --weak         # Auto-study your weakest topic

# Test yourself
$ prep quiz
$ prep quiz --review               # Spaced repetition of missed questions
$ prep quiz --mock-interview --copy   # Copy mock interview prompt to clipboard

# End of day
$ prep done --minutes 45 --notes "Covered all 10 vulnerabilities" --score 8

# Build portfolio projects
$ prep build list           # Projects ranked by your weakest areas
$ prep build start rag-eval-dashboard  # Scaffold and start building

# Track your progress
$ prep status               # CLI dashboard with track bars and quiz stats
$ prep insights             # Pace analysis, strengths, weaknesses, recommendations
$ prep build status         # Portfolio summary + hire-readiness score
$ prep serve                # Full interactive web UI (localhost:8080)
$ prep dashboard            # Legacy analytics dashboard (localhost:8501)
```

---

## Features

### Auto-Analysis
Give it a job URL and your resume — it identifies your strengths, gaps, and generates a fitment score with actionable study priorities.

### Study Plan Generation
Converts gaps into a calendar-aware, priority-ordered study schedule. Critical topics first. Review days every 3rd session. Interview prep reserved for the final weeks.

### Desktop Reminders
Native OS notifications (macOS, Linux, Windows) at your configured times. Contextual messages with streak counts and topic previews.

```bash
prep remind set 07:00 20:00    # Set times
prep remind pause --hours 4    # Snooze
prep remind skip               # Skip today
```

### Built-in Quizzes
15-20 question quiz banks per topic. Multiple choice + open-ended with self-assessment. Score tracking, spaced repetition, and AI-generated question banks.

```bash
prep quiz                          # Today's topic
prep quiz --topic "OWASP LLM"     # Specific topic
prep quiz --difficulty hard        # Filter by difficulty
prep quiz --review                 # Spaced repetition of missed questions
prep quiz --generate --topic "K8s" --num 10   # AI-generate new questions
prep quiz --import-file bank.json  # Import community question bank
prep quiz --mock-interview         # Full mock interview
prep quiz --list                   # See all available quiz banks
```

### Interactive Web UI

A full self-hosted web application running on localhost. Study in the browser, take interactive quizzes, track section-level progress, and pick up where you left off.

```bash
pip install platform-prep-kit[ui]
prep serve
```

Opens at `http://localhost:8080` with 7 pages:
- **Dashboard** — metrics, track progress bars, streak, timeline preview
- **Today** — current study card with mark-done form
- **Study Plan** — week-grouped timeline, track filters, inline completion
- **Quizzes** — 11 quiz banks, interactive sessions with answer feedback, session resume (close browser, come back, continue from where you left off)
- **Knowledge** — rich HTML rendering of all knowledge packs with section-by-section completion checkboxes
- **Portfolio** — projects, rubrics, hire-readiness score
- **Settings** — AI provider, reminders, workspace info

Built with FastAPI + HTMX + SQLite. No Node.js, no CDN, no internet required. All open source (MIT/BSD).

**Web-based onboarding:** If no workspace exists, `prep serve` opens a 5-step onboarding wizard:
- Select from 12 role templates (AI Security Engineer, Platform Engineer, ML Engineer, etc.)
- Paste a **job posting URL** — the agent fetches and parses it automatically
- Upload your **resume** (PDF, DOCX, TXT) — parsed locally, deleted immediately after
- If both provided, a **fitment analysis** shows your match score, skill gaps, and study priorities
- Set your timeline and create a personalized study plan

Everything happens locally. No data leaves your machine.

### Legacy Dashboard (Streamlit)

```bash
pip install platform-prep-kit[dashboard]
prep dashboard
```

Opens a read-only analytics dashboard at `localhost:8501`. This is deprecated in favor of `prep serve`.

### Portfolio Projects
Bridge the gap between studying and proving you can do the job. The agent generates scoped projects tailored to your skill gaps, with rubrics and portfolio-ready write-ups.

```bash
prep build list                    # Projects ranked by your weakest areas
prep build start rag-eval-dashboard  # Scaffold project with starter files
prep build check rag-eval-dashboard  # Self-evaluate against rubric
prep build showcase rag-eval-dashboard  # Generate portfolio write-up
prep build status                  # Portfolio summary + hire-readiness score
```

9 projects across 4 roles — RAG Eval Dashboard, Multi-Agent Observability, LLM Cost Optimizer, IaC Pipeline, SLI/SLO Dashboard, and more. Each project includes:
- **Starter files** — README, requirements, boilerplate code
- **Evaluation rubric** — checklist of what "done" looks like
- **Showcase generator** — markdown write-up you can use in applications
- **Gap-ranked ordering** — projects addressing your weak quiz topics surface first

### Adaptive Study Plan
The agent adjusts your plan based on actual performance:
- **Low quiz scores (<50%)** automatically insert review days
- **High quiz scores (>85%)** compress tracks to save time
- Adjustments happen automatically after `prep done`

### Progress Insights
Data-driven weekly analysis of your preparation:

```bash
prep insights
```

Shows pace (ahead/on-track/behind), strongest and weakest topics by quiz score, study consistency, and actionable recommendations.

### Content Updates
Pull the latest quiz banks, templates, and knowledge packs from GitHub:

```bash
prep update
```

### Knowledge Base
A growing personal reference library organized by topic. Search, review, and export.

```bash
prep note add "OWASP LLM" "Prompt injection: direct (user) vs indirect (data)"
prep note search "injection"
prep note show "OWASP LLM"
```

### AI Integration (Optional)
Works with any AI tool — or none at all. **The default ("None") gives you the full experience** — all 11 quiz banks, 11 knowledge packs, study plans, progress tracking, and the web UI work without any AI provider.

AI providers enhance two specific features:
- `prep study --with-ai` — generates an AI-powered tutoring session
- `prep quiz --generate` — creates new quiz questions using AI

| Provider | Cost | When to use |
|----------|------|-------------|
| **None** | Free | Default. All built-in content works. No setup needed |
| **Ollama** | Free | You run a local LLM (Llama, Mistral). Fully offline AI tutoring |
| **ChatGPT/Claude (web)** | Free | Generates a prompt, copies to clipboard. Paste into ChatGPT/Claude web |
| **Claude Code** | Paid | Generates CLAUDE.md so Claude Code auto-resumes your sessions |
| **OpenAI API** | Paid | Direct API calls for AI-generated study sessions and questions |

Configure via the web UI (Settings page) or CLI:
```bash
prep config --ai-provider ollama    # or: none, claude-code, chatgpt-paste, openai-api
```

### Role Templates
Pre-built study plans for common career transitions:

| Template | Target Role | Domain |
|----------|------------|--------|
| `ai-platform-engineer` | AI Platform Engineer | LLMOps, RAG, GenAI systems |
| `ai-security-engineer` | AI Security Engineer | LLM red-teaming, adversarial ML, AI governance |
| `cloud-compliance-engineer` | Cloud Compliance Engineer | Policy-as-code, CIS, audit automation |
| `cloud-security-lead` | Cloud Security Lead | Cloud/AI security leadership |
| `cloud-solutions-architect` | Solutions Architect | Cloud architecture, AWS/GCP/Azure |
| `devsecops-engineer` | DevSecOps Engineer | Shift-left security, SAST/DAST, container security |
| `iac-gitops-engineer` | IaC & GitOps Engineer | Terraform, CDK, Pulumi, ArgoCD |
| `ml-engineer` | ML Engineer | Feature stores, MLOps pipelines, drift monitoring |
| `platform-engineer` | Platform Engineer | IDP, Backstage, Crossplane, GitOps |
| `site-reliability-engineer` | Site Reliability Engineer | SLOs, observability, chaos engineering |
| `solutions-engineer` | Solutions Engineer | Presales, demo engineering, POC delivery |
| `custom` | Any role | Blank template |

**Not sure which template fits you?** Use `prep pivot` to find out:

```bash
prep pivot --from software_engineering   # ranked pivot targets with ramp time
prep pivot --from devops_sre --top 3
```

---

## Architecture

### Multi-Agent System with ReAct Reasoning

The agent is built using the **ReAct (Reasoning + Action)** pattern — the foundation of modern agentic AI. Each component observes state, reasons about what to do, acts, and evaluates the outcome.

```
                         User
                          │
                    ┌─────┴─────┐
                    │    CLI    │
                    └─────┬─────┘
                          │
                   ┌──────┴──────┐
                   │Orchestrator │ ← ReAct meta-loop: which agent to invoke?
                   └─┬──┬──┬──┬─┘
        ┌────────────┤  │  │  ├────────────┐
        │            │  │  │  │            │
   ┌────┴────┐ ┌─────┴──┴┐ ┌┴────────┐ ┌──┴───────┐ ┌──┴───────┐
   │Planner  │ │ Tutor   │ │  Quiz   │ │ Reviewer │ │ Project  │
   │Agent    │ │ Agent   │ │  Agent  │ │ Agent    │ │ Agent    │
   │         │ │         │ │         │ │          │ │          │
   │Schedule │ │Teach &  │ │Test &   │ │Analyze & │ │Scaffold &│
   │Optimize │ │Adapt    │ │Evaluate │ │Recommend │ │Evaluate  │
   └────┬────┘ └────┬────┘ └────┬────┘ └────┬─────┘ └────┬─────┘
        │           │           │            │            │
   ┌────┴───────────┴───────────┴────────────┴────────────┴──┐
   │              Pydantic Models (typed I/O)                 │
   ├─────────────────────────────────────────────────────────┤
   │  Storage: config.yml │ tracker.md │ knowledge/ │ projects/│
   └─────────────────────────────────────────────────────────┘
```

### The ReAct Loop (in every agent)

```
Observe (state) → Reason (decide) → Act (execute) → Evaluate (assess)
     ↑                                                      │
     └──────────────── Loop if not satisfied ───────────────┘
```

**What makes this an agent, not just a tool:**
- Agents **reason** about what to do (not just follow instructions)
- Agents **adapt** based on your progress (not fixed scripts)
- Agents **evaluate** their own actions (self-improving loop)
- Agents **communicate** via typed contracts (Pydantic models)

### Design Decisions

| Decision | Pattern | Why |
|----------|---------|-----|
| ReAct reasoning | Observe-Reason-Act-Evaluate loop | Agents decide, not just execute |
| Multi-agent decomposition | 4 specialized agents + orchestrator | Each agent has a clear, testable responsibility |
| Pydantic schemas | Typed I/O contracts | Validated, self-documenting agent communication |
| Markdown storage | Human-readable persistence | Git-friendly, survives tool changes |
| Provider-agnostic AI | Bridge pattern | Decouples from any specific AI provider |
| Evaluation harness | Test scenarios + metrics | Measurable agent reliability |

See [docs/architecture.md](docs/architecture.md) for the full architecture guide with data flows and design rationale.

---

## Installation

See [Quick Start](#quick-start) for the recommended setup. Below are the available extras you can mix and match:

```bash
pip install -e "."              # Core only (click, pyyaml, rich, pydantic)
pip install -e ".[ui]"          # + Web UI (FastAPI, HTMX, SQLite) — recommended
pip install -e ".[pdf]"         # + PDF resume parsing
pip install -e ".[web]"         # + Job URL fetching
pip install -e ".[dashboard]"   # + Legacy Streamlit dashboard
pip install -e ".[all]"         # Everything
```

**Requirements:** Python 3.10+ and that's it.

---

## All Commands

| Command | Description |
|---------|-------------|
| `prep init` | Initialize a prep workspace from a job URL, resume, or template |
| `prep today` | Show today's study schedule with previous/next context |
| `prep study` | Start a study session (standalone or AI-powered) |
| `prep study --weak` | Auto-study your weakest topic based on quiz scores |
| `prep done` | Mark today as completed with notes, score, and time spent |
| `prep status` | Full dashboard — track bars, streak, quiz stats, estimated completion |
| `prep insights` | Pace analysis, strongest/weakest topics, recommendations |
| `prep serve` | Start interactive web UI at localhost:8080 |
| `prep dashboard` | Open legacy Streamlit dashboard (localhost:8501) |
| `prep quiz` | Take a quiz with adaptive difficulty |
| `prep quiz --review` | Spaced repetition of previously missed questions |
| `prep quiz --generate` | Generate new questions using AI (Ollama or clipboard) |
| `prep quiz --import-file` | Import a quiz bank from JSON file or URL |
| `prep quiz --list` | List all available quiz banks with difficulty breakdown |
| `prep update` | Pull latest content updates from GitHub |
| `prep fitment` | View your job fitment analysis |
| `prep pivot` | Recommend role transitions ranked by skill overlap |
| `prep template validate` | Validate a template YAML against the schema |
| `prep template list` | List all available role templates |
| `prep note add/list/show/search` | Manage knowledge base notes |
| `prep remind set/pause/resume/skip` | Manage desktop reminders |
| `prep build list` | List portfolio projects ranked by gap impact |
| `prep build start <id>` | Scaffold a project with starter files and rubric |
| `prep build check <id>` | Self-evaluate a project against its rubric |
| `prep build showcase <id>` | Generate a portfolio write-up (SHOWCASE.md) |
| `prep build status` | Portfolio summary with hire-readiness score |
| `prep export` | Export progress report (markdown or JSON) |
| `prep eval` | Run agent evaluation harness |
| `prep mcp` | Start the MCP server for IDE integration |

---

## Knowledge Packs

Pre-built study materials automatically surfaced during `prep study`:

| Pack | Topics covered |
|------|---------------|
| **LLMOps Patterns** | RAG architectures, chunking, vector DBs, model serving (vLLM/TGI), RAGAS evaluation |
| **Platform Engineering** | IDP maturity, Backstage, ArgoCD vs Flux, Crossplane vs Terraform, OPA Gatekeeper |
| **SRE Fundamentals** | SLI/SLO/SLA, error budgets, USE/RED methods, chaos engineering, post-mortem templates |
| **ML Lifecycle** | Feature stores, train-serve skew, experiment tracking, deployment patterns, drift detection |
| **IaC & GitOps** | Terraform state, GitOps workflows, Atlantis, Conftest/Rego, Terratest |
| **Policy-as-Code** | OPA/Rego, CIS Benchmarks, CSPM tools, SOC 2 cloud controls, AWS Control Tower |
| **Solutions Engineering** | SPIN discovery, MEDDPICC, POC design, ROI calculation, objection handling |
| **OWASP LLM Top 10** | All 10 vulnerabilities with examples, mitigations, and cloud security analogues |
| **NIST AI RMF** | All 4 functions (GOVERN/MAP/MEASURE/MANAGE), trustworthy AI, GenAI profile |
| **MITRE ATLAS** | AI threat landscape, 14 tactics, 20 key techniques, threat modeling methodology |
| **Interview Frameworks** | STAR method, system design, behavioral questions, communication tips |

---

## Privacy

This tool is designed with privacy as a non-negotiable constraint:

- **No telemetry.** No analytics. No data collection. No phone-home behavior.
- **No accounts.** No cloud sync. No subscriptions required.
- **All data stays local** in `~/.prep/` on your machine.
- **The codebase contains zero** personal data, company names, or client references.
- **Job postings and resumes** are parsed locally and never transmitted.
- **Optional AI calls** are explicit and user-initiated only.

---

## AI Agent Design Framework

This project follows the 10-step "How to Build AI Agents from Scratch" framework:

| Step | Concept | Implementation |
|------|---------|---------------|
| 1. Define Role & Goal | What does the agent do? | Career coaching: analyze gaps, generate plans, track progress |
| 2. Structured I/O | Pydantic schemas | 20+ typed models for inter-agent communication |
| 3. Tune Behavior | Role-based prompts, MCP | AI Bridge generates role-specific prompts + CLAUDE.md |
| 4. Reasoning & Tool Use | ReAct pattern | Every agent runs Observe-Reason-Act-Evaluate loops |
| 5. Multi-Agent Logic | Agent decomposition | Planner, Tutor, Quiz, Reviewer + Orchestrator |
| 6. Memory & Context | Knowledge base + tracker | Markdown persistence + session memory |
| 7. Voice/Vision | Optional | Not in v1 (planned) |
| 8. Deliver Output | Markdown, JSON, Rich terminal | Progress reports, quizzes, study guides |
| 9. Wrap in UI | CLI + web dashboard | Click CLI + Streamlit dashboard on localhost |
| 10. Evaluate & Monitor | Test scenarios + metrics | Evaluation harness with 5 behavior tests + analytics |

This mapping makes the project a **learning resource for agentic AI development** — each component demonstrates a real-world agent pattern.

---

## Development Setup

Follow the [Quick Start](#quick-start) clone steps, then install all extras including dev tools:

```bash
# Option A: Makefile (recommended)
make init-dev
source .venv/bin/activate

# Option B: Manual
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[all,ui,dashboard,dev]"
```

### Testing

```bash
make test           # Run test suite
make test-cov       # With coverage
make lint           # Syntax checks
make check-secrets  # Scan for leaked secrets
```

### Running the Web UI in Development

```bash
make serve-dev      # Auto-reload on code changes
```

---

## Contributing

We welcome contributions! The easiest ways to help:

- **Add a role template** — Know a career path? Create a YAML template
- **Add a knowledge pack** — Write study materials for a topic
- **Add quiz questions** — Expand the question banks
- **Add project templates** — Create portfolio projects for a role (see `project_templates/`)
- **Bug fixes and features** — See [CONTRIBUTING.md](CONTRIBUTING.md)

---

## Documentation

| Guide | Description |
|-------|-------------|
| [Architecture Site](https://aiforge-labs.github.io/platform-prep-kit/) | Interactive architecture overview with click-to-explore components |
| [Getting Started](docs/getting-started.md) | Installation and first steps |
| [Architecture](docs/architecture.md) | System design, data flow, key decisions |
| [AI Integration](docs/ai-integration.md) | Setting up AI providers |
| [Creating Templates](docs/creating-templates.md) | How to build role templates |

---

## FAQ & Troubleshooting

### Setup Issues

**`zsh: command not found: prep`**
You need to install the package and activate the virtual environment first:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[ui]"
prep --version
```
The `prep` command is only available inside the activated venv. Each new terminal needs `source .venv/bin/activate`.

**`ERROR: Package 'platform-prep-kit' requires a different Python`**
The project requires Python 3.10+. Check your version and install a newer one:
```bash
python3 --version          # Must be 3.10+
brew install python@3.12   # macOS
# Then recreate your venv:
rm -rf .venv
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e ".[all,ui,dev]"
```

**`ModuleNotFoundError: No module named 'fastapi'` when running `prep serve`**
Install the web UI dependencies:
```bash
pip install platform-prep-kit[ui]
# Or if developing:
pip install -e ".[ui]"
```

**`Address already in use` when starting the server**
Another process is using port 8080. Either stop it or use a different port:
```bash
prep serve --port 8090
```

### Web UI

**How do I access the web UI?**
```bash
source .venv/bin/activate
prep serve
```
Opens automatically at `http://localhost:8080`. Use `--no-open` to skip auto-opening the browser.

**Can I access the web UI from another device on my network?**
By default, the server binds to `127.0.0.1` (localhost only) for security. If you want LAN access:
```bash
prep serve --host 0.0.0.0
```
A warning will be displayed. This is not recommended for untrusted networks.

**I closed the browser mid-quiz. Is my progress lost?**
No. Quiz sessions are saved to SQLite. Reopen the same quiz session URL and you'll resume from where you left off.

**The dashboard shows 0/0 days after `prep serve`**
Run `prep init` (CLI) or complete the web onboarding wizard first. The web UI redirects to the onboarding wizard automatically if no workspace exists.

### Study Plan

**How do I start over with a different template?**
```bash
rm -rf ~/.prep
prep init --template platform-engineer
# Or use the web UI:
prep serve    # Will show the onboarding wizard
```

**`No study session scheduled for today`**
The study plan uses calendar dates. Your first study day may be tomorrow depending on when you initialized. Check `prep status` or the Study Plan page in the web UI to see your schedule.

**Can I use both the CLI and web UI at the same time?**
Yes. Both share the same data. The web UI writes to SQLite and syncs to `tracker.md` (which the CLI reads). If you make changes via CLI while the web UI is open, it detects the change and re-imports automatically.

### AI Provider

**Do I need an AI provider to use this tool?**
No. The default setting ("None / standalone") gives you the full experience — all 11 quiz banks, 13 knowledge packs, study plans, progress tracking, and the web UI work without any AI provider.

**When would I use an AI provider?**
AI providers enhance two optional features:
- `prep study --with-ai` — generates an AI-powered interactive tutoring session
- `prep quiz --generate` — creates new quiz questions using AI

If you don't use these commands, you don't need an AI provider.

**Which AI provider should I choose?**
- **Ollama** (free) — best if you want AI features without paying, runs on your machine
- **ChatGPT paste** (free) — generates a prompt you paste into ChatGPT's web UI
- **Claude Code** (paid) — best integration, auto-resumes study sessions
- **OpenAI API** (paid) — direct API calls, requires an API key

### Data & Privacy

**Where is my data stored?**
Everything is in `~/.prep/` on your machine. Nothing is sent to any server unless you explicitly use an AI provider.

**Is my data encrypted?**
No. Data is stored as plain YAML, Markdown, JSON, and SQLite files. This is a personal tool designed for local use on your own machine.

**How do I export my progress?**
```bash
prep export              # Markdown report
prep export --format json  # JSON export
```

### Content & Updates

**How do I get new quiz questions and knowledge packs?**
```bash
prep update    # Pulls latest content from GitHub
```
Community contributions (new templates, quiz banks, knowledge packs) are added via pull requests.

**Can I add my own study materials?**
Yes:
```bash
prep note add "Topic Name" "Your notes here"    # Personal knowledge base
```
Or create files directly:
- Knowledge packs: `knowledge_packs/your-topic.md`
- Quiz banks: `quiz_banks/your-topic.json` (see CONTRIBUTING.md for the schema)

---

## License

MIT License. See [LICENSE](LICENSE).
