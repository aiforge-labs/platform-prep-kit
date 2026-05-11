# Rubric — Mock 1: IDP Design

**Scoring rubric for [`../mock/mock-1-idp-design.md`](../mock/mock-1-idp-design.md)**

> **Terms used in this rubric**
> - **IDP** — Internal Developer Platform
> - **MVP** — Minimum Viable Product / Platform
> - **SLI / SLO** — Service Level Indicator / Objective (Week 10)
> - **Trade-off** — inherent cost of a design choice
> - **Golden path** — opinionated, well-supported way (Week 1)
> - **Staff-level signal** — the depth and breadth of thinking expected at senior/staff platform engineer level
>
> Full definitions and equivalent titles in the [pack README](../README.md#what-we-mean-by-sre).

This rubric is used to score the 60-minute IDP design mock. Seven criteria, scored 1–4.

Use this rubric **before** attempting the mock (know what's being scored), **during** the mock (if you have a peer evaluator), and **after** (for self-assessment).

---

## Scoring scale

- **1** — Did not address, or addressed incorrectly (SRE-frame / tool-first)
- **2** — Addressed superficially; missed the platform-engineering framing
- **3** — Addressed well; platform-engineering framing clear
- **4** — Addressed with depth; articulated trade-offs; staff-level signal

**Score interpretation:**

- Average ≥ 3.5 — ready for senior/staff platform interviews
- Average 3.0–3.4 — close; identify weakest criteria, do a cold re-run after 48 hours
- Average < 3.0 — more prep needed; revisit Weeks 4, 7, 10 before re-running

---

## Criteria

### 1. Clarifying questions before designing (weight: high)

The candidate opened with clarifying questions before diving into design.

- **1** — Launched into design from minute 0
- **2** — Asked 1–2 questions but clearly wanted to get to the design
- **3** — Asked 4–6 thoughtful questions covering users, constraints, and success metrics; listened to answers
- **4** — Above, plus used answers to reshape the design visibly (e.g., "based on what you said about compliance, I'm going to add…")

Self-assessment: which questions did you ask? Did any of your questions reveal senior-level thinking (e.g., about team autonomy vs standardization, or about the success metric leadership is actually watching)?

### 2. Users and user problems named, not just roles

The candidate described the platform's users with specificity — not "developers" generically, but sub-personas (team leads, senior ICs, on-call engineers, new hires) with different jobs-to-be-done.

- **1** — "We'll serve the product teams."
- **2** — Named the user groups but not their specific pain points
- **3** — Named sub-personas and 2–4 concrete jobs-to-be-done
- **4** — Above, plus explicitly identified a non-user (a team the platform will NOT serve), with a reason

### 3. MVP scope and sequencing

The candidate proposed an MVP before the mature state — 3–5 capabilities that can ship in 90 days.

- **1** — Proposed a mature platform from the start (Backstage + Argo + Crossplane + OPA + Grafana + Kyverno + everything)
- **2** — Mentioned MVP but scoped it too broadly (8–10 capabilities)
- **3** — Named 3–5 MVP capabilities with a clear 90-day delivery plan
- **4** — Above, plus deliberately deferred 2+ capabilities with a specific signal that would justify building them later

### 4. Trade-offs and non-goals made explicit

The candidate named trade-offs throughout the design, not just "pros and cons" at the end. Every significant choice has a named cost.

- **1** — Listed features, no trade-offs
- **2** — Named trade-offs at the end only
- **3** — Surfaced trade-offs as they came up; named at least 3 non-goals with reasons
- **4** — Above, plus acknowledged a trade-off the candidate themselves is uncomfortable with (and why the candidate accepted it anyway)

### 5. Multi-tenancy, cost, and observability addressed

The candidate addressed per-tenant isolation, cost visibility, and the observability story (Weeks 8, 9) — not just the happy path.

- **1** — One or more of multi-tenancy, cost, or observability not mentioned
- **2** — Mentioned but hand-waved
- **3** — Specific approach for each: per-tenant quota, per-tenant observability budget, showback plan
- **4** — Above, plus explicit blast-radius / isolation thinking (e.g., "if one tenant's policy is bad, I don't want it to affect the other 39")

### 6. Platform reliability and operations

The candidate defined platform SLIs and at least sketched how the platform team operates the platform (on-call, error-budget, incident response).

- **1** — Discussed only the platform's functionality, not its operations
- **2** — Mentioned SLOs generically
- **3** — Named specific platform SLIs (deploy success rate, template latency, etc.) with a target
- **4** — Above, plus an error-budget policy with real consequences for the platform team's roadmap

### 7. Execution and communication

The candidate structured the conversation, managed time, and communicated decisions clearly.

- **1** — Disorganized; ran out of time; key decisions unclear
- **2** — Had structure but occasionally lost thread; ended rushed
- **3** — Named a structure at the start, stuck to it, ended on time with a clear summary
- **4** — Above, plus responded to interviewer push-back gracefully — changed the design or explained the trade-off, didn't defend reflexively

---

## Overall score

Sum the 7 criteria scores (max 28). Divide by 7 for average.

- **3.5+ (24.5+)** — Strong. Ready for real interviews. Continue to Mock 2 and Mock 3.
- **3.0–3.4 (21–24)** — Close. Identify weakest criterion. Do a cold re-run after 48 hours.
- **< 3.0 (< 21)** — Re-prep needed. Focus on weakest 2 criteria. Specifically consider re-reading Weeks 4, 7, 10 before re-running.

---

## Follow-up

Write 3–4 sentences after scoring:

1. What was my strongest criterion?
2. What was my weakest?
3. What would I do differently next run?
4. If I had a 10-minute prep window before a real interview, what would I review?

Keep these notes for the pattern analysis you'll do at end of Week 11.

---

## Calibration note

If this is your first mock: expect to score 2.5–3.0 on first attempt, regardless of experience. Mocks are about the *execution*, and execution improves with reps even when the material is already known. A score of 2.8 on first attempt is not a signal to panic; it's a signal that you should do the second and third mock, then a cold re-run of Mock 1, and expect to improve.

If your score doesn't improve after a cold re-run, the issue is not execution — it's a content gap. Re-read the weakest criterion's corresponding week and try again.
