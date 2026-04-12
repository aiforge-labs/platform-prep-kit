# Agentic AI Upgrade Plan

## Goal
Transform career-prep-agent from a CLI tool into a proper AI agent — following the 10-step "How to Build AI Agents from Scratch" framework. Each step is both a code upgrade AND a learning module for agentic AI development.

## What You'll Learn (and be able to explain in interviews)

| Step | Concept | Interview talking point |
|------|---------|----------------------|
| 2 | Pydantic schemas | "I use structured I/O contracts between agent components — type-safe, validated, self-documenting" |
| 3 | MCP Server | "I built an MCP server so any AI tool can interact with the agent using a standard protocol" |
| 4 | ReAct reasoning | "The agent uses a Reason-Act loop — it observes the user's state, decides what to teach, acts, then evaluates" |
| 5 | Multi-agent | "I decomposed the system into specialized agents: Planner, Tutor, Quizzer, Reviewer — each with clear I/O contracts" |
| 6 | Memory/RAG | "The agent maintains session memory and retrieves relevant knowledge using semantic search over study notes" |
| 10 | Evaluation | "I built an evaluation harness that measures study session quality, quiz coverage, and knowledge retention" |

## Architecture: Before vs After

### Before (CLI Tool)
```
User → CLI Command → Function → Output
```

### After (AI Agent)
```
User → CLI/MCP → Orchestrator → [Planner Agent, Tutor Agent, Quiz Agent, Reviewer Agent]
                      ↕                    ↕
                  Memory Store      Knowledge Base (RAG)
                      ↕
                  Evaluation Loop
```

## Implementation Plan (6 upgrades)

### Upgrade 1: Pydantic Schemas (Step 2)
- Replace dict-passing with Pydantic models
- Models: StudyPlan, DayEntry, QuizResult, FitmentReport, TrackerState, Config
- Self-documenting, validated, serializable
- **Learning:** How agents communicate with structured contracts

### Upgrade 2: ReAct Study Agent (Step 4)
- A reasoning loop that decides what to teach and how
- Observe: read tracker state, quiz history, knowledge gaps
- Reason: decide optimal next topic, difficulty, approach
- Act: generate study content, quiz, or review
- Evaluate: check if learning objectives were met
- **Learning:** ReAct pattern — the core of agentic reasoning

### Upgrade 3: Multi-Agent Orchestration (Step 5)
- Decompose into 4 specialized agents:
  - **Planner Agent** — generates/adjusts study plans based on progress
  - **Tutor Agent** — teaches concepts, adapts to user's level
  - **Quiz Agent** — generates questions, evaluates answers, tracks mastery
  - **Reviewer Agent** — analyzes progress, suggests adjustments, identifies weak areas
- Orchestrator coordinates them based on session type
- **Learning:** Agent decomposition, message passing, coordination

### Upgrade 4: MCP Server (Step 3)
- Expose agent capabilities as MCP tools
- Any AI (Claude, GPT, etc.) can call prep agent functions
- Tools: get_today, start_study, take_quiz, add_note, get_progress
- **Learning:** Model Context Protocol — the standard for AI tool interop

### Upgrade 5: Memory & RAG (Step 6)
- Session memory: what was discussed, what clicked, what didn't
- Knowledge retrieval: semantic search over study notes + knowledge packs
- Lightweight: use TF-IDF or simple embeddings, no heavy vector DB
- **Learning:** How agents maintain context across sessions

### Upgrade 6: Evaluation Harness (Step 10)
- Test prompts: predefined scenarios to validate agent behavior
- Metrics: quiz score trends, knowledge coverage, session quality
- Logs: structured logging of all agent decisions
- **Learning:** How to measure and improve agent reliability
