# STAR Stories — Reliability-to-Platform Translation

**Category 3 of 6 · 4 prompts**

> **Terms used in this category**
> - **STAR** — Situation, Task, Action, Result
> - **SRE** — Site Reliability Engineer
> - **Platform Engineer** — the role you're transitioning to
> - **SLO** — Service Level Objective
> - **MTTR** — Mean Time to Restore
> - **Postmortem** / **Post-incident review (PIR)** — written analysis after an incident
> - **Runbook** — an operational document describing how to respond to a specific alert or incident
> - **Toil** — manual, repetitive, automatable ops work
> - **Paved path** — the opinionated, well-supported way
>
> Full definitions and equivalent titles in the [pack README](../README.md#what-we-mean-by-sre).

These four prompts cover the specific category where transitioning candidates often win or lose their loop. You have deep SRE experience. The interviewer wants to see whether you can tell those stories in a way that reveals platform thinking — not *what you did as an SRE*, but *what a platform engineer would have noticed about the same situation*.

Four prompts: turning an on-call learning into a platform feature, postmortem to product, cross-team reliability, and a runbook that became a platform capability.

---

## Prompt 8 — On-call learning → platform feature

> *"Tell me about something you noticed on-call that became a platform feature. What was the observation, and how did it become a product decision?"*

### SRE trap

"I got paged about X. I fixed it. I wrote a runbook." That's the SRE arc. The interviewer wants the next half of the story: *why* you noticed this was a platform-level problem, not just your problem, and what you did about it.

### Platform framing

Structure:

1. The on-call event — what alerted you
2. The observation that generalized — "this isn't just my service; this is going to happen to anyone on the platform"
3. The product-thinking move — what did you see that made this a platform capability and not a one-off fix?
4. The build — what the platform feature was, at a high level
5. The adoption signal

### Coaching rubric (1–4 per criterion)

- **Generalization moment** — Named the specific observation that made you see it as platform-level
- **Product-thinking move** — Framed the fix as a platform capability, not a one-off
- **Build described briefly** — Showed the shape without going deep on mechanics
- **Adoption signal** — Concrete evidence the feature landed

Target: 3+ on each.

### Example shape

> "I got paged at 2am because a specific deploy had rolled out a bad config — an env var that pointed to a stale secret — and caused the service to 500 on startup. Standard story: roll back, ship a fix in the morning. But during the rollback I noticed that 7 other services in the same namespace referenced the same env var in the same way. If any of them had restarted that night — which they might have, due to autoscaling — they'd have hit the same pattern.
>
> The generalization: we didn't have *any* platform-level handling of secret rotation. Every service was doing its own thing. The fact that I'd been paged was luck; the platform had no safety net.
>
> I wrote this up in the postmortem as a platform gap, not an app gap. The corrective action was a platform feature — a pre-deploy check that warned if a referenced secret had been rotated in the last 24 hours, and a graceful-restart pattern for services to fail-closed if they couldn't read their secret. The service-level change was 20 lines of YAML per service; the platform-level check was the new thing.
>
> Six months later we'd avoided at least 3 similar pages across different services. I only know about 3 because teams mentioned them in retros; the ones where the check silently prevented the issue I never heard about."

---

## Prompt 9 — Postmortem to product

> *"Walk me through a postmortem where the corrective action became a platform-level change, not a team-level one."*

### SRE trap

Describe the incident, the 5-whys, and the team-level corrective action. Misses the interesting part — the judgment call to make this a platform problem, not a team problem.

### Platform framing

The key move is the reframing. Every incident has multiple possible framings: bad code, missed review, skipped test, gap in platform safety. *The choice of framing is a design decision.* Strong answers articulate why you chose the platform framing — and usually, what resistance you encountered when you did.

Elements:

1. The incident in one paragraph
2. The obvious team-level framing — what most postmortems would have landed on
3. Your reframe to a platform-level problem
4. The stakeholder conversation — who pushed back, who agreed
5. The corrective action at platform level
6. The meta-benefit — what this reframing enabled beyond this specific incident

### Coaching rubric (1–4 per criterion)

- **Obvious-framing named** — Showed what a team-level postmortem would have concluded
- **Platform reframe** — Articulated the shift in framing, not just the shift in fix
- **Stakeholder acknowledgment** — Named the politics
- **Meta-benefit** — Showed the reframing paid off beyond this one incident

Target: 3+ on each.

### Example shape

> "A service had a full-day outage because a team had scaled up a dependency that didn't support horizontal scaling — it was designed to be a singleton and the team didn't know. The team's read of the postmortem: 'we should document which services are horizontal-scale-safe.'
>
> That's a fine team-level fix. But from the platform angle, it was a platform failure. The deploy pipeline let a non-scalable service scale. The platform had the information — the service was labeled correctly in its Helm chart — and didn't use it. Any team could trip this; we'd just gotten lucky it was this one first.
>
> The reframe was: *it's not a documentation problem; it's a missing platform guardrail.* The stakeholder resistance came from the platform team itself — adding a pre-scale check is platform work, and we had a full roadmap. A team-level 'document it' is free.
>
> I made the case by quantifying: 6 other services in the catalog with the same singleton pattern, any of which could have been the one. The platform team agreed to take on the pre-scale admission check. It shipped in about 3 weeks. The meta-benefit: the check itself became a *pattern* — the team now had a place to encode 'before scaling a workload, run these checks,' and three months later two more checks had joined the same admission controller. The postmortem kicked off a small mechanism that's been paying down for over a year."

---

## Prompt 10 — Cross-team reliability problem

> *"Tell me about a reliability problem that crossed team boundaries, where no single team was responsible for the fix. How did you drive it?"*

### SRE trap

"We formed a tiger team." Vague. Reveals no mechanism, no structure, no understanding of why cross-team reliability problems are hard.

### Platform framing

Cross-team reliability problems are where platform engineers specifically earn their keep. The interviewer wants to see:

1. The specific nature of the cross-team-ness — e.g., a failure mode that requires changes in 3 teams' services plus platform instrumentation plus infra config
2. The coordination structure you set up — not "we had meetings," but a specific mechanism (a shared doc, a weekly sync with defined agenda, a RACI, a working group with a time-bound charter)
3. The accountability — who owned what, how progress was visible
4. The thing that almost made it fail — cross-team work *always* has a stall moment
5. The outcome

### Coaching rubric (1–4 per criterion)

- **Specificity of cross-team-ness** — Named what made it cross-team, concretely
- **Coordination structure** — Described the mechanism with some detail
- **Accountability** — Named who owned what
- **Stall moment** — Acknowledged a real moment where it almost failed

Target: 3+ on each.

### Example shape

> "Our platform-wide MTTR had regressed 3x over two quarters. No single team was responsible. Contributing factors: our alerting had gotten noisier (platform issue), our on-call rotations had more junior engineers rotating in as teams grew (team issue), our runbooks had decayed (mixed), and our escalation paths weren't clear for cross-team incidents (org issue).
>
> I proposed a 6-week working group: 2 platform engineers (me plus one), one senior engineer from each of the 4 highest-MTTR service teams, and a representative from the SRE function. We met weekly. Three specific workstreams with single owners: alert rationalization (platform), runbook refresh (team reps), escalation policy (SRE rep with platform input). Each had a 6-week deliverable.
>
> The stall moment was week 3. The runbook refresh workstream wasn't progressing — the team reps weren't making time. I reframed: the platform team would ship a runbook template and do the first refresh *with* each team as pairing, rather than asking them to do it solo. That unlocked it.
>
> By end of 6 weeks: alert noise down ~40%, 80% of critical runbooks refreshed, a documented escalation-during-incident policy with 4 named on-call managers. MTTR drifted back to baseline over the following two quarters. The working group disbanded cleanly — a rare thing; most working groups become standing meetings."

---

## Prompt 11 — A runbook that became a platform capability

> *"Describe a runbook or manual process that you decided to turn into a platform capability. How did you decide it was worth automating, and what was the trade-off?"*

### SRE trap

"It was toil, so I automated it" — reveals no judgment about *when* to automate vs accept vs improve the runbook.

### Platform framing

Not every runbook should be a platform capability. Automating the wrong ones creates maintenance debt. The interviewer wants:

1. The runbook / process you started with
2. The judgment call — why this one, not others (frequency × pain × stability × generalizability)
3. The cost of automation (what breaks, what you now have to maintain)
4. The outcome — did it earn its keep?

### Coaching rubric (1–4 per criterion)

- **Judgment call articulated** — Named the criteria for choosing this over alternatives
- **Honest cost** — Named the maintenance burden
- **Follow-up on ROI** — Did you measure whether the automation paid back?
- **What you did *not* automate** — Bonus if you named a similar runbook you deliberately kept manual

Target: 3+ on each.

### Example shape

> "We had a runbook for 'node pressure remediation' — when a node hit CPU or memory pressure, on-call would cordon, drain, and replace it manually, taking about 20 minutes and happening maybe 4–5 times a quarter per cluster. Boring, low-stakes, common enough that every on-call had done it.
>
> I considered three options: (1) keep the runbook, (2) improve the runbook with better docs and a CLI alias, (3) automate fully.
>
> The judgment call favored (3) because the process was stable (it had been the same for over a year), generalizable (every cluster had this; every on-call had done it), and the failure mode was gentle (over-triggering would just replace a healthy node, which is tolerable). Three criteria: frequent enough, stable enough, and safe enough.
>
> I chose *not* to automate two related runbooks: 'cluster-scale event' (too rare; automation would have bit-rotted) and 'service mesh connectivity issues' (too unstable; the underlying issue mutated every few months as the mesh was tuned).
>
> The cost of the automation: a new platform service (a remediation controller) that now needs its own on-call for the rare cases when *it* misbehaves. Operational surface area moved, didn't vanish. And we did have one incident where the controller failed-open and cordoned an entire node pool because of a metric-collection bug. Embarrassing but contained.
>
> Outcome: toil down by ~8 hours per on-call rotation. The controller has been in production ~18 months; it's been a good investment. The rule-of-thumb I now use: *automate when all three axes — frequency, stability, gentleness-of-failure — are 'yes.' If any is 'no,' improve the runbook instead.*"

---

## How to use this file

1. Read all four prompts. Identify which story from your career each maps to.
2. For each, draft a version matching the example shape. Replace every scenario with your own.
3. Record yourself delivering each in 2–3 minutes. Listen back.
4. Score with the rubric. Note your weakest criterion across all four.
5. Revisit in Week 12 for the final polish.

## Navigation

- Previous category: [02-customer-empathy.md](02-customer-empathy.md)
- Next category: [04-influence-without-authority.md](04-influence-without-authority.md)
- Back to: [stories/](README.md)
