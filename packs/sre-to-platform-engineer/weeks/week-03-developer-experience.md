# Week 3: Developer Experience (DevEx)

**Phase 1 — Mindset & Foundations**

> **Terms used in this week**
> - **SRE** — Site Reliability Engineer
> - **Platform Engineer** — the role you're transitioning to
> - **DevEx** — Developer Experience; the discipline of measuring and improving how product engineers experience their work
> - **DORA** — DevOps Research and Assessment; Google's research program that produces the annual "State of DevOps" reports and the four-key metrics framework
> - **DORA 4 keys** — Deployment Frequency, Lead Time for Changes, Change Failure Rate, Mean Time to Restore (MTTR)
> - **SPACE** — Framework for developer productivity measurement: Satisfaction, Performance, Activity, Communication, Efficiency (Forsgren, Storey, Maddila, Zimmermann, Houck, Butler)
> - **Three DevEx dimensions** — Flow state, Feedback loops, Cognitive load (Noda, Forsgren, Storey — follow-up to SPACE)
> - **MTTR** — Mean Time to Restore (or Recover); time from incident start to resolution
> - **NPS** — Net Promoter Score; a satisfaction measurement sometimes used internally for platform teams
>
> Full definitions and equivalent titles in the [pack README](../README.md#what-we-mean-by-sre).

Week 3 is the last of the mindset weeks. If Week 1 rewired how you think about output (system → product), and Week 2 gave you vocabulary for organizational design, Week 3 gives you a *measurement discipline*.

DevEx is where platform engineering meets product engineering meets research. It's a field with real academic foundations — not just vibes — and senior Platform Engineer interviews routinely probe whether you can reason about productivity as a measurable thing, not a feeling.

---

## Time commitment

~6–8 hours:

- Read: 2–3 hours (dense this week — papers and reports, not blog posts)
- Apply: 3 hours (real audit on a real workflow)
- Articulate: 1 hour
- Self-assess: 30 minutes

## Learning objectives

By end of week you should be able to:

1. Name the DORA 4 keys and explain what each measures — and what it doesn't
2. Name the 5 dimensions of SPACE and distinguish it from DORA
3. Articulate the 3 DevEx dimensions (flow, feedback, cognitive load) and when each is the right lens
4. Audit a real developer workflow and identify friction mapped to DevEx dimensions
5. Avoid the two most common DevEx traps: measuring activity (lines of code, commits) and optimizing for vanity metrics

---

## Read (2–3 hours)

Order matters this week — DORA first, then SPACE, then DevEx. Each paper builds on the previous.

### Required

**1. DORA — Accelerate State of DevOps 2023 Report (or latest)**
- [dora.dev](https://dora.dev/research/) — reports are free PDFs, no registration required.
- 45 minutes. Read the Executive Summary and the 4-keys methodology section.
- Focus on: what each metric claims to measure, and the distribution of organizations across the performance tiers (elite / high / medium / low).

**2. SPACE Framework paper (ACM Queue)**
- ["The SPACE of Developer Productivity" by Forsgren, Storey, Maddila, Zimmermann, Houck, Butler](https://queue.acm.org/detail.cfm?id=3454124) — freely accessible on ACM Queue.
- 30–40 minutes. This is an academic paper; read it carefully, not as skim.
- Focus on: the critique of single-metric productivity measurement, and the 5 SPACE dimensions with at least one example metric per dimension.

**3. "DevEx: What Actually Drives Productivity" (ACM Queue)**
- ["DevEx: What Actually Drives Productivity" by Noda, Forsgren, Storey](https://queue.acm.org/detail.cfm?id=3595878) — freely accessible on ACM Queue.
- 30 minutes. The natural successor to SPACE — same lead authors, practitioner-oriented.
- Focus on: the three DevEx dimensions (flow, feedback, cognitive load) and how they relate to the SPACE framework.

**4. In-repo reference — `knowledge_packs/sre-fundamentals.md`**
- Skim any sections on SLOs, reliability metrics, and MTTR — you'll need the SRE vocabulary fresh for the Apply exercise and for contrasting reliability metrics with productivity metrics.
- 15 minutes.

### Recommended (pick one)

**5a. Google Engineering Productivity Research blog posts**
- [Google Research — Engineering Productivity](https://research.google/research-areas/software-engineering/) — search for posts by Nicole Forsgren, Ciera Jaspan, Caitlin Sadowski, Emerson Murphy-Hill.
- Pick one that resonates and read it carefully.
- Focus on: how Google's internal DevEx research is conducted and what questions they ask.

**5b. Stripe / Shopify / LinkedIn public engineering blog on internal developer productivity**
- Each of these companies publishes some public material on their internal DevEx work. Search for "Stripe developer productivity", "Shopify internal tooling", "LinkedIn developer platform" on their engineering blogs.
- Pick one post and read it critically.
- Focus on: what they measure, how they decided what to measure, and what they changed as a result.

### Why this source order

DORA is the baseline — every serious platform-eng conversation references it, whether positively or critically. Read it first so you know what people are reacting to.

SPACE is the considered academic critique of "reduce-productivity-to-a-number" thinking. Essential for senior interviews — your interviewer has almost certainly read it, or at least heard of it.

DevEx (the Noda/Forsgren/Storey paper) is the current practitioner synthesis. It's the most directly useful framework for day-to-day platform work. The authors are the right authors — Forsgren co-authored DORA's Accelerate book and the SPACE paper.

---

## Apply (3 hours)

### Exercise: DevEx Audit on a Real Workflow

Pick one workflow in your current org that product engineers do regularly. Candidates:

- Creating a new service from scratch
- Deploying a change to production
- Debugging an issue that reproduces only in staging
- Onboarding a new engineer to their first code change
- Running local tests before a PR
- Getting observability set up for a new feature

Pick one. **Do not pick the workflow that's obviously broken.** Pick one that's *okay* — because auditing something that's already "fine" is harder and more revealing.

#### Step 1: Document the current flow (45 min)

Write down the literal steps. Not the ideal — what actually happens. Include:

- Every tool the developer touches
- Every approval or handoff
- Every wait (e.g., "CI takes 14 minutes to run")
- Every context switch
- Every opportunity to get confused or lost

If you aren't sure of any step, find out — ask a teammate, walk through it yourself, read the internal docs. Don't guess.

Aim for 15–40 steps written at the level of what a developer perceives, not what the system does.

#### Step 2: Identify friction (45 min)

For each step, annotate:

- **Flow-state risk** (1–5): does this step break the developer's concentration?
- **Feedback-loop length**: how long until they know if they did the right thing?
- **Cognitive load**: what do they need to remember or figure out to complete this step correctly?

Highlight the 5 worst steps. These are your friction hot-spots.

#### Step 3: Map to frameworks (30 min)

For each friction hot-spot, classify:

- Which DevEx dimension is most affected? (Flow, Feedback, Cognitive load)
- Which SPACE dimension does this degrade? (Often Efficiency or Satisfaction, but not always.)
- Is this measurable with a DORA key? (Usually at most one is.)

This forces you to notice: DORA alone *misses most friction*. A workflow can score well on DORA's 4 keys and still be miserable to use. That insight is worth the exercise.

#### Step 4: Propose interventions (30 min)

For your 5 hot-spots, write one proposed improvement each. For each, rate:

- **Effort** (1–5)
- **Impact** (1–5)
- **Risk** (1–5) — what could go wrong, who needs to buy in

Rank by effort:impact ratio. Your top 2 are your "if I had one sprint" list. Your bottom 2 are "nice to have" — be honest about that.

#### Step 5: Synthesize (30 min)

Write half a page answering:

- What's the highest-leverage intervention, and why?
- What would you measure *before and after* to prove impact?
- What would you *not* fix, and why?
- If this workflow is typical, what does that say about your org's DevEx maturity?

Keep this. It's STAR-story material for weeks 11–12.

### What good looks like

- Step-by-step documentation that a new hire could follow
- Friction ratings that are specific, not uniformly "high"
- At least one intervention where you explicitly chose *not* to do something
- Recognition that DORA metrics wouldn't capture most of the friction you found

### What weak looks like

- High-level framing ("deploys are slow")
- Generic improvements ("automate it" without specifying what or how)
- Ignoring measurement — "trust me, it would be better"
- Treating DORA as the full answer

---

## Articulate (1 hour)

### Prompt A

> *"Tell me about a time you improved developer productivity. How did you measure the impact?"*

Interviewers listen for: measurement discipline, honest scope, and an awareness of what *didn't* work.

**SRE trap:**
Describe a tool or automation and claim it "saved time" without a number. Or use a system metric (CI duration, deploy time) as a proxy for productivity without acknowledging the proxy.

**Platform framing:**
Start with the problem and how you knew it was real (data or qualitative signal). Name the dimension you targeted (flow, feedback, cognitive load, or one of SPACE's five). Describe the intervention and — critically — *what you measured before and after*. Include at least one thing that didn't go as expected.

Example shape:
> "Our product teams reported that setting up a new service took two full days on average. We validated this with a quick timed study — 5 teams, measured in hours not story points. The biggest friction was cognitive load: a new service required touching 11 different repos and 4 different tools, and most of that was boilerplate. We built a scaffolder that reduced it to 40 minutes. Post-implementation we re-measured: median 35 minutes, 90th percentile 90 minutes — an outlier team had a legitimate edge case we'd missed. Bigger learning was that "developer time saved" wasn't actually the right metric; the real win was that teams were now willing to create services more freely, because the cost was lower. We tracked service-creation rate as a leading indicator for architectural flexibility."

### Prompt B

> *"What's the biggest DevEx problem in your current org, and why hasn't it been fixed?"*

This is a test of honesty and systemic thinking. Candidates who can't answer it convincingly suggest they haven't looked hard at their own org.

**SRE trap:**
Either "we don't really have DevEx problems" (an obvious mis-read) or a laundry list without prioritization.

**Platform framing:**
Pick one specific friction. Describe it at the step-level, not at the abstract level. Explain *why it hasn't been fixed* in terms of organizational dynamics — missing ownership, unclear funding, competing priorities, technical complexity, political cost. Acknowledge that "nobody cares" is almost never the real answer; usually it's "no team has clear authority and budget to own it."

This is where "why platform engineering?" starts to answer itself — a good answer to this prompt is a candidate who thinks structurally about DevEx, not just tactically.

### Self-check rubric

1–4 per prompt:

- **1** — No measurement mentioned, or only system-side metrics
- **2** — Metric mentioned but not connected to a user outcome
- **3** — User-facing metric, honest about scope and limitations
- **4** — Above plus: acknowledges a surprise, a mistake, or a counter-intuitive finding

Target: 3+ on both. A "4" on Prompt A is particularly impressive in interviews.

---

## Self-assess (30 min)

### From the repo

```bash
prep quiz --topic platform-engineer
```

Alternatively, review `quiz_banks/platform-engineer.json` for questions tagged `dora`, `space`, `devex`, or `productivity-metrics`.

Target: 80%+.

### Reflection (write your answers)

1. In your current org, what DORA keys do you actually know — with data — vs. guess? Be honest.
2. Which of the 3 DevEx dimensions (flow, feedback, cognitive load) is most under-invested-in where you work?
3. Based on your DevEx audit exercise, if your platform team had one engineer-month of capacity, where would the highest ROI come from?

---

## Outcome checkpoint

Before Week 4:

- [ ] Completed DevEx audit on a real workflow, with steps, friction ratings, and prioritized interventions
- [ ] Can name DORA 4 keys, SPACE 5 dimensions, and DevEx 3 dimensions without lookup
- [ ] Can explain *why* SPACE was written as a critique of single-metric productivity — not just what it says
- [ ] Can answer Prompt A with at least one before/after metric and one surprise
- [ ] Can answer Prompt B with one specific friction and a structural (not just technical) explanation
- [ ] Scored 80%+ on Week 3 quiz subset
- [ ] Wrote your three reflection answers

---

## Phase 1 wrap-up

Weeks 1–3 are the mindset shift. If they went well, you should notice:

- You no longer reflexively describe systems — you describe users and problems first
- You have vocabulary (stream-aligned, X-as-a-service, cognitive load, DORA/SPACE/DevEx) that Platform Engineers actually use
- You can articulate *why* reliability alone is not enough for a platform

If any of that doesn't feel true yet, spend the weekend reviewing the weakest week before starting Week 4. Phase 2 gets technical fast — Internal Developer Platforms, GitOps at scale, policy-as-code. You don't want to layer tooling onto shaky foundations.

## Connections to later weeks

- Week 8 (Observability as a Platform Product) re-uses DevEx framing applied to telemetry
- Week 11 (System Design Deep-Dive) expects DORA/SPACE vocabulary to be reflexive
- Week 12 (Behavioral) revisits Prompts A and B — sharpen them here, polish them there
