# Architecture

## Design Philosophy

Career Prep Agent follows four core principles:

1. **Privacy-first** — All data stays local. No telemetry, no cloud sync, no accounts.
2. **AI-optional** — The tool works fully without any AI subscription. AI enhances, never gates.
3. **Markdown-native** — All state is human-readable markdown/YAML/JSON. No database. Git-friendly.
4. **Graceful degradation** — Missing optional dependencies produce helpful messages, never crashes.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         CLI Layer (Click)                          │
│  prep init │ today │ study │ done │ status │ quiz │ remind │ note  │
└──────┬──────┬──────┬──────┬──────┬──────┬──────┬──────┬───────────┘
       │      │      │      │      │      │      │      │
┌──────┴──────┴──────┴──────┴──────┴──────┴──────┴──────┴───────────┐
│                        Core Layer                                  │
│                                                                    │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌───────────────┐     │
│  │  Config   │  │ Planner  │  │ Tracker  │  │   Analyzer    │     │
│  │ (YAML)   │  │ (Study   │  │(Progress │  │ (Fitment      │     │
│  │          │  │  Plans)  │  │ Tracking)│  │  Scoring)     │     │
│  └──────────┘  └──────────┘  └──────────┘  └───────────────┘     │
│                                                                    │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────────────────┐    │
│  │  Quiz    │  │Knowledge │  │      Template Loader          │    │
│  │ Engine   │  │  Base    │  │  (Role-specific study plans)  │    │
│  └──────────┘  └──────────┘  └──────────────────────────────┘    │
└──────┬─────────────────┬─────────────────────┬────────────────────┘
       │                 │                     │
┌──────┴─────────────────┴─────────────────────┴────────────────────┐
│                    Integration Layer                               │
│                                                                    │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌───────────────┐    │
│  │ Resume   │  │   Job    │  │Scheduler │  │   AI Bridge   │    │
│  │ Parser   │  │ Fetcher  │  │(OS-native│  │ (Provider-    │    │
│  │(PDF/DOCX)│  │(URL/HTML)│  │ Remind)  │  │  agnostic)    │    │
│  └──────────┘  └──────────┘  └──────────┘  └───────────────┘    │
│                                                                    │
│  ┌────────────────────────┐                                       │
│  │  Notifier (Desktop)    │                                       │
│  │  macOS│Linux│Windows   │                                       │
│  └────────────────────────┘                                       │
└───────────────────────────────────────────────────────────────────┘
       │                 │                     │
┌──────┴─────────────────┴─────────────────────┴────────────────────┐
│                    Storage Layer (~/.prep/)                        │
│                                                                    │
│  config.yml    tracker.md    study-plan.md    fitment-analysis.md  │
│  knowledge/    quiz-history.json    schedule.json    content/      │
└───────────────────────────────────────────────────────────────────┘
```

## Package Structure

```
prep_agent/
├── __init__.py              # Version metadata
├── cli.py                   # Click CLI entry point with lazy command loading
│
├── commands/                # CLI command handlers
│   ├── init_cmd.py          # Workspace initialization pipeline
│   ├── today_cmd.py         # Daily schedule display
│   ├── study_cmd.py         # Study session launcher
│   ├── done_cmd.py          # Day completion tracking
│   ├── status_cmd.py        # Progress dashboard
│   ├── quiz_cmd.py          # Quiz runner + AI prompt generator
│   ├── remind_cmd.py        # Reminder management
│   ├── note_cmd.py          # Knowledge base CRUD
│   ├── fitment_cmd.py       # Fitment analysis viewer
│   └── export_cmd.py        # Progress report exporter
│
├── core/                    # Business logic (no external deps beyond stdlib+yaml)
│   ├── config.py            # Config schema, validation, defaults
│   ├── planner.py           # Study plan generation algorithm
│   ├── tracker.py           # Markdown-based progress persistence
│   ├── analyzer.py          # Keyword-based fitment scoring
│   ├── quiz_engine.py       # Local quiz runner + AI prompt builder
│   ├── knowledge.py         # Topic-organized note manager
│   └── templates.py         # Template discovery, loading, validation
│
├── integrations/            # External system interfaces (optional deps)
│   ├── resume_parser.py     # PDF/DOCX/TXT resume extraction
│   ├── job_fetcher.py       # HTTP job posting retrieval
│   ├── scheduler.py         # OS-native cron/launchd scheduling
│   ├── notifier.py          # Cross-platform desktop notifications
│   └── ai_bridge.py         # Provider-agnostic AI integration
│
└── utils/                   # Shared utilities
    ├── display.py           # Rich terminal formatting
    ├── dates.py             # Date arithmetic
    └── file_ops.py          # YAML/JSON/Markdown file I/O
```

## Data Flow

### Initialization (`prep init`)

```
Job URL ──→ JobFetcher ──→ Job Data ──┐
                                      ├──→ FitmentAnalyzer ──→ Gaps ──→ StudyPlanner ──→ Plan
Resume  ──→ ResumeParser ──→ Resume ──┘                                      │
                                                                              ├──→ tracker.md
Template ──→ TemplateLoader ──→ Tracks ──→ (merged into config)              ├──→ study-plan.md
                                                                              ├──→ config.yml
                                                                              └──→ schedule.json
```

### Daily Cycle

```
prep today  ──→ Tracker.load() ──→ find today's entry ──→ display card
prep study  ──→ Tracker.load() ──→ AIBridge (or standalone) ──→ session
prep done   ──→ Tracker.mark_done() ──→ update streak ──→ display progress
prep quiz   ──→ QuizEngine.get_questions() ──→ interactive quiz ──→ log result
```

### Reminder Cycle (OS-level)

```
launchd/cron ──→ prep _notify morning ──→ Notifier.send() ──→ Desktop notification
                                    └──→ reads tracker for contextual message
```

## Key Design Decisions

### 1. Markdown as Database

**Why:** Human-readable, git-friendly, works with any text editor, survives tool changes.

```markdown
# Progress Tracker

| Day | Date       | Topic          | Status | Score | Notes |
|-----|------------|----------------|--------|-------|-------|
| 1   | 2026-04-01 | OWASP LLM #1-5 | done   | 8     | ...   |
| 2   | 2026-04-02 | OWASP LLM #6-10| done   | 7     | ...   |
```

**Trade-off:** Parsing is more fragile than a database. Mitigated by structured generation and defensive parsing.

### 2. Lazy Command Loading

**Why:** A missing or broken command file should never prevent the rest of the CLI from working.

```python
def _lazy_command(module_path, attr):
    try:
        mod = importlib.import_module(module_path)
        return getattr(mod, attr)
    except (ImportError, AttributeError):
        return None  # Skip, don't crash
```

### 3. Optional Dependency Pattern

**Why:** Core tool installs in seconds with 3 deps. Heavy deps (PDF parsing, HTTP) are extras.

```python
def _parse_pdf(self, path):
    try:
        import pdfplumber
        # use it
    except ImportError:
        raise ImportError(
            "PDF parsing requires pdfplumber. "
            "Install with: pip install career-prep-agent[pdf]"
        )
```

### 4. Provider-Agnostic AI

**Why:** AI tools change fast. The bridge pattern decouples prep tracking from any specific AI.

```python
class AIBridge:
    def generate_session(self, topic, tracker_data):
        if self.provider == "claude-code":
            self._update_claude_md(...)  # Write CLAUDE.md
        elif self.provider == "chatgpt-paste":
            return self._build_prompt(...)  # Copy to clipboard
        elif self.provider == "ollama":
            return self._call_local(...)  # API call
        else:
            return self._standalone(...)  # Knowledge pack only
```

### 5. Template System

**Why:** Different career transitions need different study tracks. Templates make it reusable.

```yaml
# templates/cloud-security-lead.yml
tracks:
  - id: "ai-security"
    topics:
      - id: "owasp-llm"
        name: "OWASP LLM Top 10"
        estimated_hours: 6
        priority: critical
        knowledge_pack: "owasp-llm-top10"
        quiz_bank: "owasp-llm-top10"
```

## Dependency Graph

```
Required (3):          Optional (5):
  click >=8.0            pdfplumber >=0.9     [pdf]
  pyyaml >=6.0           python-docx >=0.8    [docx]
  rich >=13.0            httpx >=0.24         [web]
                         beautifulsoup4 >=4.12 [web]
                         pyperclip >=1.8      [clipboard]
```

## Security Considerations

- **No network calls** except explicit `prep init --job-url` (user-initiated)
- **No telemetry** — zero analytics, tracking, or phone-home behavior
- **Local storage only** — all data in `~/.prep/`, never transmitted
- **API keys** (if configured for OpenAI) stored in local config, never logged
- **Reminder scripts** run as the user, no elevated privileges needed

## Agent Architecture (ReAct Pattern)

### The ReAct Loop

Every agent in the system follows the ReAct (Reasoning + Action) pattern:

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│ Observe  │────→│  Reason  │────→│   Act    │────→│ Evaluate │
│ (state)  │     │ (decide) │     │(execute) │     │ (assess) │
└──────────┘     └──────────┘     └──────────┘     └────┬─────┘
                                                        │
                                          ┌─────────────┘
                                          │ Not satisfied?
                                          ▼
                                    Loop back to
                                     Observe
```

This is the fundamental pattern of agentic AI. Unlike a simple function call:
- The agent **observes** its environment before deciding
- The agent **reasons** about what action to take
- The agent **evaluates** whether its action succeeded
- The agent **iterates** if the result isn't satisfactory

### Agent Decomposition

```
                    ┌──────────────┐
                    │ Orchestrator │
                    │  (meta-loop) │
                    └──────┬───────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
     ┌────────┴──┐  ┌─────┴────┐  ┌───┴────────┐
     │  Planner  │  │  Tutor   │  │   Quiz     │
     │  Agent    │  │  Agent   │  │   Agent    │
     │           │  │          │  │            │
     │ Schedule  │  │ Teach &  │  │ Test &     │
     │ Optimize  │  │ Adapt    │  │ Evaluate   │
     └───────────┘  └──────────┘  └────────────┘
              │
     ┌────────┴──┐
     │ Reviewer  │
     │ Agent     │
     │           │
     │ Analyze & │
     │ Recommend │
     └───────────┘
```

### Inter-Agent Communication

Agents communicate via Pydantic models (typed contracts):

```
Orchestrator ──StudySessionRequest──→ TutorAgent
TutorAgent   ──StudySessionResponse──→ Orchestrator
Orchestrator ──QuizResult──→ ReviewerAgent
ReviewerAgent──ReviewReport──→ Orchestrator
```

### Evaluation Loop

The AgentEvaluator monitors all agent decisions:

```
Agent Decision → Structured Log → Metrics Analysis → Reliability Report
                                                          │
Quiz Results → Learning Curve Analysis ──────────────────→│
                                                          │
Test Scenarios → Behavior Validation ───────────────────→│
                                                          ▼
                                                   Evaluation Report
```
