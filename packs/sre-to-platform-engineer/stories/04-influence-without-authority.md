# STAR Stories — Influence Without Authority

**Category 4 of 6 · 3 prompts**

> **Terms used in this category**
> - **STAR** — Situation, Task, Action, Result
> - **SRE** — Site Reliability Engineer
> - **Platform Engineer** — the role you're transitioning to
> - **Influence without authority** — driving change or adoption across teams where you have no reporting relationship or formal decision-making power
> - **RFC** — Request For Comments; a written proposal circulated for feedback before a decision
> - **Paved path / Golden path** — the opinionated, well-supported way
> - **Skeptic** — not a negative term; in mature platform work, skeptics are often the most valuable early reviewers
>
> Full definitions and equivalent titles in the [pack README](../README.md#what-we-mean-by-sre).

Platform engineers rarely have authority over the teams they serve. The platform team doesn't get to *make* product teams use the platform — it has to *earn* their use, conversation by conversation, release by release. These three prompts test that skill: driving adoption, aligning across teams, and convincing skeptics.

---

## Prompt 12 — Driving adoption of a platform feature

> *"Tell me about a platform feature you shipped and then drove to adoption. What did the rollout actually look like, week by week?"*

### SRE trap

"We shipped it and announced it in the engineering all-hands and emailed the teams." Reveals no *product* thinking about rollout — as if adoption happens automatically once the feature exists.

### Platform framing

Adoption is a product problem, not a communication problem. Strong answers show:

1. Pre-launch: the early design partners (teams that had input before GA) — they are your adoption backbone
2. Launch criteria: what made you call it "ready for general adoption"? Not "it compiles"; something like "3 teams have been using it for 4 weeks without issues"
3. The first 30 days: who adopted early, what friction emerged, what you fixed fast
4. The next 90 days: how you got from ~20% adoption to ~80%, the plateau-breaking moves
5. The long tail: the holdouts — did you make peace with them, or did you keep going?
6. Adoption metric: not just count, but usage quality — depth of use, retention, whether teams came back

### Coaching rubric (1–4 per criterion)

- **Pre-launch design partners** — Named specific teams and how they influenced the design
- **Launch criteria** — Specific threshold, not just a calendar date
- **First 30 days** — Concrete friction observed and fixed
- **Plateau-breaking move** — Named a specific tactic for getting past the early-adopter wall
- **Holdouts handled** — Acknowledged the long tail with judgment

Target: 3+ on each.

### Example shape

> "We shipped a service-scaffolder that would generate a new service with pre-wired observability, deploy pipeline, and catalog entry. Big deal for us — our first really opinionated platform feature.
>
> Pre-launch: 3 design-partner teams who'd given feedback in the RFC, then used a pre-GA version for about 6 weeks. Their feedback reshaped the config format twice before GA.
>
> Launch criteria wasn't 'we finished building.' It was 'a design-partner team has successfully onboarded a junior engineer who created a new service in under an hour without help.' That happened at roughly week 10.
>
> First 30 days post-GA: 4 new teams tried it. One service got stuck in a edge case (a specific cloud region we hadn't tested), which we fixed in 24 hours. Two teams had feedback about the language choice in the default template — we added a second option. The first 30 days was more about fixing than marketing.
>
> The plateau came around the 3-month mark. Fast adopters were in; skeptics weren't. The plateau-breaking move was a specific one: I noticed that most non-adopters still created services through 'copy an existing repo.' So we made the scaffolder the *same* experience — one command, same naming conventions as the copy workflow — rather than asking teams to learn a new paradigm. That, plus publishing 'how long it takes to add a service with the scaffolder vs copying' with actual numbers, moved us from 20% to 60% over the next quarter.
>
> The long tail: about 15% of teams never adopted. I made peace with it. Some had legitimate escape-hatch cases (wrap an existing open-source server; we didn't support that well). Some had inertia. I focused platform resources on keeping the scaffolder good for the adopters and let the long tail stay un-coerced. A good platform treats the long tail as signal, not as a failure.
>
> At 1 year: ~85% of all new services went through the scaffolder; the scaffolder's user experience metric (time-to-first-deploy) had improved 3 times in response to adopter feedback."

---

## Prompt 13 — Cross-team alignment

> *"Describe a time you had to align multiple teams on a platform direction when they had competing interests. How did you resolve it?"*

### SRE trap

"We had meetings and eventually reached consensus." Vague, reveals no method.

### Platform framing

Alignment across teams with competing interests is the canonical platform challenge. Interviewers want to see:

1. The specific competing interests (not "different opinions" — what each team actually wanted and why)
2. Your map of whose constraints were negotiable and whose weren't
3. The alignment method — usually an RFC process, a structured set of options with trade-offs, or a clear escalation path if alignment fails
4. The resolution — which side won, which side lost, and how you managed the "lost" side
5. The follow-through — did the alignment hold, or did it drift?

Key insight that strong candidates surface: *alignment isn't consensus*. Sometimes alignment means "we all agree Team A's direction wins, and Team B is going to be unhappy, and we've named the unhappiness."

### Coaching rubric (1–4 per criterion)

- **Specific competing interests** — Not vague; what each team wanted
- **Negotiability map** — Knew whose constraints were hard and whose were preferences
- **Method** — Described a specific alignment mechanism
- **Asymmetric resolution acknowledged** — Acknowledged that alignment often means someone loses
- **Drift monitoring** — Noted whether alignment held

Target: 3+ on each.

### Example shape

> "We needed to pick a single CI/CD tool for the platform. Three product groups had different needs: a web team wanted something with a rich UI and easy-to-use pipeline syntax (Team A), a data team needed strong job-orchestration primitives and retry semantics (Team B), a mobile team needed strong hardware-runner support for on-device builds (Team C).
>
> The RFC framed three options, each strong for one group's use case and imperfect for the others. I mapped the negotiability: Team C's hardware-runner constraint was *hard* (no runner support = can't do mobile), Team A's UI preference was *soft* (annoying, not blocking), Team B's orchestration need was *hard-ish* (could be worked around by chaining simpler jobs, at a cost).
>
> Once the map was visible, the decision was easier than it initially seemed: any tool that didn't support Team C's hardware runners was out. That narrowed the field to two. Between the two, we picked the one that gave Team B the better orchestration story, because workaround-to-chain-jobs was higher-cost than the UI annoyance.
>
> Team A was the "lost" side. We were explicit about it. The platform team committed to building one specific UI-layer tool on top of the chosen CI to reduce Team A's friction — so we carried part of the cost. Team A was unhappy for about a quarter, then adapted.
>
> The alignment held. Two years later we're still on the chosen tool. The tradeoff we accepted for Team A was real; I don't think we underestimated it. We just decided it was the right trade-off, and told Team A we'd decided it was the right trade-off, clearly."

---

## Prompt 14 — Convincing a skeptic

> *"Tell me about a time you convinced someone who was initially skeptical of a platform direction. What was their objection, and what actually changed their mind?"*

### SRE trap

Two common weak patterns:

- "I showed them the data" — reveals no understanding that data alone rarely convinces
- "They came around eventually" — reveals no specific moment of change

### Platform framing

Strong skeptics are almost always *right about something*. Often they're right about a concrete risk that the enthusiastic builders are under-weighting. A candidate who describes the skeptic charitably — as a valuable source of critique, not an obstacle — reads as senior.

Elements:

1. The skeptic and their specific objection (not "they didn't get it")
2. Why their objection was legitimate — the real risk or concern
3. The *specific moment* or evidence that changed their mind — usually not data, usually a demo, a pilot, a witnessed failure mode they cared about, or a conversation with a peer
4. How the conversation ended — did you earn a supporter? A neutral? A tolerator?
5. What you took away from the skeptic's objection — did it reshape what you built?

### Coaching rubric (1–4 per criterion)

- **Skeptic steelmanned** — Described their objection fairly
- **Legitimacy acknowledged** — Named why they had a real point
- **Specific change moment** — Not vague; a particular demo / evidence / conversation
- **Outcome classified** — Named the kind of support you earned (supporter / neutral / tolerator)
- **Design influence** — Acknowledged what the skeptic changed about the work

Target: 3+ on each.

### Example shape

> "We were introducing policy-as-code at admission time — blocking non-compliant manifests from being applied. The senior engineer who was most skeptical was also the most-respected SRE in the org, so her objection mattered a lot. Her specific concern: 'If the admission controller is broken, nobody deploys. You're introducing a single point of failure into the critical path for every team.'
>
> She was right. This is a legitimate risk and I'd under-weighted it. My initial instinct had been to argue about the policy's value. That was the wrong instinct.
>
> What actually changed her mind wasn't data. It was that I listened — I took her objection seriously enough to redesign the rollout around it. Specifically: dual-mode operation where the admission controller failed-open by default during the first 60 days, with alerts on fail-opens so we'd know if the controller was having issues without causing outages. We'd switch to fail-closed only after we had 60 days of controller-uptime data.
>
> The specific moment of change was when I showed her the proposed runbook for 'controller-down' and the SLO target (99.99% for the controller itself). She looked at it, said 'OK, this is fine,' and moved on. From there she was a quiet supporter — she never advocated for the program, but she stopped pushing back.
>
> What her objection changed about the work: the dual-mode rollout that I'd now use for *any* admission controller, and a pattern of considering controllers as critical-path infrastructure with their own SLOs. Both of those made it into the platform as a whole — her objection was a gift, even though at the time I remember being stung by it."

---

## How to use this file

1. Read all three prompts. Identify which story from your career each maps to.
2. For each, draft a version matching the example shape. Replace every scenario with your own.
3. Record yourself delivering each in 2–3 minutes. Listen back.
4. Score with the rubric. Note your weakest criterion across all three.
5. Revisit in Week 12 for the final polish.

## Navigation

- Previous category: [03-reliability-to-platform.md](03-reliability-to-platform.md)
- Next category: [05-failure-stories.md](05-failure-stories.md)
- Back to: [stories/](README.md)
