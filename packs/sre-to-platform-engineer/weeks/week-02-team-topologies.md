# Week 2: Team Topologies

**Phase 1 — Mindset & Foundations**

> **Terms used in this week**
> - **SRE** — Site Reliability Engineer
> - **Platform Engineer** — the role you're transitioning to
> - **Team Topologies** — a book / framework by Matthew Skelton and Manuel Pais (2019) that classifies team types and their interactions; now common vocabulary in platform engineering
> - **Stream-aligned team** — a team aligned to a single, valuable stream of work (e.g., a product, feature set, or user journey)
> - **Platform team** — a team that provides internal products (platforms) consumed by stream-aligned teams
> - **Enabling team** — a team that helps other teams acquire missing capabilities, short-term
> - **Complicated-subsystem team** — a team that owns a subsystem requiring deep specialist knowledge (rare, narrow scope)
> - **Interaction mode** — how two teams work together: X-as-a-service, Collaboration, or Facilitating
> - **Cognitive load** — the total mental effort required of a team to do its work; a core constraint in Team Topologies design
>
> Full definitions and equivalent titles in the [pack README](../README.md#what-we-mean-by-sre).

Week 2 gives you the vocabulary Platform Engineers use to reason about organizational design. If you can't speak Team Topologies in an interview, you'll miss half of the non-technical questions — "how should your team interact with product teams?" is really asking "do you understand interaction modes?" without saying so.

This is still mindset work, not tooling. But the vocabulary you pick up here becomes the scaffolding for every later week.

---

## Time commitment

~6–8 hours total for the week:

- Read: 2–3 hours
- Apply exercise: 3 hours
- Articulate: 1 hour
- Self-assess: 30 minutes

## Learning objectives

By end of week you should be able to:

1. Name the four team types from Team Topologies and describe each in one sentence
2. Name the three interaction modes and explain when each is appropriate
3. Map your current org to team types — correctly, including where your org is fuzzy or misaligned
4. Recognize the "cognitive load" lens and apply it to team design decisions
5. Articulate why a Platform team is *not* just "infra team renamed" in Team Topologies terms

---

## Read (2–3 hours)

### Required

**1. Team Topologies Key Concepts**
- [teamtopologies.com/key-concepts](https://teamtopologies.com/key-concepts) — the authors' own free summary, 20 minutes.
- Read all four team-type pages and the interaction-modes page.
- Focus on: what distinguishes each type from the others; what problem each interaction mode solves.

**2. Team Topologies Reading List (GitHub)**
- [TeamTopologies/reading-list on GitHub](https://github.com/TeamTopologies/reading-list) — curated free resources, Apache 2.0 licensed.
- Pick 2–3 articles flagged "foundational" or "overview" from the reading list.
- Focus on: what problem each article says Team Topologies solves — the stated problem is the framework's strongest claim.

**3. Matthew Skelton / Manuel Pais talk (YouTube, public)**
- Search YouTube for "Team Topologies conference talk" and pick one 30–45 minute session from either author. Suggested entry points: "Team Topologies at PlatformCon" or "Team Topologies at QCon" — either year's talks are substantively similar.
- Focus on: how they frame the platform team's relationship to product teams, and where they draw the line between platform and product scope.

**4. CNCF Platforms White Paper (from last week) — Section 4**
- [CNCF Platforms White Paper, Section 4 Capabilities](https://tag-app-delivery.cncf.io/whitepapers/platforms/#what-should-platforms-provide) — the section you skimmed last week. Now read carefully, 20 minutes.
- Focus on: how platform *capabilities* map to interaction modes. (If a capability is self-service, the interaction mode is X-as-a-service; if it requires collaboration, that's a signal something is misaligned.)

### Recommended (pick one)

**5a. "Inverse Conway Maneuver" — Martin Fowler's blog**
- [Conway's Law on martinfowler.com](https://martinfowler.com/bliki/ConwaysLaw.html) — free, 10 minutes.
- Pairs naturally with Team Topologies: the *reason* team design affects architecture.

**5b. "The Team Topologies Playbook" — IT Revolution article excerpts**
- Search for any free excerpts or summaries of Team Topologies material published on IT Revolution or on Medium by recognized platform-engineering practitioners (Nicky Wrightson, Andrew Harmel-Law, Charity Majors, etc.).
- Focus on: practitioner commentary, not the authors' original material — to see how others apply the framework in practice.

### On the book itself

The full *Team Topologies* book by Skelton and Pais is not free (paid paperback / e-book). This week's required material covers the core concepts at sufficient depth for interview prep.

**If you enjoy this week and want to go deeper,** the book is a worthwhile investment — it contains organizational detail and case studies beyond what's available free. But it's not required for this pack; do not summarize or quote from the book in this repo.

---

## Apply (3 hours)

### Exercise: Team Topology Map of Your Current Org

This is a hands-on analytical exercise. Expect to spend 2–3 hours. You're not drawing a pretty org chart — you're diagnosing.

#### Step 1: Inventory (45 min)

List every engineering team in your organization. For each team, write down:

- Team name
- Team size (approximate)
- Primary output (what they ship or operate)
- Who consumes their output (other teams, end users, both)

Aim for honest classification. If a team's primary output is "supporting other teams," that's a clue they're not stream-aligned.

#### Step 2: Classify (45 min)

For each team, pick the best-fit Team Topologies classification:

- **Stream-aligned** — owns a value stream end-to-end; has a direct feedback loop with users of their output
- **Platform team** — provides internal products/services consumed by multiple stream-aligned teams; success = those teams self-serve
- **Enabling team** — helps other teams acquire missing capabilities, short-term; success = the recipient team no longer needs help
- **Complicated-subsystem team** — owns a subsystem needing deep specialist skill (ML model serving, kernel, cryptographic library); exists when cognitive load of owning the subsystem would overwhelm a stream-aligned team

Include "hybrid / unclear" as a valid classification. Many teams *in real orgs* are hybrids — the exercise is to notice this, not force-fit.

#### Step 3: Interaction Audit (45 min)

Pick the 5 most important team pairs (i.e., pairs that talk to each other the most). For each pair, classify the dominant interaction mode:

- **X-as-a-service** — Team A consumes something Team B provides, via well-defined interfaces, without needing Team B's ongoing attention
- **Collaboration** — Team A and Team B work closely together for a period, typically to discover or build something new; high communication, temporary
- **Facilitating** — One team coaches the other through a capability gap; should decrease over time

For each pair, also rate the *health* of the interaction 1–5 and write one sentence on what's working or not.

#### Step 4: Diagnose (45 min)

Write one page (you're not sharing this — it's analysis for you). Answer:

1. Which teams, if any, should be classified differently than their current identity suggests?
2. Where is Collaboration happening where X-as-a-service *should* be happening? (Classic sign of platform immaturity.)
3. Where is the biggest gap — a team type that doesn't exist in your org but probably should?
4. If you were given authority to reshape the org, what's the single highest-leverage change, and what would it unlock?
5. Where does your current role sit? If you're moving to Platform Engineer, what's the organizational shape you'd want to step into?

### What good looks like

- Honest classifications, including "unclear/hybrid" for teams that don't fit cleanly
- Specific examples for interaction-mode health (not generic "communication is hard")
- At least one finding that surprised you
- The diagnosis section reads like a Staff-Eng+ writeup — observations tied to consequences, not just description

### What weak looks like

- Classifying every team cleanly into one bucket (orgs are messier than the framework)
- Treating the framework as prescriptive ("we should have exactly these four types") rather than diagnostic
- Generic observations like "we need more collaboration" without naming specific teams or interactions

---

## Articulate (1 hour)

### Prompt A

> *"How should a platform team interact with product teams? What gets in the way when it goes wrong?"*

This question is asking whether you understand the X-as-a-service interaction mode and the failure modes around it.

**SRE trap:**
Describing the technical interface ("we give them APIs, runbooks, Slack channel") without naming the interaction principle. Or treating the platform team as "the team that helps product teams" — which is actually describing an Enabling team, not a Platform team.

**Platform framing:**
Lead with the principle: "Primarily X-as-a-service, with facilitating as a short-term bridge when teams are onboarding new capabilities, and very deliberately *not* collaboration as the default mode — because collaboration signals the platform hasn't made the underlying capability self-service yet."

Then name the failure modes specifically. The most common: platform teams that drift into ongoing collaboration mode — "we're here to help" — which feels helpful but is actually a sign the platform's abstractions are too leaky. Product teams can't self-serve, so they keep needing the platform team's attention. Over time, the platform team becomes a bottleneck or an Enabling team by accident.

**What good answers include:**
- The correct interaction mode labeled by name
- A specific failure mode named
- A metric for when the relationship is healthy (e.g., platform team shouldn't be in the critical path for product team deploys)

### Prompt B

> *"How do you decide what belongs in the platform vs what belongs in individual product teams?"*

This is the scope question. It's one of the two or three most common Platform Engineer interview prompts at senior levels.

**SRE trap:**
Over-generalizing ("anything reusable") or under-generalizing ("only the stuff that's literally shared infrastructure like Kubernetes and CI"). Both miss the framework's answer.

**Platform framing:**
Lead with cognitive load. A capability belongs in the platform when:
1. The cognitive load of owning it would overwhelm a typical stream-aligned team
2. Enough stream-aligned teams need the capability that economies of scale are real
3. Platformizing it doesn't sacrifice stream-aligned teams' autonomy for things they actually need to control

A capability belongs in the stream-aligned team when:
1. It's core to their value stream — they need to iterate fast on it
2. Generalizing it would add accidental complexity without meaningful reuse
3. Their cognitive budget can handle it

**What good answers include:**
- "Cognitive load" named explicitly
- A specific example of something that does *not* belong in the platform despite being tempting (a counter-example earns more trust than a positive example)
- Recognition that this is a judgment call with trade-offs, not a formula

### Self-check rubric

Score yourself 1–4 per prompt:

- **1** — Didn't use Team Topologies vocabulary
- **2** — Used vocabulary superficially
- **3** — Used vocabulary correctly; named at least one trade-off or failure mode
- **4** — Above plus: surfaced a non-obvious insight (e.g., a counter-example, a metric, a specific organizational pattern)

Target: 3+ on both.

---

## Self-assess (30 min)

### From the repo

```bash
prep quiz --bank platform-engineer --topic team-topologies
```

If that topic slug isn't in the quiz bank yet, review `quiz_banks/platform-engineer.json` for questions tagged `team-types`, `interaction-modes`, `org-design`, or `cognitive-load`.

Target: 85%+. If below, revisit the teamtopologies.com Key Concepts page — that's the lowest-effort highest-yield re-read.

### Reflection (write your answers)

1. In your Team Topology map, where did you find the biggest misalignment between a team's identity and what the framework says they should be?
2. In your org, is the concept of "cognitive load" ever invoked explicitly in planning? If not, name one decision that went wrong because cognitive load wasn't considered.
3. In your target Platform Engineer role, what's the most likely way *you* would drift away from X-as-a-service and into unintended Collaboration mode?

Keep these — they feed into STAR prompts later.

---

## Outcome checkpoint

Before Week 3:

- [ ] Completed Team Topology map of your current org, including honest "hybrid/unclear" calls
- [ ] Can name all 4 team types and 3 interaction modes without lookup
- [ ] Can answer Prompt A in under 3 minutes, naming X-as-a-service and at least one failure mode
- [ ] Can answer Prompt B in under 3 minutes, invoking cognitive load and giving a counter-example
- [ ] Scored 85%+ on the Week 2 quiz subset
- [ ] Wrote your three reflection answers

If you're below target on Prompt B, spend another 30 minutes specifically on that question before moving on. It's the highest-value articulation in Phase 1.

---

## Connections to later weeks

- Week 4 (Internal Developer Platforms) builds on team types — you can't design an IDP without knowing who consumes it
- Week 7 (Service Catalogs, Self-Service) is the technical expression of X-as-a-service
- Week 9 (Multi-tenancy) is where cognitive-load trade-offs become very concrete
- Week 12 (Behavioral) revisits Prompt B, because "scope" is one of the hardest behavioral topics to articulate

If anything from this week feels thin, don't dwell — it gets reinforced in context as later weeks apply it.
