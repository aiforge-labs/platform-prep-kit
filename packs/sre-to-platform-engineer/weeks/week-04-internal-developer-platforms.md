# Week 4: Internal Developer Platforms (IDP)

**Phase 2 — Technical Foundations**

> **Terms used in this week**
> - **SRE** — Site Reliability Engineer (the role you're transitioning *from*)
> - **Platform Engineer** — the role you're transitioning *to*
> - **IDP** — Internal Developer Platform
> - **PaaS** — Platform-as-a-Service; historically the external/commercial ancestor of the IDP (Heroku, Cloud Foundry)
> - **MVP** — Minimum Viable Product; used here as "minimum viable platform"
> - **CNCF** — Cloud Native Computing Foundation
> - **IaC** — Infrastructure-as-Code
> - **CRD** — Custom Resource Definition (Kubernetes); how most platform abstractions are expressed today
> - **Paved path / Golden path** — the opinionated, well-supported way a platform expects teams to build and ship
> - **TAG App Delivery** — CNCF Technical Advisory Group on Application Delivery; publishes the Platforms White Paper
>
> Full definitions and equivalent titles in the [pack README](../README.md#what-we-mean-by-sre).

Phase 2 shifts from mindset to tooling. Week 4 is the foundation: *what, concretely, is an Internal Developer Platform*. Not a product pitch, not an architecture diagram — a working definition you can defend in an interview and use to frame every subsequent technical week.

Most senior SREs enter platform-engineering interviews with an intuition for what an IDP is, but not a *model*. By end of this week you should have a model — components, interfaces, maturity levels — that you can apply to any org, including a company you've never worked at.

---

## Time commitment

~6–8 hours:

- Read: 2–3 hours
- Apply: 3 hours (design exercise — pen on paper counts)
- Articulate: 1 hour
- Self-assess: 30 minutes

## Learning objectives

By end of week you should be able to:

1. Name the core components of an IDP (developer control plane, integration/delivery, resource provisioning, observability, security/policy) and what each plane is responsible for
2. Distinguish a Platform-as-a-Service (PaaS) from an IDP, and explain *why the distinction matters* for an internal platform
3. Sketch a "minimum viable platform" for a 50-engineer org — without defaulting to a full Backstage-and-Crossplane stack
4. Compare three reference architectures (Backstage-centric, Humanitec-style orchestration, custom-built) on at least 4 axes — complexity, customization, team-size fit, lock-in
5. Identify the two or three platform capabilities that should *not* be built in-house at most orgs

---

## Read (2–3 hours)

The required material is short and dense. Don't skim — the definitions are the value.

### Required

**1. CNCF Platforms White Paper — capabilities section**
- [CNCF Platforms White Paper](https://tag-app-delivery.cncf.io/whitepapers/platforms/) — CC-BY, free. You read the early sections in Week 1; this week focus on Section 4 (Capabilities of Platforms) and Section 5 (Attributes of Good Platforms).
- 30–40 minutes.
- Focus on: the capability taxonomy (web portals, automation for golden paths, APIs and CLIs, observability, developer-friendly docs, a platform team structure). This is the vocabulary interviewers use.

**2. Internal Developer Platform reference architecture — the "five planes"**
- [internaldeveloperplatform.org reference architecture](https://internaldeveloperplatform.org/reference-architectures/) — free, practitioner-maintained.
- 30 minutes.
- Focus on: the five planes (Developer Control Plane, Integration & Delivery Plane, Resource Plane, Monitoring & Logging Plane, Security Plane). Map each to tools you already know — what plane is your current CI/CD in? Your service catalog?

**3. Backstage documentation — "What is Backstage?" and "Software Catalog" sections**
- [Backstage docs](https://backstage.io/docs/overview/what-is-backstage) — Apache 2.0, free.
- 20 minutes.
- Focus on: the three core concepts (Catalog, Scaffolder, TechDocs) and what *Backstage is not* (it is not a deployment tool; it is a portal and catalog).

**4. In-repo reference — `knowledge_packs/platform-engineering.md`**
- Revisit Section 2 (IDP Maturity Model) and any sections on reference architectures.
- 15 minutes. You need the vocabulary fresh for the Apply exercise.

### Recommended (pick one)

**5a. PlatformCon keynote on reference architectures**
- Search [PlatformCon](https://platformcon.com/) talks (prior years on YouTube) for "reference architecture" or "platform at scale." Pick a 30–45 minute talk.
- Focus on: the speaker's framing of *trade-offs* — what they deliberately chose not to build.

**5b. Humanitec's Platform Orchestrator whitepapers (public)**
- Humanitec publishes several whitepapers on platform orchestration. They are vendor-authored, but the *concepts* — workload specifications, resource graphs, dynamic configuration — are industry-standard and worth the read.
- Read critically: separate the pattern (platform orchestration as a distinct plane) from the product pitch.

### Why this source order

CNCF is the neutral reference — it is the citation that carries the most weight in interviews because it is vendor-agnostic and committee-authored.

internaldeveloperplatform.org gives you a reference architecture with enough specificity to be useful in whiteboard exercises. Every Platform Engineer interviewer you meet has seen the five-planes model, even if they don't name it.

Backstage documentation is essential because Backstage is the most commonly cited IDP portal in the wild (open-sourced by Spotify, now a CNCF incubating project). You don't need to love Backstage to interview for platform roles — but you do need to be able to describe what it does and what it doesn't do, without hand-waving.

---

## Apply (3 hours)

### Exercise: Design a Minimum Viable Platform

You are the first Platform Engineer hired at a 50-engineer product company (say, a B2B SaaS with a web app, a few backend services, and a mobile app). The engineering org has been running on Heroku-style deploys and a wiki of tribal knowledge. Leadership has asked for "a platform" and budgeted one Platform Engineer (you) plus one more hire in six months.

Design the platform.

#### Constraints

- You cannot build everything. Pick the 3–5 capabilities you will build *first*.
- You must ship something usable within 90 days.
- You are forbidden from building a "portal" as capability #1. (This constraint is deliberate and important — most new platform teams over-invest in portals before they have anything worth surfacing.)
- You must name at least one capability you will deliberately *not* build, and explain why.

#### Step 1: User problems first (30 min)

Before any tooling decision, write down 5–7 specific pain points the 50 product engineers are likely to have. Not "deploys are slow" — "new engineers take 4 days to ship their first code change because the README is stale and the deploy guide assumes AWS credentials they don't have."

Pull from your DevEx audit in Week 3 if useful, but adapt to this fictional org.

#### Step 2: Candidate capabilities (30 min)

List 8–12 platform capabilities you *could* build. Include the obvious ones (CI/CD, service scaffolding, secrets management) and the less-obvious ones (env parity for local dev, on-call rotation tooling, cost-attribution dashboards, a standard logging agent).

For each, note: which pain point(s) does it address? Is it *enabling* (removes a blocker) or *accelerating* (makes an existing flow faster)? Enabling capabilities almost always beat accelerating ones for a first-90-days platform.

#### Step 3: Pick 3–5 and sequence them (30 min)

Rank. For each, write:

- The one-sentence user value ("product engineers can spin up a new service with a single command, pre-wired for observability and deploys")
- The build approach — buy, adopt open source, or build — and why
- The first milestone you'd measure (adoption, time-saved, error-rate-before/after)
- The 90-day deliverable

If "buy" is an option you rejected, say *why*. "Too expensive" is rarely the full answer at this scale.

#### Step 4: Non-capabilities (20 min)

Explicitly name 2–3 capabilities you will *not* build in the first year.

Strong answers include: a visual portal (too early), a custom workflow engine (adopt something off-the-shelf), a secrets-management service (use the cloud provider's), a custom IaC abstraction layer (let teams use Terraform directly until pain emerges).

This is the single most important step. A senior platform engineer is defined by what they choose not to build.

#### Step 5: Reference architectures compared (40 min)

Now that you've designed your MVP, compare against three real-world reference patterns. For each, answer: would this pattern over-serve, under-serve, or fit your org?

- **Backstage-centric**: Backstage as the portal + catalog + scaffolder, with GitOps (Flux or Argo) handling deploys and Crossplane/Terraform handling infra.
- **Orchestration-centric** (Humanitec-style or custom): a workload-spec-driven orchestrator that reads an app manifest and composes env-specific resources. Portal is optional or minimal.
- **Light / "thin platform"**: a handful of scripts, golden-path repo templates, a shared CI workflow library, and explicit docs. No portal, no orchestrator.

At 50 engineers, the thin platform usually wins. Say so if it does; then say what would need to be true to justify moving to a heavier pattern.

#### Step 6: Synthesize (20 min)

Write half a page answering:

- What's the one capability whose failure to land would make your platform a failure?
- What would you measure at 90 days? At 6 months?
- If you got a second engineer today, what would they build *first*? (Hint: almost never the portal.)

### What good looks like

- Specific user problems, sourced from evidence (even fictional evidence counts if you name the source)
- 3–5 capabilities chosen with *stated trade-offs*, not a full wish-list
- At least two "we will not build this" entries with real reasoning
- A clear argument for a thin platform over a heavyweight stack at 50 engineers
- Metrics that are measurable at 90 days, not "improve DevEx"

### What weak looks like

- Starting with "we'll deploy Backstage and Crossplane and ArgoCD" — tools before problems
- Treating platform-engineering as *having* the tools rather than *solving* the problems
- No non-goals — platform capability list reads like a vendor brochure
- Metrics are all system-side ("reduce deploy time by 30%") with no user-facing signal
- Reference-architecture comparison is one-sentence hand-waves, not actual trade-off reasoning

---

## Articulate (1 hour)

### Prompt A

> *"Walk me through how you'd design a platform from scratch for a 200-engineer company that's currently running on ad-hoc scripts and tribal knowledge."*

This is Week 11's system-design prompt in miniature. Expect variants in every platform-engineering interview.

**SRE trap:**
Leaping into technology choices ("I'd deploy Backstage and use ArgoCD for GitOps…") before discussing users, problems, or constraints. Interviewers read this as *"hasn't designed a platform, has deployed one."*

**Platform framing:**
Start with discovery. "First 30 days I'd talk to 15–20 product engineers and 4–5 engineering leaders to understand the top five recurring friction points." Name a likely prioritization framework — enabling > accelerating, or impact × adoption ÷ effort. Only then discuss capabilities. And explicitly name the capabilities you would *not* build first, and why.

Example shape:
> "At 200 engineers, the pain is rarely 'no platform' — it's 'inconsistent platform.' I'd start by auditing what already exists. Then I'd pick the two or three capabilities where standardization would unlock the most team autonomy — typically a deploy-and-rollback mechanism, a service-scaffolding template, and a shared observability baseline. I'd deliberately defer a portal: portals matter once you have five or six capabilities worth surfacing, not before. For buy-vs-build, I'd lean on off-the-shelf for anything that isn't a point of differentiation — GitHub Actions or a CNCF CI tool for CI/CD, a managed secrets service, etc. The harder judgment calls are the platform-specific ones: whether to abstract cloud resources behind a workload spec, and whether to adopt something like Crossplane. At 200 engineers, I'd probably keep it direct — Terraform modules with clear ownership — and only introduce an abstraction layer when three or more teams explicitly ask for the same simplification."

### Prompt B

> *"Tell me about a platform capability that you shipped and later regretted — either because it didn't land or because it became a liability."*

This is a test of hindsight and systems thinking. Interviewers want to see whether you can critique your own output.

**SRE trap:**
Either "everything I shipped worked" (not credible) or blaming users ("teams wouldn't adopt it").

**Platform framing:**
Take a specific capability. Describe the assumption you got wrong about users, scope, or timing. What signal should have told you earlier? What would you have done differently — at the scoping stage, not the implementation stage?

Strong version includes the *second-order cost*: maintenance burden, opportunity cost, or the cultural expectation it set. Platforms don't just cost to build; they cost to keep.

### Self-check rubric

1–4 per prompt:

- **1** — Technology-first, no user framing
- **2** — Users mentioned but no prioritization reasoning
- **3** — Clear prioritization, at least one non-goal, tool choices justified
- **4** — Above plus: a surprising trade-off, a deliberate deferral, or an explicit acknowledgment of lock-in / maintenance cost

Target: 3+ on both. A "4" on Prompt A often distinguishes a strong IC Platform Engineer from a staff-level one.

---

## Self-assess (30 min)

### From the repo

```bash
prep quiz --topic platform-engineer --tag idp
```

Alternatively, review `quiz_banks/platform-engineer.json` for questions tagged `idp`, `backstage`, `five-planes`, or `platform-architecture`.

Target: 80%+.

### Reflection (write your answers)

1. If your current org handed you a platform mandate tomorrow, what are the top 3 capabilities you would build first? Order them by *user value*, not by what's most interesting to you.
2. What's one platform capability that looks attractive but is a maintenance trap? Why?
3. Name one platform you have used (internal or external) that felt "right." What specifically made it feel right? What was the interface?

---

## Outcome checkpoint

Before Week 5:

- [ ] Designed an MVP platform for a 50-engineer org, with 3–5 capabilities, sequencing, and explicit non-goals
- [ ] Compared three reference architectures (Backstage-centric / orchestration-centric / thin) with real trade-offs
- [ ] Can name the five IDP planes without lookup
- [ ] Can describe what Backstage *is not* in one sentence
- [ ] Can answer Prompt A with discovery-first framing, not technology-first
- [ ] Can answer Prompt B with a specific regret and a second-order cost
- [ ] Scored 80%+ on Week 4 quiz subset
- [ ] Wrote your three reflection answers

---

## Connections to later weeks

- Week 5 (GitOps at Scale) is where the Integration & Delivery Plane gets real
- Week 6 (Policy-as-Code) covers the Security Plane in detail
- Week 7 (Service Catalogs, Self-Service, Templates) takes Backstage's three concepts (Catalog, Scaffolder, TechDocs) and goes deep on the *product* design of each
- Week 11 (System Design Deep-Dive) revisits the MVP exercise at interview-scale
