# AI Integration Guide

Platform Prep Kit works **100% without AI**. AI is an optional enhancer for interactive study sessions, quizzes, and content creation.

## Supported Providers

| Provider | Cost | Best For |
|----------|------|----------|
| **None** | Free | Self-directed learners who prefer reading/self-testing |
| **Ollama** | Free | Privacy-focused users who want AI locally |
| **ChatGPT (paste)** | Free/Paid | Users who already have ChatGPT open |
| **Claude Code** | Paid | The richest experience — auto-resume sessions |
| **OpenAI API** | Paid | Developers who want API integration |

## Setup

```bash
# Set provider
prep config --ai-provider <provider-name>

# Options:
prep config --ai-provider none           # Default — no AI
prep config --ai-provider ollama          # Local LLM
prep config --ai-provider chatgpt-paste   # Copy-paste prompts
prep config --ai-provider claude-code     # Claude Code integration
prep config --ai-provider openai-api      # OpenAI API
```

## Provider Details

### None (Default)

No AI required. Uses:
- Built-in knowledge packs for study material
- Local quiz banks for self-testing
- Markdown-based study guides
- Manual knowledge note-taking

### Ollama (Free, Local)

Run AI models locally on your machine.

**Setup:**
1. Install Ollama: https://ollama.ai
2. Pull a model: `ollama pull llama3`
3. Configure: `prep config --ai-provider ollama`

**Usage:**
```bash
prep study --with-ai    # Sends topic to local Ollama
prep quiz --with-ai     # AI-generated quiz via Ollama
```

### ChatGPT / Any AI Chat (Copy-Paste)

Generates prompts you paste into any AI chat.

**Setup:**
```bash
prep config --ai-provider chatgpt-paste
```

**Usage:**
```bash
prep study --with-ai    # Copies study prompt to clipboard
# Paste into ChatGPT, Claude.ai, Gemini, etc.

prep quiz --mock-interview --copy
# Copies mock interview prompt to clipboard
```

### Claude Code (Richest Experience)

Auto-generates instruction files that Claude Code reads.

**Setup:**
```bash
prep config --ai-provider claude-code
```

**Usage:**
```bash
# In any Claude Code session:
> continue my prep

# Claude reads ~/.prep/ files and:
# 1. Knows your current day/topic
# 2. Teaches the scheduled concepts
# 3. Quizzes you
# 4. Updates your tracker
```

**How it works:** The agent generates a `CLAUDE.md` file at `~/.prep/.ai/claude-code/CLAUDE.md` with:
- Your current progress state
- Today's topic and schedule
- Session format instructions
- Knowledge base references

### OpenAI API

Direct API integration for programmatic AI sessions.

**Setup:**
```bash
prep config --ai-provider openai-api --api-key sk-...
```

**Note:** API key is stored locally in `~/.prep/config.yml`. Never committed to any repo.

## What AI Adds

| Feature | Without AI | With AI |
|---------|-----------|---------|
| Study material | Built-in knowledge packs | + AI-generated explanations tailored to your background |
| Quizzes | Pre-built question banks | + Dynamic AI-generated questions |
| Mock interviews | Question list for self-practice | + Interactive mock interview with feedback |
| Content creation | Manual writing | + AI-assisted blog drafts, threat models |
| Session tracking | Manual `prep done` | + Auto-update tracker after AI sessions |
