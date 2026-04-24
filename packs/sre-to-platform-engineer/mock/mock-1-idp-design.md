# Mock 1 — Design an Internal Developer Platform

**Scored mock exercise · 60 minutes · Week 11**

> **Terms used in this mock**
> - **IDP** — Internal Developer Platform
> - **SRE** — Site Reliability Engineer
> - **Platform Engineer** — the role you're transitioning to
> - **MVP** — Minimum Viable Product; used here as "minimum viable platform"
> - **Paved path / Golden path** — the opinionated, well-supported way
> - **GitOps** — Week 5 framework: Git as source of truth, pull-based reconciliation
> - **Multi-tenancy** — multiple teams / apps / environments sharing a platform (Week 9)
> - **Blast radius** — the set of tenants affected by a single failure
> - **Scaffolder** — a tool that generates a new service from a template
> - **SLI / SLO** — Service Level Indicator / Objective (Week 10)
>
> Full definitions and equivalent titles in the [pack README](../README.md#what-we-mean-by-sre).

This mock simulates the classic 60-minute open-ended platform system design interview. Expect similar prompts in real loops from large and mid-sized companies with a platform-engineering function.

Rubric: [`../rubrics/rubric-1-idp-design.md`](../rubrics/rubric-1-idp-design.md) — read **before** attempting.

---

## Setup

You have joined a mid-sized company as the first Platform Engineer. The profile:

- **Company:** B2B SaaS, 5 years old
- **Engineering org:** 200 engineers, 30 product teams, 1 central SRE team of 5
- **Infrastructure:** multi-cloud (primarily one provider, secondary on another), Kubernetes-based
- **Current state:** no platform team; every product team builds and operates its own services with help from the SRE team when things go wrong
- **Leadership mandate:** "build a platform that makes our engineers more productive"
- **Budget:** one more hire in 6 months (you + 1)
- **Timeline:** first demonstrable value in 90 days

**Interviewer prompt:** *"Design the platform. Tell me how you'd think about it, what you'd build first, and how you'd know it's working."*

You have 60 minutes. Expect 2–3 clarifying-question rounds and 1–2 follow-up prompts ("What if you had 10x the scale?", "What would you change if the budget was tighter?").

---

## How to run this mock

### Solo variant

1. Set a timer for 60 minutes.
2. Treat the setup above as the interviewer's opening prompt.
3. Speak aloud (or write) your answer, working through the structure in real time.
4. Stop at 60 minutes regardless of where you are — real interviews do.
5. Score using the rubric. Honest scoring is more valuable than optimistic scoring.

### With a practice partner

- Share the setup with the partner.
- Have them read the "interviewer notes" section below.
- Run the full 60-minute loop with clarifying questions and follow-ups.
- Partner scores using the rubric; you score yourself; compare.

### After the mock

- Score against the rubric.
- If average is below 3.0, schedule a re-run *at least 48 hours later*. Cold re-runs reveal more than hot ones.
- Note your weakest criterion — this is your highest-priority Week 11 focus area.

---

## Suggested structure (for the candidate)

You are not required to use this, but the top-scoring answers typically follow roughly this shape:

### 0–10 min: Clarify

Ask 4–6 questions before designing. High-value ones:

- What does "productivity" actually mean — are there signals leadership is watching?
- What are engineers *currently* complaining about? Top 3 pain points?
- How opinionated does the platform need to be? Is standardization a goal, or is team autonomy sacred?
- What's the compliance / regulatory context?
- Are there existing tools we'd displace, or are we greenfield?
- What's the success metric at 90 days? At 1 year?

Make these real questions, not performative ones. Listen to the answers and let them shape the design.

### 10–20 min: Users, requirements, MVP scope

Name the users (30 product teams, ~200 engineers), the sub-personas (team leads, senior ICs, on-call engineers, new hires), and the jobs-to-be-done (create a new service, deploy a change, debug a failing service, onboard a new hire).

Pick 3–5 capabilities for the 90-day MVP. Candidates to reach for:

- Deploy pipeline + GitOps reconciliation
- Service scaffolder with opinionated defaults
- Observability baseline (logs, metrics, generated dashboards, alerts from SLO templates)
- Catalog (ownership + metadata)
- A thin, well-documented "golden path"

Deliberately *defer*:

- A portal (Backstage or similar) — too early
- Full policy-as-code program — Week 6 material, but for the first 90 days it's audit-mode only
- Multi-cluster strategy — you have one cluster per env; keep it there
- Secrets management — use the cloud provider's native service, don't build
- FinOps — start with visibility only

### 20–40 min: Design

Sketch the architecture. Expected depth:

- The GitOps controller choice (Argo or Flux) with one sentence on why
- The scaffolder (a simple templating tool + catalog registration) with one sentence on why not Backstage yet
- The observability stack (OpenTelemetry Collector + Prometheus + Loki + Grafana, or equivalent OSS) with per-tenant visibility noted
- The catalog (one `catalog-info.yaml` per service repo, a simple indexer, no portal UI yet)
- The policy story (audit-mode Kyverno or Conftest for the top 3 rules — requires/limits, image registry, owner label)
- The CI (GitHub Actions or equivalent; do not reinvent)

Name what you are *not* solving: secrets service (use cloud), cost-attribution deep-dive (observability gives visibility, attribution is phase 2), Backstage portal (phase 2), multi-cluster (phase 3), ML-specific workflows (phase 3).

### 40–50 min: Reliability, scale, trust

Expected to address at least briefly:

- Platform SLIs: deploy success rate, scaffolder time-to-first-deploy, observability ingestion lag
- Error-budget policy for the platform team
- What happens if the GitOps controller fails — failure mode + runbook
- Multi-tenancy model — soft (namespace-per-team) is appropriate at this scale
- Cardinality/cost controls — per-tenant observability budget
- How you'd know the platform is "working" — team adoption %, time-to-first-deploy, DevEx survey

### 50–60 min: Trade-offs, open questions, what you'd do differently

Expected to surface:

- The decision to defer a portal; what signal would tell you it's time
- The decision to go multi-cloud-lite vs cloud-native; consequences
- The decision to start with audit-mode policy; when to switch to enforce
- The risks in the 90-day plan; what you'd de-scope if behind
- The hardest stakeholder conversation you expect

---

## Interviewer notes (for a practice partner)

When running this mock with a partner, the partner should:

### Set the scene

Read the setup aloud. Let the candidate ask questions. Answer reasonably; don't volunteer information.

### Push back

Pick 1–2 of these to introduce during the session:

- "Leadership actually wants this in 30 days, not 90. What do you cut?"
- "What if the compliance team says everything has to be in one cloud, no multi-cloud?"
- "A staff engineer on a product team is strongly against GitOps — she thinks it'll slow her team down. What do you do?"
- "Budget just got cut. You're still solo, no second hire. What changes?"
- "What if the scaffolder is wildly successful and 200 services get created in the first year — how does your design hold up?"

These are common real-interview disruptions. The candidate's handling of them reveals more than the base design.

### Ask a follow-up

Around minute 45, ask one of:

- "Tell me more about the observability stack — specifically, how do you prevent one team's cardinality from hurting another team?"
- "Let's go deep on the scaffolder. What's in the template, what's a parameter, what does it produce?"
- "Walk me through onboarding a new product team to your platform. Minute by minute."

### Score with the rubric

Use [`../rubrics/rubric-1-idp-design.md`](../rubrics/rubric-1-idp-design.md). Compare with candidate's self-score.

---

## Notes for your own future self

After completing this mock, write 3–4 sentences on:

1. What you did well this run
2. What you'd do differently next run
3. The one criterion you want to improve most
4. The open question you couldn't answer well and want to prep for

Keep these notes — they compound across multiple mock runs.
