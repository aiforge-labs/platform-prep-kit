# Week 11: System Design Interview Deep-Dive

**Phase 4 — Leadership, Interviews, Closing**

> **Terms used in this week**
> - **SRE** — Site Reliability Engineer
> - **Platform Engineer** — the role you're transitioning to
> - **System design interview** — an open-ended whiteboard-style interview where you design a system or platform component under time pressure (usually 45–75 minutes)
> - **IDP** — Internal Developer Platform
> - **MVP** — Minimum Viable Product
> - **GitOps** — Week 5 — Git as source of truth, pull-based reconciliation
> - **SLI / SLO** — Service Level Indicator / Objective (Week 10)
> - **Blast radius** — the set of tenants affected by a failure (Week 9, 10)
> - **Tenant** — a team, app, or environment consuming the platform
> - **Mock** — a full practice interview with scoring; this pack includes three (see [`../mock/`](../mock/))
>
> Full definitions and equivalent titles in the [pack README](../README.md#what-we-mean-by-sre).

Week 11 is the single most important week of the pack for interview outcomes. Every platform engineer interview loop includes at least one system design round. Senior loops often include two. Candidates fail these rounds not because they don't know the content — they fail because they can't *execute* a design conversation in 45 minutes under pressure.

This week is about execution: structure, pacing, questions-first, trade-offs-in-real-time. The content you already have from Weeks 1–10 is enough. What's missing is reps.

---

## Time commitment

~6–8 hours, front-loaded onto the mocks:

- Read: 45 minutes
- Apply (run three full mocks): 5–6 hours (including post-mock review)
- Articulate (meta-reflection on your pattern): 30 minutes
- Self-assess: 30 minutes

## Learning objectives

By end of week you should be able to:

1. Use a consistent, named structure for every platform system-design conversation — so you never lose orientation mid-interview
2. Open a design conversation with 4–6 clarifying questions that reveal senior judgment
3. Size, sequence, and articulate trade-offs in real time
4. Know your own failure modes under interview pressure (your "tell" when you're getting nervous)
5. Identify 3–5 design patterns you reach for reliably (GitOps for deploys, per-tenant quota for isolation, catalog as truth source, opinionated templates with escape hatches, policy-as-code as guardrail)

---

## Read (45 minutes)

### Required

**1. Interview execution structure — pick and adopt one**

There are several structures commonly used for platform/infrastructure system design interviews. Adopt one explicitly; don't improvise. Common ones:

- **Clarify → Scope → Design → Scale → Trust** (a platform-adapted version of the classic 5-step system-design template)
- **Users → Requirements → MVP → Scale → Reliability → Trade-offs** (the IDP-specific extension)
- **4Rs**: Requirements, Rough sketch, Refine, Review

Pick one. Commit. Use the same one in every mock this week so it becomes automatic.

**2. Pack review — skim your own notes from Weeks 1–10**

- 15–20 minutes.
- You are not learning new material this week. You are indexing what you already know so you can reach for it fast. Make a single-page cheat-sheet: your go-to design patterns, your 5 favorite SLIs, your 2 or 3 favorite anti-patterns to call out, the architecture diagram you could draw in 60 seconds.

**3. In-repo reference — mock setups and rubrics**

- [`../mock/README.md`](../mock/README.md) and [`../rubrics/README.md`](../rubrics/README.md), plus the three mock files and their rubrics.
- 15 minutes. Know the rubric *before* you run the mocks. The rubric is how you'll score yourself; mock is useless if you didn't score against the criteria you care about.

### Why only 45 minutes of reading

Reading is not the limiting factor at this point. Reps under something close to interview pressure are. Don't let reading become a procrastination signal.

---

## Apply (5–6 hours) — Run the Three Mocks

The mocks are the heart of this week. Each is designed to be done *under time pressure* — even if you are alone with a notebook.

### Mock 1 — Design an Internal Developer Platform

- Setup, constraints, and scoring: [`../mock/mock-1-idp-design.md`](../mock/mock-1-idp-design.md)
- Rubric: [`../rubrics/rubric-1-idp-design.md`](../rubrics/rubric-1-idp-design.md)
- Time: 60 minutes, strict. Use a timer.

After the mock, give yourself 30 minutes to score against the rubric and take notes on:

- Did you ask clarifying questions before designing?
- Did you propose an MVP before the mature state?
- Did you name trade-offs?
- What was your weakest criterion?

### Mock 2 — IaC Review and Redesign

- Setup: [`../mock/mock-2-iac-review.md`](../mock/mock-2-iac-review.md)
- Rubric: [`../rubrics/rubric-2-iac-review.md`](../rubrics/rubric-2-iac-review.md)
- Time: 45 minutes.

Post-mock review: 30 minutes. Focus especially on:

- Did you distinguish wrong from outdated from acceptable-trade-off?
- Did you sequence changes by blast radius, not by what's interesting?

### Mock 3 — Platform Incident Response

- Setup: [`../mock/mock-3-platform-incident.md`](../mock/mock-3-platform-incident.md)
- Rubric: [`../rubrics/rubric-3-platform-incident.md`](../rubrics/rubric-3-platform-incident.md)
- Time: 45 minutes.

Post-mock review: 30 minutes. Focus especially on:

- Was your comms proactive, or did you handle mitigation first and comms later?
- Did you distinguish "the team that triggered it" from "the platform that allowed it"?

### If you have a practice partner

Strong option: have a colleague or peer act as the interviewer. They set the scene, push back, and ask clarifying questions you wouldn't ask yourself. Recommended for at least one of the three mocks if you can find a partner at a similar level.

### Solo variant — what to simulate

If solo: treat the setup as a strict prompt. Speak your answer aloud as if an interviewer were there (record yourself if you can — the gap between what you think you sound like and what you actually sound like is always larger than expected). Timebox strictly.

---

## Articulate (30 min)

After all three mocks, spend 30 minutes on meta-reflection:

1. **Your pattern.** Across the three mocks, what did you do consistently well? What did you consistently miss?
2. **Your tell.** When you get nervous under time pressure, what do you reach for? Over-explaining? Drawing too much? Jumping to a tool before clarifying requirements? Naming the tell is half of managing it.
3. **Your design reach.** What 3 patterns do you reach for reliably, with confidence? These are your anchors in an interview — you will return to them when you're unsure.
4. **Your gaps.** What one topic showed up in the mocks where you felt thin? (Common honest answers: multi-tenancy details, cost allocation, disaster recovery for the platform itself, Backstage internals, policy-as-code rollout.) Plan 2–3 hours this week to shore it up before Week 12.

Write these down. They become your pre-interview self-briefing.

---

## Self-assess (30 min)

### From the repo

```bash
prep quiz --bank platform-engineer --topic system-design
```

Alternatively, review `quiz_banks/platform-engineer.json` for questions tagged `system-design`, `idp-design`, or `interview`.

Target: 80%+. This is less important than the mock scores this week; the quiz is a supplement, not the main assessment.

### Post-mock scorecard

For each mock, record:

- Your average rubric score (1–4 scale)
- The weakest criterion
- Notes on execution (did you run out of time? did you forget a step?)

If any mock averaged below 3.0, re-run it after 48 hours. Cold repetition is more useful than hot; trying immediately after reviewing the rubric is largely memorization practice.

---

## Outcome checkpoint

Before Week 12:

- [ ] Adopted a named system-design structure and used it consistently across all three mocks
- [ ] Ran Mock 1 (IDP design) under time pressure; scored against rubric
- [ ] Ran Mock 2 (IaC review) under time pressure; scored against rubric
- [ ] Ran Mock 3 (platform incident) under time pressure; scored against rubric
- [ ] Identified your own pattern, tell, design-reach, and gaps
- [ ] Scored average 3.0+ on each mock's rubric
- [ ] Scored 80%+ on Week 11 quiz subset (supplementary)

If any mock averaged below 3.0 after a cold re-run, that's your highest-priority focus area this week. Don't advance to Week 12 without at least one re-run that lands 3.0+.

---

## Strategy notes for interview day

A handful of judgments learned from senior-level loops:

1. **Always clarify first.** Every design conversation should start with 3–5 questions that reveal senior judgment. Who are the users? What are the constraints (scale, timeline, compliance)? What's the success metric?
2. **State your structure out loud.** "I'm going to spend the first 10 minutes on users and requirements, then 25 minutes on design, then 10 on trade-offs and operations." Shows the interviewer you've done this before.
3. **Propose the MVP first.** Most interviewers want to see your MVP thinking. They'll ask you to evolve it to a mature version — but only if you start with MVP. Starting with a mature architecture loses the MVP-first signal.
4. **Name what you're not solving.** Explicitly saying "I'm not solving secrets management deeply in this conversation — I'd use a managed service and move on" is a senior move. Juniors try to solve everything; seniors scope.
5. **Quantify when you can.** "40 tenants × 5 services each × 3 environments" is better than "lots of services." Quantification shows you can reason about scale.
6. **Bring trade-offs to the surface every 10 minutes.** Every design choice has a cost. Say it. "I'm proposing namespace-per-team because at 50 teams it's the right default; the cost is that we're relying on policy-as-code for isolation rather than hard kernel-level boundaries."

---

## Connections to later week

- Week 12 (Behavioral + Closing) uses the STAR prompts in [`../stories/`](../stories/) — many of which map directly to the mocks you just ran
