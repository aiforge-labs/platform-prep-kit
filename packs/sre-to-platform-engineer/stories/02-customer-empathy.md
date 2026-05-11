# STAR Stories — Customer / Developer Empathy

**Category 2 of 6 · 4 prompts**

> **Terms used in this category**
> - **STAR** — Situation, Task, Action, Result
> - **SRE** — Site Reliability Engineer
> - **Platform Engineer** — the role you're transitioning to
> - **DevEx** — Developer Experience
> - **Stakeholder** — in platform context, almost always an internal team or team lead
> - **Ticket-driven platform** — an antipattern where platform work is inbound-only; platform reacts to requests without owning a product direction
> - **Paved path / Golden path** — the opinionated, well-supported way a platform expects teams to build and ship
>
> Full definitions and equivalent titles in the [pack README](../README.md#what-we-mean-by-sre).

Customer-empathy prompts are where platform engineers most often get separated from SREs who "happen to build tools." The language, the framing, and the instincts are visibly different. Four prompts: finding real pain, saying no, migrating reluctant users, and validating an idea before building.

Each prompt follows the pack's standard STAR-coaching structure.

---

## Prompt 4 — Finding the real pain (not the reported pain)

> *"Tell me about a time the pain a team reported to you wasn't actually their real pain. How did you find out?"*

### SRE trap

"A team complained about slow deploys, so I profiled the CI pipeline and found a cache issue." Reasonable SRE story, but it takes the complaint at face value. Platform engineers who are at their best do the more interesting thing: treat every ticket as partial information about a deeper workflow problem.

### Platform framing

Describe the original reported pain. Then describe the investigation — the conversation, the observation, the data — that revealed the *actual* friction, which was different (and usually more interesting). Name what would have happened if you'd just solved the reported pain — it would have been a short-term fix and probably a repeat complaint three months later. Then the fix you actually shipped.

### Coaching rubric (1–4 per criterion)

- **Original reported pain was specific** — Named what they said, in their words
- **Investigation method** — Described how you learned the real pain (not just "I talked to them")
- **The delta** — Made the difference between reported and actual pain explicit
- **Long-term fix vs short-term fix** — Named what a short-term fix would have missed

Target: 3+ on each.

### Example shape

> "A product team filed a ticket that our internal CI was 'too slow' — specifically that their test suite ran 14 minutes and it was blocking PRs. The obvious thing to do was profile their CI job and try to trim minutes off.
>
> I offered to pair on it instead. In the first 20 minutes of watching their workflow, I noticed they ran the full test suite 3–4 times before merging — once locally, then twice in CI because they'd push a fix. The 14 minutes wasn't the main cost; the 3–4 rounds of flakiness was.
>
> The real pain wasn't CI latency; it was flaky tests compounding with a no-merge-until-green policy. If I'd 'fixed' CI by trimming 4 minutes, the ticket would have been back in two months with the same complaint.
>
> I brought the flake data back and the team realized they'd been living with it for a long time — flake repair had no owner. We set up a simple weekly flake budget report and changed the merge policy to skip the flaky tests by name (identified from the data) while a separate track did the actual flake repair. Six weeks in, their effective PR turnaround was about 30% faster, and the CI suite duration hadn't changed. The fix wasn't a CI fix."

---

## Prompt 5 — Saying no to a request

> *"Tell me about a time a team asked you for something and you said no. How did you handle it?"*

### SRE trap

Either:

- "I said no and referred them to our roadmap" — reveals no relationship management, sounds gate-keeper-ish
- "I said yes but in a small scope" — isn't actually a no; reveals no conviction
- "I told them it wasn't possible" — over-strong; rarely is something truly impossible

### Platform framing

A good platform engineer says no frequently, because every "yes" is a commitment to future maintenance. The interviewer wants to hear:

1. The specific request
2. Why it was a reasonable thing to ask for (validate the request; don't strawman it)
3. The reason it was still a no — usually: cost relative to benefit, opportunity cost, scope creep, or (most interestingly) that the request masked a different problem that the platform shouldn't solve
4. How you said it — tone, content, what you offered instead
5. The downstream — did the team understand, push back, escalate? Did the relationship survive?

### Coaching rubric (1–4 per criterion)

- **Specific request, steelmanned** — Described the request fairly; didn't set up a strawman
- **Reason for the no** — Gave a real reason, not "it's not on our roadmap"
- **Tone and offer** — Described the conversation and what you offered instead
- **Relationship outcome** — Named what happened to the team-platform relationship

Target: 3+ on each.

### Example shape

> "A team asked us to add a 'deployment-freeze button' to the platform — a single click that would pause all deploys for their services during their Black Friday-equivalent event. On the surface, reasonable. They'd had deploys during peak traffic bite them before.
>
> The request was reasonable but the solution was the wrong level of abstraction. A freeze button on the *platform* would be an easy feature to add and hard to remove — we'd have more teams asking for variants (freeze my team only, freeze at specific times, freeze conditionally). It would encode an expectation that the platform was responsible for a team's change-management calendar.
>
> I said no, but carefully. I agreed with the risk. I proposed a different solution: a team-owned GitHub Actions workflow that set their services' GitOps reconciliation to paused for a time window, with automatic unpause. Same outcome; ownership in the right place; no platform feature to maintain.
>
> The conversation had two rounds. First round, they pushed back — wanted the convenience of the platform feature. Second round, I showed them the pause-workflow I'd already prototyped (20 lines of YAML) and walked them through it. They adopted it. Two other teams have since used it.
>
> The relationship improved, actually. Saying no with a better alternative reads as having thought about their problem, not deflecting it."

---

## Prompt 6 — Migrating reluctant users

> *"Tell me about a time you had to get a team to migrate off something they were used to and onto a new platform or tool. How did you do it?"*

### SRE trap

"We announced the migration and gave them a deadline" — reveals no empathy, no migration support, no understanding that developers have sunk cost for a reason.

### Platform framing

Migration is a product-engineering problem, not a compliance problem. Strong answers cover:

1. Why they were reluctant (often: prior bad migration experience; or: the old thing still works; or: they don't trust the new thing)
2. The early skeptics you recruited (not: "we told everyone"; but: "we picked one team who were critical-friendly and migrated them first")
3. What evidence you offered — the new thing must be clearly better for *them*, not just better for the platform
4. The migration-cost absorption — what did you, the platform team, do to reduce the developer cost?
5. Pacing — migrations that try to move everyone at once often stall; the best ones move in visible waves

### Coaching rubric (1–4 per criterion)

- **Root of the reluctance** — Named specifically why they were resistant
- **Early-adopter strategy** — Described who went first and why
- **Platform-absorbed migration cost** — Named concrete work you did to reduce their burden
- **Pacing strategy** — Didn't describe this as a single event

Target: 3+ on each.

### Example shape

> "We were moving teams off a legacy logging pipeline — a 6-year-old Elasticsearch + Logstash setup we ran in-house — onto OpenSearch as a managed service with a new ingestion path. Most teams were fine with it. Three were reluctant: they'd built dashboards, alerts, and saved queries over years on the old system.
>
> The reluctance was rational. Their investment was real. And migrations have a *specific* history of being announced, partially completed, and then abandoned, leaving teams with two half-working systems. They'd lived that before.
>
> We picked one of the three as the early adopter. Not the most critical team — the most critical-friendly team, a team whose tech lead I trusted to push back honestly. We migrated them first, end-to-end: the platform team wrote the OpenSearch queries to reproduce their saved searches, converted their dashboards, re-pointed their alerts. Two weeks of platform-team work for one team's migration. We ate the cost.
>
> That first migration took 3 weeks instead of the 1 we'd hoped. The edge cases alone were worth it — we documented 8 migration gotchas we hadn't anticipated.
>
> The other two teams migrated in the following month, following the same pattern but with the platform team absorbing less of the cost (because we had a migration guide by then). We finished in 8 weeks across the three reluctant teams and ~14 weeks for all teams.
>
> I was wrong about one thing: I'd budgeted one week per team, had to negotiate with leadership for more. The cost we absorbed was larger than planned. The migrations didn't stall — and that was what I'd been most afraid of — but they took longer. The lesson: migration timelines I give to leadership should always include explicit platform-team cost, not just the wall-clock to finish."

---

## Prompt 7 — Validating an idea before building

> *"Tell me about a platform capability you were excited to build and then chose not to build, because the validation didn't hold up. How did you kill it?"*

### SRE trap

"I decided not to build it after thinking about it" — no validation method, no evidence. Reveals instinct, not process.

### Platform framing

This tests whether you have any validation practice beyond your own judgment. Strong answers describe a specific validation method (survey, interviews, shadow deployment, internal beta with one team), the signal it produced, and the discipline to follow the signal even when it contradicts your instinct.

Killing a project you were excited about is a distinctly senior skill. Juniors build the thing anyway and rationalize. Seniors kill it and save the maintenance cost.

### Coaching rubric (1–4 per criterion)

- **Specific validation method** — Named *how* you tested the idea
- **Contrary signal** — Named what the validation told you that contradicted your instinct
- **Discipline to kill** — Explained how you actually decided to stop, rather than scoping down
- **Second-order outcome** — Named what you learned that informed a different decision

Target: 3+ on each.

### Example shape

> "I'd been wanting to build an internal 'paved-path' for machine-learning services — a scaffolder template that would stand up a model-serving service with observability, A/B traffic splitting, and a feature store hook pre-wired. I thought it would unblock data-science teams who were pain-points at the time.
>
> Before building, I ran a quick validation: 30-minute interviews with 6 ML engineers from 4 different teams. My hypothesis: they were spending 3–5 days bootstrapping services. A reasonable investment: if we cut that to 30 minutes, they'd love us.
>
> What the interviews surfaced: bootstrapping was a pain, but it wasn't their top-3 pain. Their top-3 were (1) feature-store read latency, (2) a lack of shadow-traffic evaluation before going live, and (3) the observability not being model-aware — metrics were request/latency, not prediction drift or calibration. A fancy paved-path service would have been a nice-to-have for problem 0, which was their top-5.
>
> I killed the paved-path idea and started scoping the shadow-traffic-and-model-observability idea instead. That was harder to build and more specific, but actually solved a top-3 pain. We shipped the shadow-traffic tool about 6 months later and it had 5 of the 6 teams using it within a quarter.
>
> The honest lesson was about my own instinct. The paved-path idea was seductive because it would be satisfying to build and easy to measure (time-to-first-deploy). The shadow-traffic idea was less satisfying to build and harder to measure, but it solved a real problem. Validation saved me from the appealing-but-wrong project."

---

## How to use this file

1. Read all four prompts. Identify which story from your career each maps to.
2. For each, draft a version matching the example shape. Replace every scenario with your own.
3. Record yourself delivering each in 2–3 minutes. Listen back.
4. Score with the rubric. Note your weakest criterion across all four.
5. Revisit in Week 12 for the final polish.

## Navigation

- Previous category: [01-technical-leadership.md](01-technical-leadership.md)
- Next category: [03-reliability-to-platform.md](03-reliability-to-platform.md)
- Back to: [stories/](README.md)
