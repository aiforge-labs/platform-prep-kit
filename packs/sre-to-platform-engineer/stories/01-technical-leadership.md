# STAR Stories — Technical Leadership

**Category 1 of 6 · 3 prompts**

> **Terms used in this category**
> - **STAR** — Situation, Task, Action, Result; the canonical behavioral-interview story format
> - **SRE** — Site Reliability Engineer (the role you're transitioning *from*)
> - **Platform Engineer** — the role you're transitioning *to*
> - **IDP** — Internal Developer Platform
> - **SLO** — Service Level Objective
> - **Trade-off** — the inherent cost of any design choice; naming it is a senior signal
> - **Paved path / Golden path** — the opinionated, well-supported way a platform expects teams to build and ship
>
> Full definitions and equivalent titles in the [pack README](../README.md#what-we-mean-by-sre).

Technical-leadership prompts test whether you can own a technical decision end-to-end: understand the problem, propose an approach, make trade-offs explicit, and own the outcome whether it lands well or not. Three prompts in this category: designing something, making a trade-off, and deprecating something.

Each prompt below follows the pack's standard structure:

- **Prompt** — the interview question itself
- **SRE trap** — how an SRE typically answers (and why it reads as weak)
- **Platform framing** — what the interviewer is actually listening for
- **Coaching rubric** — 4 criteria, score yourself 1–4 per criterion
- **Example shape** — a sample answer scaffold (replace with your real story)

---

## Prompt 1 — Designing something used by other engineers

> *"Walk me through a technical system you designed that other engineers ended up using. What was the problem, and what design decisions did you make?"*

### SRE trap

Describe the system architecture in detail — components, data flow, infrastructure — without mentioning the users, their problems, or the adoption signal. The interviewer's eyes glaze over because the answer is about the system, not the people who used it or didn't use it.

A second trap: claim success based on system-level metrics (uptime, latency) without any user-facing outcome.

### Platform framing

Start with the user and the problem, in that order. State the specific pain point using a number or a signal — "5 teams were each building their own version of this"; "deploys took 45 minutes and 30% failed." Then the design, briefly — enough to show the shape, not the YAML. Then the adoption signal and the learning.

Structural elements of a strong answer:

1. Problem: what users wanted to do and couldn't, or did badly
2. One-line shape of the solution (not a tour of the architecture)
3. The non-obvious design decision — something where a reasonable engineer could have picked differently
4. Adoption signal — how many teams used it, how many still use it, what the feedback was
5. The surprising lesson

### Coaching rubric (1–4 per criterion)

- **User-centered framing** — Named specific users and a measurable problem (not "engineers wanted better deploys")
- **Non-obvious design decision** — At least one choice where the trade-off is called out ("I chose X over Y because…")
- **Adoption signal** — A number or a concrete signal, not a claim
- **Honest lesson** — Named something you learned or would do differently, even if the outcome was good overall

Target: 3+ on each.

### Example shape (replace with your own story)

> "Our product teams were each writing their own cluster-bootstrap scripts — at the time 5 teams across 3 product lines, and they'd diverged enough that we had security gaps because only some of them included the hardening baseline. I proposed one shared bootstrap module as an internal Terraform module with opinionated defaults for the security baseline and explicit escape hatches for team-specific config.
>
> The non-obvious decision was making it a *module*, not a service. Some folks pushed for a provisioning API — a platform-run service — which would have been more powerful but would have made the platform team a bottleneck for cluster creation. A module kept teams self-service. The trade-off: version drift. Teams could lag behind the latest security baseline. I mitigated this with an automated compliance scan and a 30-day grace period before escalation.
>
> 8 of the 12 teams adopted it within the first quarter. Two held out — both had legitimate reasons we'd missed; we added their requirements in v2. Two never adopted, which I initially read as failure, but after talking to them I realized they were already planning to migrate to a different cluster strategy entirely, and our module wasn't worth the short-term investment.
>
> The lesson was that I'd built it as a platform capability first, and an adoption story second. For v2 I started with the migration conversation and found 4 more use cases I hadn't known about."

---

## Prompt 2 — A trade-off you had to make

> *"Tell me about a technical trade-off you made that had real consequences. What were the options, and how did you decide?"*

### SRE trap

Either:

- Describe a trade-off where the "right" choice was obvious in hindsight — unconvincing, because every real trade-off has regret
- Describe the choice but not the consequences — "we picked option A, it worked out"
- Frame the trade-off as purely technical, ignoring organizational or user-experience dimensions

### Platform framing

Name the options at roughly equal depth. The *why-not-the-other* is usually more revealing than the *why-this-one*. Name the specific stakeholder conversations — who wanted A, who wanted B, who had which concern. Then the decision and — critically — the *regret* or cost you accepted.

Trade-offs worth considering from your own career:

- Build vs buy (e.g., adopt an OSS tool vs build in-house)
- Strict vs flexible (policy-as-code: strict enforcement vs audit mode)
- Centralized vs federated (one platform team vs embedded platform engineers)
- Migration strategy (big-bang vs gradual vs coexist)
- Feature completeness vs timeline

### Coaching rubric (1–4 per criterion)

- **Options at equal depth** — Both sides of the trade-off fully described
- **Stakeholder dimension** — Acknowledged organizational / political constraints, not just technical
- **Explicit cost** — Named what the chosen option cost you (not just what it gained)
- **Retrospective judgment** — Said whether you'd make the same call today, and why

Target: 3+ on each.

### Example shape

> "We were deciding how to roll out policy-as-code for our Kubernetes platform. Two paths: audit-mode first, enforce-mode first. Audit-mode first was safer — we'd see what would break before it broke — but it's slower, and the longer policies sit in audit, the longer teams treat them as 'probably not going to be real.' Enforce-mode first is the stronger commitment, but a bad policy at enforce is an incident.
>
> The stakeholders: the security team wanted enforce-mode immediately because they'd been waiting a quarter for this. The platform team was nervous about breaking deploys. The product teams, when I asked, mostly hadn't thought about it.
>
> We went audit-mode first, with a strict 30-day cap before promotion. The cost was the security team's patience — they were tired, and I understood that. I committed to publishing the audit findings weekly so they could see progress. In practice, we found 4 things in audit that would have caused deploy failures on day one, so the audit window justified itself. But the 30-day cap was important — it said 'this isn't a permanent half-measure.'
>
> If I did it again, I'd go audit-mode *shorter* — two weeks, not four. Four weeks was enough for teams to get used to seeing violations and shrugging. Two weeks is enough to catch the big ones and forces us to commit sooner."

---

## Prompt 3 — Deprecating something

> *"Tell me about something you deprecated — a tool, service, or platform capability. How did you handle it?"*

### SRE trap

"We announced the deprecation, gave teams 90 days, and turned it off." Technically accurate, reveals nothing about stakeholder management, migration support, or the uncomfortable conversations that real deprecations always involve.

### Platform framing

Deprecation is one of the most senior platform tasks. Every platform accumulates capabilities that *were* good but now should go. Describing a real deprecation well reveals:

1. The discovery that it needed to go (what signal told you)
2. The stakeholder map — who was using it, who'd be affected, who'd be relieved
3. The migration support you provided — not just "we have docs," but something concrete
4. The edge-case that held things up (there's always one)
5. The final flip — did you hit the original deadline, or did you slip, and how did you manage that

### Coaching rubric (1–4 per criterion)

- **Signal for deprecation** — Specific reason, not just "it was old"
- **Stakeholder management** — Named who was affected, what they needed
- **Migration support** — Concrete, beyond docs
- **Honest edge case** — Acknowledged something that didn't go to plan

Target: 3+ on each.

### Example shape

> "We had a custom secrets-distribution tool I'd built two years prior. It was a thin wrapper over HashiCorp Vault with some org-specific conveniences. At the time, it saved a lot of onboarding friction. By year two, Vault had added native equivalents for most of what our wrapper did, and our wrapper was now carrying drift — it was the slow path to Vault features because we had to add them to the wrapper too.
>
> The signal for deprecation was that the wrapper had four open issues, none had been touched in 6 weeks, and two were from teams asking for features Vault already had natively. The wrapper had become a tax, not a capability.
>
> I mapped the 11 services using it, talked to their owning teams, and found three classes: services that had a thin usage pattern (just read secrets), services with a medium pattern (secret rotation tied to our wrapper's cron), and one service that had wrapped itself tightly around our wrapper's failure semantics. The first two classes were 1-day migrations each. The third was a 2-week refactor and needed support from the platform team.
>
> We did it in two waves: the thin users in 30 days (quiet migration, we wrote the PRs ourselves), the medium users in 60 days (we provided a migration guide and pair-programmed with one team who volunteered), and the tightly-coupled user as a separate project with its own 90-day window.
>
> The edge case: one team had built an audit-log integration on our wrapper's error codes. Those error codes weren't in Vault. We had to build a tiny adapter service that translated Vault errors into the legacy codes for a 6-month transition, then deprecated the adapter too. That slipped our original shutdown date by about 3 months.
>
> The hardest conversation was with the security team, who wanted the wrapper off the network immediately for risk-reduction reasons. We negotiated: they got a hard shutdown date in writing; we got the flex to support the edge-case team. The final flip happened on the revised date, not the original."

---

## How to use this file

1. Read all three prompts. Identify which story from your career each maps to.
2. For each, draft a version matching the example shape. Replace every scenario with your own.
3. Record yourself delivering each in 2–3 minutes. Listen back.
4. Score with the rubric. Note your weakest criterion across all three.
5. Revisit in Week 12 for the final polish.

## Navigation

- Back to: [stories/](README.md)
- Next category: [02-customer-empathy.md](02-customer-empathy.md)
