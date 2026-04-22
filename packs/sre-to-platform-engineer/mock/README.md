# Mock Exercises

3 scored mock exercises for Week 11 of the plan. Content will be populated in milestone 1.5.

---

## Why three, and why these

Platform engineer interviews typically include one or more of:

1. **Open-ended system design** — "design an internal developer platform for a 200-engineer company"
2. **Design review / critique** — "here's an IaC repo structure; what's wrong with it?"
3. **Operational scenario** — "your deploy platform is degraded for 6 hours — walk me through response, comms, and postmortem"

These three mocks are shaped to mirror those three interview styles, not to test knowledge of specific tools.

## Planned exercises (placeholders)

### Mock 1: Design an Internal Developer Platform

**Setup**
- Mid-sized org (200 engineers, 30 teams, multi-cloud)
- 60-minute design exercise
- You have no existing platform; you're the first platform hire

**Evaluation criteria** (see [`../rubrics/`](../rubrics/) when content lands)
- Did you ask about users/constraints before designing?
- Did you propose an MVP before a mature state?
- Did you make adoption and migration strategy explicit?
- Did you explain trade-offs, not just choices?

Content pending milestone 1.5.

### Mock 2: IaC Review and Redesign

**Setup**
- You're given a Terraform + Kubernetes + CI/CD repository
- 45 minutes to review and propose changes
- The repo has realistic problems — not obvious bugs, structural issues

**Evaluation criteria** (see [`../rubrics/`](../rubrics/) when content lands)
- Did you ask what the platform's users experience, not just what the code does?
- Did you identify governance/policy gaps, not just code smells?
- Did you sequence your changes by blast radius and ROI?
- Did you distinguish "wrong" from "outdated" from "acceptable trade-off"?

Content pending milestone 1.5.

### Mock 3: Platform Incident Response

**Setup**
- You are the on-call platform engineer
- Your deploy pipeline is degraded — 30% of deploys are hanging
- Multiple product teams are escalating
- You have no rollback for the change that caused it
- 45 minutes to walk through response, comms, mitigation, postmortem framing

**Evaluation criteria** (see [`../rubrics/`](../rubrics/) when content lands)
- Did you separate mitigation from root cause?
- Did you manage stakeholder comms proactively, not reactively?
- Did you think about platform tenants, not just the platform itself?
- Did you surface actionable lessons, not generic ones?

Content pending milestone 1.5.

---

## How to use mocks

**Solo:** write out your answer as you would speak it (30–40 minutes), then score against the rubric. Wait 48 hours, then re-read — you'll see gaps more clearly with a cold read.

**With a peer:** share the setup, have them play interviewer, do it live. Best format if you can find a practice partner at a similar level.

**With an AI assistant:** use [`prep`](../../../README.md) in interactive mode to simulate an interviewer. The tool can prompt you, push back, and score with the rubric — but its feedback is supplementary, not definitive. The rubric is the authority.

## Placeholder

Content pending milestone 1.5.
