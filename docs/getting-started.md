# Getting Started

## Installation

```bash
pip install platform-prep-kit
```

For full features:
```bash
pip install platform-prep-kit[all]
```

## Quick Start: From a Job Posting

The fastest way to get started is with a job URL and your resume:

```bash
prep init --job-url "https://careers.example.com/jobs/12345" --resume ~/resume.pdf
```

The agent will:
1. Fetch and analyze the job posting
2. Parse your resume
3. Run a fitment analysis (strengths vs gaps)
4. Generate a personalized study plan
5. Set up daily desktop reminders
6. Create your workspace at `~/.prep/`

## Quick Start: From a Template

If you don't have a specific job posting yet:

```bash
prep init --template cloud-security-lead
```

Available templates:
- `cloud-security-lead` — Cloud/AI Security Leadership
- `cloud-solutions-architect` — Solutions Architect
- `devsecops-engineer` — DevSecOps Engineer
- `custom` — Blank template for any role

## Quick Start: Interactive

For a guided setup:

```bash
prep init --interactive
```

## Daily Workflow

### Morning
```bash
# Check today's plan
prep today

# Start studying
prep study
```

### Evening
```bash
# Continue with evening session
prep study

# Take a quiz to test understanding
prep quiz

# Mark the day complete
prep done --notes "Key takeaway: prompt injection has two types" --score 8
```

### Weekly
```bash
# Check overall progress
prep status

# Review weak areas
prep quiz --topic "areas you struggled with"
```

## Adding AI (Optional)

### Claude Code
```bash
prep config --ai-provider claude-code
# Then in Claude Code: "continue my prep"
```

### ChatGPT / Any AI Chat
```bash
prep study --with-ai
# Copies a study prompt to your clipboard — paste into any AI
```

### Local AI (Ollama)
```bash
prep config --ai-provider ollama
prep study --with-ai
```

## Managing Reminders

```bash
prep remind status          # Check schedule
prep remind set 07:00 20:00 # Change times
prep remind pause           # Pause temporarily
prep remind resume          # Resume
prep remind skip            # Skip just today
```

## Building Your Knowledge Base

```bash
# Add notes as you study
prep note add "OWASP LLM" "Key insight: prompt injection is like SQL injection for LLMs"

# Review later
prep note show "OWASP LLM"

# Search across all notes
prep note search "injection"
```

## Exporting Progress

```bash
prep export --format md --output ~/my-progress.md
prep export --format json --output ~/my-progress.json
```
