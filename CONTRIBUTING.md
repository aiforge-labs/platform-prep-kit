# Contributing to Platform Prep Kit

Thank you for your interest in contributing! This guide will help you get started.

## Development Setup

```bash
# Clone the repo
git clone https://github.com/aiforge-labs/platform-prep-kit.git
cd platform-prep-kit

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install in development mode with all extras
pip install -e ".[all,dev]"

# Run tests
pytest

# Run the CLI
prep --version
```

## Project Structure

```
prep_agent/
├── cli.py                  # CLI entry point — register new commands here
├── commands/               # One Click command per file
│   ├── init_cmd.py
│   ├── study_cmd.py
│   ├── quiz_cmd.py
│   ├── serve_cmd.py        # Web UI launcher
│   └── ...
├── agents/                 # ReAct agents (Planner, Tutor, Quiz, Reviewer, Orchestrator)
├── core/                   # Business logic (shared by CLI + web)
│   ├── config.py           # Configuration management
│   ├── planner.py          # Study plan generation
│   ├── tracker.py          # Progress tracking (markdown)
│   ├── analyzer.py         # Fitment analysis
│   ├── quiz_engine.py      # Quiz system
│   ├── knowledge.py        # Knowledge base
│   └── templates.py        # Template loading
├── web/                    # Self-hosted web UI (FastAPI + HTMX)
│   ├── app.py              # FastAPI application factory
│   ├── database.py         # SQLite schema and connection management
│   ├── migrate.py          # Markdown <-> SQLite bidirectional sync
│   ├── services.py         # Service layer (bridges routes to core modules)
│   ├── csrf.py             # CSRF protection middleware
│   ├── server.py           # Uvicorn launcher
│   ├── routes/             # FastAPI routers (dashboard, study, quiz, etc.)
│   ├── templates/          # Jinja2 HTML templates
│   └── static/             # CSS, JS, vendored HTMX
├── integrations/           # External integrations
│   ├── scheduler.py        # OS reminders
│   ├── notifier.py         # Desktop notifications
│   ├── job_fetcher.py      # Job URL parsing
│   ├── resume_parser.py    # Resume parsing
│   └── ai_bridge.py        # AI provider integration
└── utils/                  # Shared utilities

templates/                  # Role template YAML files
knowledge_packs/            # Bundled markdown study guides
quiz_banks/                 # JSON question banks
.github/                    # CI/CD workflows, issue/PR templates
```

## Ways to Contribute

### Adding a Role Template

Templates live in `templates/` as YAML files. See existing templates for the format.

1. Create `templates/your-role.yml`
2. Follow the schema in `templates/_schema.yml`
3. Include: tracks with topics, resources, interview questions, `bridge_from` entries
4. Validate: `prep template validate templates/your-role.yml`
5. Test end-to-end: `prep init --template your-role`
6. Submit a PR

**`bridge_from` key rules** — use only these canonical role slugs:

| Slug | Covers |
|------|--------|
| `software_engineering` | General software / application engineering |
| `backend_engineering` | Backend / API / server-side focus |
| `cloud_engineering` | Cloud infrastructure and services |
| `devops_sre` | DevOps, SRE, platform ops (also matches `devops_engineer`) |
| `infrastructure_engineering` | On-prem or hybrid infra |
| `system_administration` | Sysadmin / Linux / Windows ops |
| `security_engineering` | General application or product security |
| `cloud_security` | Cloud-native security and posture management |
| `penetration_testing` | Offensive security / red team |
| `network_security` | Network and perimeter security |
| `security_operations` | SOC, incident response, threat hunting |
| `ml_engineering` | ML model training, pipelines, MLOps |
| `data_engineering` | Data pipelines, warehouses, ETL |
| `data_scientist` | Modelling, experimentation, analytics |
| `audit_compliance` | GRC, audit, compliance programs |
| `customer_success` | CSM, account management |
| `technical_support` | Technical support / escalation engineering |
| `network_engineering` | Network design and operations |
| `web_development` | Frontend / fullstack web |

Using a non-canonical key will still work but will reduce `prep pivot` coverage.

### Adding a Knowledge Pack

Knowledge packs are markdown study guides in `knowledge_packs/`.

1. Create `knowledge_packs/your-topic.md`
2. Include: overview, key concepts, examples, self-test questions, resources
3. Keep it educational and practical
4. Submit a PR

### Adding Quiz Questions

Quiz banks are JSON files in `quiz_banks/`. Each bank must follow this schema:

```json
{
  "topic_id": "your-topic",
  "title": "Your Topic Title",
  "version": 1,
  "questions": [
    {
      "id": "q01",
      "question": "Which approach is best for X?",
      "type": "multiple_choice",
      "options": ["A) Option 1", "B) Option 2", "C) Option 3", "D) Option 4"],
      "answer": "B",
      "explanation": "Why B is correct.",
      "difficulty": "medium"
    },
    {
      "id": "q02",
      "question": "Explain concept Y and its tradeoffs.",
      "type": "open",
      "key_points": ["Key point 1", "Key point 2", "Key point 3"],
      "difficulty": "hard"
    }
  ]
}
```

**Required fields:**
- MC questions: `id`, `question`, `type`, `options` (4 items, A-D prefix), `answer` (A/B/C/D), `difficulty`
- Open questions: `id`, `question`, `type`, `key_points` (non-empty), `difficulty`
- Difficulty must be one of: `easy`, `medium`, `hard`

**Steps:**
1. Create `quiz_banks/your-topic.json`
2. Validate: `prep quiz --import-file quiz_banks/your-topic.json`
3. Test: `prep quiz --topic your-topic`
4. Submit a PR

You can also generate a starting bank with AI: `prep quiz --generate --topic "your topic" --num 10`

### Bug Fixes and Features

1. Check existing issues first
2. Create an issue describing the bug/feature
3. Fork, branch, implement, test
4. Submit a PR referencing the issue

## Pull Request Process

1. **Fork the repo** and create a feature branch from `main`
2. **Make your changes** — keep PRs focused on a single concern
3. **Run tests** before submitting: `make test` or `pytest tests/ -v`
4. **Submit a PR** using the PR template — fill in all sections
5. **Wait for review** — at least one maintainer approval is required before merge
6. **CI must pass** — automated tests run on every PR (Python 3.10, 3.11, 3.12)

### Branch Protection

The `main` branch has these protections enabled:
- Pull request reviews required before merging
- Status checks (CI tests) must pass
- Branch must be up to date before merging
- Direct pushes to `main` are not allowed

## Security Guidelines

**These are critical for all contributions:**

1. **Never use `eval()`, `exec()`, or `os.system()` with user input**
2. **Always use parameterized queries** for SQLite — never string formatting/f-strings
3. **Sanitize file paths** — use `pathlib`, reject path traversal (`..`)
4. **Never commit secrets** — no API keys, passwords, tokens, or `.env` files
5. **Escape HTML output** — Jinja2 autoescaping is on; never use `|safe` on user-provided content
6. **Validate inputs server-side** — don't trust client-side validation alone
7. **No external network calls** without explicit user intent

See [SECURITY.md](SECURITY.md) for the full security policy and vulnerability reporting.

## Code Guidelines

- **Python 3.10+** with type hints
- **No proprietary data** — zero company names, client references, or personal data in code
- **Graceful degradation** — optional deps fail with helpful messages, not crashes
- **Privacy first** — no telemetry, no external calls without user intent
- **Tests** — add tests for new features (`pytest`)
- **CLI output** — use `rich` for formatted output, `click.echo` for plain
- **Web UI** — use FastAPI routers for new pages, Jinja2 templates, HTMX for interactivity

## Privacy Rules

These are non-negotiable:

1. The codebase must contain **zero** references to specific companies, clients, or individuals
2. All examples use generic placeholders ("Acme Corp", "Jane Doe")
3. No telemetry, analytics, or data collection of any kind
4. User data stays in `~/.prep/` and is never transmitted
5. Optional dependencies must fail gracefully with install instructions

## Running Tests

```bash
# Using Makefile (recommended)
make test           # All tests
make test-cov       # With coverage
make lint           # Syntax checks
make check-secrets  # Scan for leaked secrets

# Or directly
pytest tests/ -v
pytest tests/test_planner.py     # Specific file
```

## Commit Messages

Use conventional commits:
- `feat: add new quiz bank for kubernetes security`
- `fix: handle missing resume file gracefully`
- `docs: add guide for creating custom templates`
- `template: add platform-engineer role template`
- `knowledge: add AWS security fundamentals pack`
- `web: add portfolio detail page`
