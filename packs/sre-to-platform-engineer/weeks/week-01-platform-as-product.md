# Week 1: Platform as a Product

**Phase 1 — Mindset & Foundations**

> **Terms used in this week**
> - **SRE** — Site Reliability Engineer (the role you're transitioning *from*)
> - **Platform Engineer** — the role you're transitioning *to*
> - **IDP** — Internal Developer Platform
> - **SLO** — Service Level Objective
> - **CNCF** — Cloud Native Computing Foundation
>
> Full definitions and equivalent titles in the [pack README](../README.md#what-we-mean-by-sre).

The single biggest distinction between a Platform Engineer and a Site Reliability Engineer (SRE) is not technical. It's a shift in how you think about your output: from "a system that's reliable" to "a product that internal teams choose to use." This week is about rewiring that mental model before we touch any platform tooling.

---

## Time commitment

~6–8 hours total for the week, spread across 3–5 sessions:

- Read: 2–3 hours
- Apply exercise: 2–3 hours
- Articulate (practice STAR prompts): 1 hour
- Self-assess: 30 minutes

## Learning objectives

By end of week you should be able to:

1. Explain what Platform Engineering is — and how it's distinct from DevOps, SRE, and Infrastructure Engineer — in 90 seconds, without hand-waving
2. Define your platform's "users" in terms that a product manager would recognize (personas, JTBD, adoption metrics)
3. Distinguish "we built a platform" from "teams use our platform" — and articulate why the gap matters
4. Identify at least one tool or automation you've already built as an SRE, and re-frame it in product-thinking language

---

## Read (2–3 hours)

Work through these in order. All sources are publicly accessible and permissively licensed or free-to-read.

### Required

**1. Platform Engineering overview — platformengineering.org**
- [Platform Engineering community site](https://platformengineering.org/blog/what-is-platform-engineering) — the "What is Platform Engineering?" intro post. 15 minutes.
- Focus on: the distinction between a platform-as-output and a platform-as-product.

**2. Internal Developer Platform reference — internaldeveloperplatform.org**
- [IDP definition and reference architecture](https://internaldeveloperplatform.org/what-is-an-internal-developer-platform/) — 20 minutes.
- Focus on: the "five planes" model (developer control plane, integration plane, resource plane, monitoring plane, security plane). You don't need to memorize it, but recognize the components.

**3. CNCF Platforms White Paper**
- [CNCF Platforms White Paper](https://tag-app-delivery.cncf.io/whitepapers/platforms/) — free, CC-BY. 30–40 minutes.
- Focus on: Sections 1–3 (what a platform is, why organizations build them, what makes them good or bad). Skim Section 4 (capabilities).

**4. In-repo reference — `knowledge_packs/platform-engineering.md`**
- Sections 1 and 2: Platform Engineering vs DevOps vs SRE comparison table, and IDP Maturity Model.
- 15 minutes. Especially useful as a compact summary you can reference later.

### Recommended (pick one)

**5a. Humanitec "Platform Engineering Fundamentals" whitepaper**
- [Humanitec Platform Engineering Fundamentals](https://humanitec.com/whitepapers) — free PDF, registration may be required. Alternative: most of the same material is restated in their public blog posts.
- Focus on: the organizational dynamics of platform teams, not the Humanitec product pitch.

**5b. PlatformCon keynote talks (YouTube, public)**
- Pick one 30–45 minute talk from [PlatformCon](https://platformcon.com/) (prior-year keynotes are on YouTube).
- Suggested: any of the "state of platform engineering" keynotes from the last 2 years.
- Focus on: how the speaker frames platform engineering to a non-technical executive audience.

### Why these sources

- **platformengineering.org** is community-run and the closest thing to a canonical definition that isn't vendor-captured.
- **internaldeveloperplatform.org** is maintained by practitioners and gives you a vocabulary your interviewer is likely to use.
- **CNCF white paper** is the neutral, vendor-agnostic reference — carries weight in any conversation.
- **Humanitec** and **PlatformCon** add practitioner color; they also show you what industry voices sound like.

You'll notice all four required sources spend significant space on *why platforms fail*. That's not rhetorical. Most platform engineers interview against stories of platforms that didn't land. Weeks 1–3 are partly about understanding why.

---

## Apply (2–3 hours)

### Exercise: Platform Product Brief

Pick one internal tool, automation, or system you've built or materially contributed to as an SRE. It can be anything from a deploy script to a monitoring abstraction to a cluster-provisioning workflow. Size doesn't matter — familiarity does.

Write a one-page "Platform Product Brief" for it. Use this template:

```
# Platform Product Brief: [Name]

## Elevator pitch (2 sentences)
What is this, and what's the core problem it solves?

## Users (who, not what)
- Primary users: which roles / teams
- Secondary users: who else touches it
- Non-users: who we explicitly do not serve (this is important)

## Jobs to be done (2–4)
What were your users trying to accomplish when they reached for this?
Phrase each as "When [situation], I want to [motivation], so I can [outcome]."

## Success metrics (3 max)
How would you know if this is working? Not "uptime" — user-centric metrics.
- Adoption: how many teams / how many uses per week
- Experience: time saved, errors avoided, or satisfaction signal
- Platform health: something that you, the operator, care about

## Roadmap (next 3 items, prioritized)
If you had one more engineer for a quarter, what would you build?
Rank by user value, not by technical interest.

## Explicit non-goals
What are you NOT going to build, and why?

## Risks / open questions
What could cause this to fail? What would you need to validate?
```

### What good looks like

A strong brief:
- Names specific teams, not "developers" in general
- Has at least one user-centric metric (adoption, satisfaction, time-saved) — not just system metrics
- Has explicit non-goals — this is the single biggest tell of product thinking
- Reads like a brief a PM would write, not like an RFC or runbook

### What weak looks like

A weak brief (common SRE-style):
- Describes the system, not the user problem
- Success metrics are all system-side (uptime, latency, error rate)
- No non-goals — treats scope as open-ended
- Roadmap reads like "things we could add" instead of "things users need"

### Anti-cheat

It's tempting to use an AI tool to generate this brief. Don't — or at least, don't do it first. The exercise is training *your* brain to frame work in product terms. An AI-generated brief skips the step where your mental model rewires. Use AI to critique your draft, not to produce it.

---

## Articulate (1 hour)

Interview-style prompts. Speak them aloud; time yourself. Each answer should be 2–3 minutes. Record yourself if you can — the gap between how you think you sound and how you actually sound is almost always larger than expected.

### Prompt A

> *"Walk me through a platform, tool, or automation you've built. Who were the users, and how did you measure success?"*

**SRE trap (how this typically gets answered, and why it reads weak):**
The candidate describes the system architecture — "so we had a Kubernetes operator that reconciled custom resources..." — and measures success by reliability metrics ("we had 99.95% uptime"). The interviewer's eyes glaze over because the answer is about the system, not about the people who used it or didn't use it.

**Platform framing (what the interviewer is listening for):**
Start with the user and the problem. "Our product teams were spending 2–3 days per service setup, and half of them skipped steps. I built [X]. The users were team leads and service owners. I measured success by the percentage of new services that went through the tool in the first 30 days — target was 80%, we hit 72% in Q1 and 91% in Q2. The bigger learning was about the 9% who opted out: they had a legitimate case we hadn't supported."

### Prompt B

> *"Tell me about something you built that didn't get the adoption you hoped for. What happened?"*

This is the classic "teach me to think like a PM" interview question. Almost every SRE has one of these stories; almost none tell it well.

**SRE trap:**
Either avoids the question ("it worked, it just wasn't used") or blames users ("teams were resistant to change"). Both are career-limiting answers.

**Platform framing:**
Take responsibility. What did you not understand about users, constraints, or adoption before building? What signal did you miss? What would you do differently — not just technically, but in terms of discovery, buy-in, or scoping?

> The unexpected lesson I didn't see until six months later was that teams weren't resisting the tool; they were resisting what the tool was signaling — that we expected them to own more operational work. We'd built the right tool for the wrong target state.

That kind of reflection is what earns the interviewer's trust.

### Self-check rubric

For each prompt, score yourself 1–4:

- **1** — Described the system, not the users
- **2** — Named users but no user-centric metric
- **3** — User-centric framing, clear metric, clean structure
- **4** — Above plus: surfaced a non-obvious insight or trade-off

Target: 3+ on both by end of week.

---

## Self-assess (30 min)

### From the repo

Run the platform-engineer quiz, focused on Week 1 topics:

```bash
prep quiz --topic platform-engineer --tag platform-as-product
```

Alternatively, review `quiz_banks/platform-engineer.json` for questions tagged `platform-as-product`, `platform-vs-sre`, or `adoption`.

Target: 80%+ correct. If below, re-read the CNCF whitepaper Section 2–3 before moving on.

### Reflection (write down your answers — don't just think them)

1. On a 1–5 scale, how product-oriented is your current role? What specifically moves the needle up or down?
2. Name one tool or automation in your current org (built by anyone) that has low adoption despite being technically sound. What would a Platform PM's diagnosis look like?
3. If your current SRE team was given a product mandate tomorrow, what would change about how you work in the first 30 days?

These reflections become raw material for STAR stories (milestone 1.4). Keep them.

---

## Outcome checkpoint

Before moving to Week 2, verify:

- [ ] Wrote a Platform Product Brief for a real system you know
- [ ] Can answer Prompt A in under 3 minutes, with a user-centric metric, and not drift into architecture
- [ ] Can answer Prompt B without blaming users or dodging the question
- [ ] Scored 80%+ on the Week 1 quiz subset
- [ ] Wrote your three reflection answers

If any of these is a no, don't rush to Week 2. The mindset from this week is the foundation for the rest of the plan.

---

## Further reading (optional, for depth)

- *Team Topologies* by Matthew Skelton & Manuel Pais — book, paid. We cover its core concepts in Week 2 from free sources, but the full book is a strong investment if this direction feels right.
- *Empowered* by Marty Cagan — product management classic; if you've never read PM material, this is the shortest path to thinking like one.
- DORA / Accelerate research — freely available reports from Google's DORA team on what drives high-performing software orgs. Light on platform specifics, foundational for Week 3's DevEx material.

Don't read these this week — Week 1's required material is enough. Note them for after the pack, when you want to go deeper.
