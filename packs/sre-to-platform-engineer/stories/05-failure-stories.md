# STAR Stories — Failure Stories

**Category 5 of 6 · 3 prompts**

> **Terms used in this category**
> - **STAR** — Situation, Task, Action, Result
> - **SRE** — Site Reliability Engineer
> - **Platform Engineer** — the role you're transitioning to
> - **Failure story** — a story about something that didn't work; in interviews, a required category for senior roles
> - **Blast radius** — the set of tenants or users affected
> - **Paved path / Golden path** — the opinionated, well-supported way
>
> Full definitions and equivalent titles in the [pack README](../README.md#what-we-mean-by-sre).

Failure stories are non-optional at senior level. Interviewers ask explicitly because *the absence of a strong failure story is disqualifying*. A candidate who can't produce one reads as either unreflective or too junior.

Three prompts: a platform nobody used, a wrong abstraction, and a signal you missed. Each tests a specific kind of reflection.

---

## Prompt 15 — A platform nobody used

> *"Tell me about something you built that didn't get the adoption you hoped for. What happened?"*

### SRE trap

Two common weak patterns:

- "It was used, just not as much as we hoped" — hedging; fails to answer the question
- "Teams were resistant to change" — blame-shifting; specifically the thing interviewers flag

### Platform framing

The interviewer wants to hear:

1. What you built and what adoption you hoped for (so the failure has scale)
2. What you assumed about users that turned out to be wrong
3. The signal that told you it wasn't landing — and how long it took you to see the signal
4. What you did about it — kept iterating, rescoped, deprecated, learned and moved on
5. The second-order takeaway — what your *process* for building platform features has changed since

The deepest version of this story is when the candidate realizes that *they built the right tool for the wrong target state* — i.e., they solved a problem that wouldn't exist once the org had done something different upstream. This kind of self-awareness is rare and highly distinguishing.

### Coaching rubric (1–4 per criterion)

- **Scale of hope** — Described the adoption you expected, concretely
- **Wrong assumption named** — Specifically what you thought users wanted
- **Signal latency** — Acknowledged how long it took to admit the problem
- **Process change** — Named something that's different in how you build now
- **No blame-shifting** — Did not attribute the failure primarily to users

Target: 3+ on each.

### Example shape

> "I built an internal 'service blueprint' tool. The idea: product teams could describe their service at a high level (a YAML manifest — 'this is a web service with a Postgres database, needs internal-only networking, expected traffic 100 req/s') and the platform would generate the Terraform, Helm, CI config, and catalog entry.
>
> I expected ~70% of new services to use it within a year. After 6 months, adoption was about 15%. After a year, about 25%.
>
> The wrong assumption: I thought the friction was in writing infrastructure config. Once I actually watched teams start a new service, I realized the friction was in *thinking through what they wanted before they had to commit to it*. Teams liked to iterate on their Terraform as they figured out what their service was. My tool asked them to make decisions upfront that they were trying to avoid making upfront.
>
> The signal that told me was telling. Only a fraction of teams used the blueprint tool. A much larger fraction copy-pasted the *output* of the blueprint tool from the first team that used it, then modified it. They wanted a starting point, not a generator. I took about 2 months too long to admit this.
>
> What I did: deprecated the blueprint-generator UI and converted it into a library of well-commented templates teams could copy and hack. Essentially: reduced my own tool to a much smaller, less clever thing. That version got to ~80% adoption within the next quarter.
>
> What changed about my process: I now start every platform feature with the question *'how would a team do this without the platform?'* If the answer is 'they'd copy-paste from a teammate,' my tool should be a better thing to copy-paste from — not a generator that replaces the copy-paste. That rule has saved me from building two more too-clever tools since."

---

## Prompt 16 — The wrong abstraction

> *"Tell me about a time you built an abstraction that turned out to be the wrong abstraction. How did you recognize it, and what did you do?"*

### SRE trap

"It was slightly wrong, so we refactored it" — reveals no deep learning.

### Platform framing

Wrong-abstraction stories are a specific subset of failure story. The shape:

1. The problem you were solving, and why the specific abstraction seemed right at the time
2. The early success — wrong abstractions usually look right for a while
3. The pattern of pressure — requests that started feeling like they were *fighting* the abstraction rather than using it
4. The recognition moment — usually specific; something you saw that crystallized "this shape is wrong"
5. The decision — evolve, replace, or deprecate
6. What you took away about how to recognize this pattern earlier next time

The recognition-moment is the heart of the story. Weak versions never arrive at the specific moment; strong versions pinpoint it.

### Coaching rubric (1–4 per criterion)

- **Why the abstraction seemed right** — Fairly describes the original reasoning
- **Early success acknowledged** — Doesn't pretend it was obviously wrong
- **Recognition moment named** — Specific moment, not "over time we realized"
- **Decision owned** — Named whether you evolved, replaced, or deprecated
- **Pattern for next time** — Named how you'd spot it earlier

Target: 3+ on each.

### Example shape

> "We had a 'service tier' abstraction — services were labeled tier-1 (customer-critical), tier-2 (internal-critical), or tier-3 (experimental). The tier drove everything: deploy-approval requirements, observability detail, SLO targets, on-call behavior.
>
> It seemed right. It *was* right for about 18 months. Teams understood the tiers, and the platform behaved predictably based on tier.
>
> The pattern of pressure: requests started arriving that didn't fit. 'This is a tier-1 service but only for an internal team — do we need customer-grade on-call?' 'This is tier-3 but handles regulated data — can we tier-1 the security but keep tier-3 on-call?' Every month, another variant.
>
> The recognition moment was specific: a new service that was tier-1 for reliability, tier-2 for on-call, tier-1 for security, and tier-3 for velocity. All four at once. The tier number was doing the work of four independent attributes, and we'd been treating it as one.
>
> The decision: replace the tier abstraction with a small set of independent attributes (reliability-class, security-class, on-call-class, velocity-class — 2-3 values each). More configuration, but it matched reality. We migrated services over ~6 months with catalog-metadata updates.
>
> The pattern I now recognize earlier: *when teams ask for 'custom' or 'hybrid' tiers, the abstraction is collapsing*. The number of custom requests is the canary. If you see more than 2–3 per quarter, the axis underlying your 'tier' isn't really one axis anymore."

---

## Prompt 17 — A signal you missed

> *"Describe a situation where a platform problem was brewing for months and you didn't see it until it became a real issue. What was the signal, and why did you miss it?"*

### SRE trap

"I didn't have the right metric" — reveals no self-awareness. Most missed signals are missed because they weren't being *attended to*, not because they couldn't be measured.

### Platform framing

This is a prompt about attention, not instrumentation. Strong answers explore:

1. The problem that emerged and the consequence it had
2. The signal that had been visible — usually not a technical metric, often a qualitative one (team morale, specific-engineer-leaving, repeated small complaints that didn't pattern-match, rising ticket volume in a specific category)
3. Why you missed it — honest reflection, not self-flagellation
4. What you changed about your attention habit afterward

The best versions of this story don't involve a technical monitoring gap. They involve a blind spot in the candidate's own attention — over-focus on shipping vs listening, or on one team's feedback at the expense of a quieter team's, or on leading indicators of success but not leading indicators of decay.

### Coaching rubric (1–4 per criterion)

- **Signal was qualitative or systemic** — Not a standard metric; something subtler
- **Honest reason for missing it** — Reflection, not excuse
- **Consequence specified** — What the missed signal cost
- **Attention-habit change** — Named a specific practice that's different now
- **No self-flagellation** — Appropriate weight, not performative regret

Target: 3+ on each.

### Example shape

> "Over about 6 months, the platform team's ticket volume from one specific product group had been slowly rising. Not dramatically — from an average of 2 tickets per week to maybe 5. Each individual ticket seemed reasonable; each was resolved within a day. I was monitoring aggregate ticket volume and average resolution time, both of which looked healthy.
>
> What I wasn't monitoring was the *trend per tenant*. The rising ticket count from this one group was a leading indicator that they were hitting a systemic issue — a specific platform feature didn't fit their use case well, and they were compensating by asking us for one-off help. Each individual ask seemed fine; the *pattern* was that this team was accumulating a debt against the platform that was being paid in our one-off responses.
>
> When we noticed — after the team's tech lead wrote a frustrated message in Slack — we'd been absorbing ~4 hours per week of platform-team time specifically to cover for this mismatch, for 6 months. The cost was real and invisible.
>
> Why I missed it: I was looking at the platform's metrics (aggregate volume, MTTR on tickets) instead of at each tenant's experience of the platform. The platform team was healthy; one tenant's relationship with the platform was not.
>
> What I changed: monthly per-tenant ticket-volume and theme review. Spend 30 minutes once a month reading each team's tickets as a batch, looking for patterns. This surfaced two other mismatches in the first quarter after I started. The cost is real — 30 minutes per month is real time — but it's the cheapest leading indicator of platform-vs-tenant-fit I've found."

---

## How to use this file

1. Read all three prompts. Identify which story from your career each maps to.
2. For each, draft a version matching the example shape. Replace every scenario with your own.
3. Record yourself delivering each in 2–3 minutes. Listen back.
4. Score with the rubric. Note your weakest criterion across all three.
5. Revisit in Week 12 for the final polish.

### A note on telling failure stories

The common mistake on failure stories is under-weighting them — treating them as confessions to minimize. Strong candidates treat them as signals of senior judgment: *the fact that I know this is a failure, know specifically why, and changed something about my practice is exactly the signal you're asking for.* Don't apologize. Don't soften. Do claim the learning.

## Navigation

- Previous category: [04-influence-without-authority.md](04-influence-without-authority.md)
- Next category: [06-career-motivation.md](06-career-motivation.md)
- Back to: [stories/](README.md)
