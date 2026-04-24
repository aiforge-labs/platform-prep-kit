# Week 7: Service Catalogs, Self-Service, Templates

**Phase 3 — Platform-Specific Design & Ops**

> **Terms used in this week**
> - **SRE** — Site Reliability Engineer
> - **Platform Engineer** — the role you're transitioning to
> - **Service catalog** — a canonical inventory of services (and sometimes other components: APIs, libraries, resources) with metadata, ownership, and discoverability
> - **Scaffolder** — a tool that generates a new service from a template with opinionated defaults (Backstage's term; GitHub also calls template-instantiation scaffolding)
> - **Golden path** / **Paved path** — the opinionated, well-supported way a platform expects teams to build and ship
> - **Backstage** — CNCF incubating portal project, Apache 2.0, open-sourced by Spotify
> - **TechDocs** — Backstage's docs-as-code feature; renders Markdown living alongside service code
> - **IDP** — Internal Developer Platform
> - **IaC** — Infrastructure-as-Code
> - **CRUD** — Create, Read, Update, Delete
> - **PaaS** — Platform-as-a-Service
> - **CODEOWNERS** — GitHub's file-path-to-owner mapping for review requirements
> - **SBOM** — Software Bill of Materials
>
> Full definitions and equivalent titles in the [pack README](../README.md#what-we-mean-by-sre).

Phase 3 starts the shift from "how the platform works" to "how the platform is *consumed*." Week 7 is the biggest leap of the whole pack: it's where platform engineering visibly becomes product engineering for internal users. The core deliverable of a mature platform — what developers actually interact with — is a service catalog and the self-service flows around it.

The catalog isn't just a list. It's where discovery, ownership, scaffolding, documentation, and ops tooling converge. Designed well, it makes the platform feel like one thing. Designed poorly, it's a stale wiki masquerading as a product.

---

## Time commitment

~6–8 hours:

- Read: 2 hours
- Apply: 3 hours (design exercise with optional hands-on)
- Articulate: 1 hour
- Self-assess: 30 minutes

## Learning objectives

By end of week you should be able to:

1. Describe the three things a service catalog is actually for (discovery, ownership, operational context) and the two things it is not (documentation index, status page)
2. Design a catalog schema for a realistic org — entities, relationships, required vs optional metadata — without over-modeling
3. Build (or design) a scaffolder that handles 80% of new-service creation without configuration and 20% with sane defaults
4. Decide where to be opinionated vs flexible, and articulate the principle behind that decision
5. Recognize the catalog-decay problem (metadata rot) and design against it
6. Distinguish Backstage as *portal* vs Backstage as *catalog engine* — and know when each is the right answer

---

## Read (2 hours)

### Required

**1. Backstage Software Catalog — concepts and descriptor format**
- [Backstage Catalog documentation](https://backstage.io/docs/features/software-catalog/) and the [descriptor format](https://backstage.io/docs/features/software-catalog/descriptor-format/) — Apache 2.0, free.
- 45 minutes.
- Focus on: the entity model (Component, System, Domain, API, Resource, User, Group) and the relationship types (`ownedBy`, `partOf`, `providesApi`, `consumesApi`). This is the most widely-used catalog schema today; even teams that don't use Backstage often borrow from it.

**2. Backstage Scaffolder (Software Templates)**
- [Backstage Software Templates documentation](https://backstage.io/docs/features/software-templates/) — Apache 2.0, free.
- 30 minutes.
- Focus on: the template lifecycle (fetch → transform → publish → register), what default actions exist, and how parameters surface to users as a form.

**3. TechDocs concept and workflow**
- [Backstage TechDocs](https://backstage.io/docs/features/techdocs/) — Apache 2.0, free.
- 20 minutes.
- Focus on: docs-as-code — living in the service repo, rendered via MkDocs, surfaced in the catalog. The design insight is that docs decay when they live anywhere else.

**4. CNCF Platforms White Paper — capabilities recap**
- Revisit Section 4 (capabilities) of the [CNCF Platforms White Paper](https://tag-app-delivery.cncf.io/whitepapers/platforms/), focused on the catalog, discovery, and self-service capabilities.
- 20 minutes.

**5. In-repo reference — `knowledge_packs/platform-engineering.md`**
- Section on service catalogs and self-service flows.
- 15 minutes.

### Recommended (pick one)

**6a. A real Backstage case study (public talk or blog)**
- Search for public talks: "Backstage at [company]" — Spotify, Expedia, American Airlines, HashiCorp, and others have public material.
- 30 minutes.
- Focus on: the *organizational journey* of rolling out a catalog — what broke, what they de-scoped, how they populated it. Not the Backstage-is-great tour.

**6b. An alternative catalog approach**
- OpsLevel, Cortex, Port, Port's open-source "developer portal" examples, or Kratix are all non-Backstage patterns worth a quick look. Many have public blog posts that describe their model without requiring a product purchase.
- 30 minutes.
- Focus on: what they chose to be *different* from Backstage, and the implicit critique of Backstage's model that their difference implies.

### Why this source order

Backstage-first isn't because Backstage is always the right answer. It's because Backstage is the *reference model*. Any platform-engineering interview conversation about catalogs will assume you can think in Backstage's vocabulary — Components, Systems, Owners, APIs — whether you use Backstage or not.

TechDocs is worth reading even if you're sure your org won't use it. The *principle* (docs live with the code, in a standard format, rendered by the platform) applies regardless of tool. Most catalog-rollout failures include some version of "we built the catalog and the docs got stale within a quarter." TechDocs is one answer.

---

## Apply (3 hours)

### Exercise: Design a Service Catalog and Scaffolder for a Realistic Org

You are the Platform Engineer at a 150-engineer org with ~80 services across ~20 teams. The services were built over 7 years by different teams with different conventions. No one has a single view of "what services exist." Ownership is partly in the README, partly in Slack channels, partly in nobody's head.

Design the catalog and the first three scaffolder templates.

#### Part A — Catalog schema (60 min)

Decide:

1. **Entity types.** Start with Backstage's core set (Component, System, Domain, API, Resource, User, Group). Which ones will you actually use? Which would over-model your org? Cut ruthlessly — a catalog with 12 entity types nobody maintains is worse than a catalog with 3 that do.

2. **Required metadata.** For each entity you keep, what metadata is *required*? Default suggestions: owner (Group), lifecycle (production / experimental / deprecated), language/stack (free text), and a short description. Avoid required fields nobody will fill reliably.

3. **Optional but common metadata.** What's useful but not blocking? Dependencies, on-call info, runbook links, dashboards, API specs, lifecycle-owner (the human champion separate from the team), SBOM reference.

4. **Relationships.** Which relationships will you capture (e.g., `dependsOn`, `ownedBy`, `partOf`, `providesApi`)? Which will you *not* capture because you can't keep them accurate?

5. **Source of truth.** Where does this metadata live? In the service repo (catalog-info.yaml per Backstage convention)? In a separate metadata repo? Both? Pick and defend.

#### Part B — Population strategy (30 min)

You have 80 services today, mostly without catalog metadata. Design the population flow:

1. **Discovery** — how do services get *found*? (Backstage has built-in GitHub/GitLab discovery; you can also script a one-time crawl.)
2. **Bootstrap** — what's the minimum required for an existing service to be "registered"? Resist the urge to require too much on day one.
3. **Gap-filling** — how do you get from "we have 80 services with the minimum metadata" to "we have 80 services with *usable* metadata"? Who fills in the gaps and when?
4. **The catalog-decay problem** — how do you prevent metadata from going stale? Options: CODEOWNERS-style automated reviews, quarterly attestation, automated scans (e.g., a service with no commits in 6 months flagged as potentially-abandoned), linking service creation to owner-team onboarding.

#### Part C — Three scaffolder templates (60 min)

Design (in outline form) the first three templates your platform will offer. Pick from common new-service starters:

- HTTP backend service (Go, or your org's standard language)
- Event-driven worker / consumer service
- Internal library / shared module
- Frontend application (React, Vue — pick one standard)
- Data pipeline / batch job
- ML-inference service

For each template:

1. **Scope** — what does the template create? (Repo, initial code, CI/CD config, deployment manifests, observability baseline, catalog entry?)
2. **Defaults vs parameters** — what's hardcoded, what's a prompt, what's an optional override?
3. **What the template *doesn't* include** — explicit non-goals (e.g., "this template doesn't include a database; if you need one, request a resource through the Resource Catalog")
4. **Opinionation** — where are you being prescriptive and where are you being flexible? One principle that's useful: *opinionated for the first 80% of teams; escape hatches for the remaining 20%.*

#### Part D — The opinionation question (30 min)

Write half a page answering:

1. Where does your platform deliberately *not* give developers flexibility, and why?
2. What's your escape hatch for teams that legitimately need to deviate?
3. What's the cost of an escape hatch becoming the default? (Hint: "configuration sprawl.")
4. If you had to pick one dimension — speed to first production deploy, developer satisfaction, operational consistency — that your catalog+scaffolder optimizes for, which and why?

### What good looks like

- Fewer entity types than Backstage's default, with explicit cuts and reasons
- Required metadata that's realistic (ownership, lifecycle) — not a wishlist
- Population strategy that acknowledges decay as a first-class problem
- Scaffolder templates with explicit non-goals
- A clear principle for opinionation that a reasonable team could disagree with

### What weak looks like

- Adopting Backstage's full entity model uncritically
- Scaffolder templates that try to handle every possible case (configuration sprawl)
- No plan for metadata decay
- Escape hatches that become default paths
- "Flexibility" as an unquestioned virtue — no acknowledgment that flexibility has a cost

### Optional hands-on extension

If you have time and haven't used Backstage before: spin up Backstage locally following the [getting started guide](https://backstage.io/docs/getting-started/). Register one real (or fictional) service with a `catalog-info.yaml`. Add one scaffolder template. This is 2–3 hours on its own — skip if your design exercise already took the full 3 hours.

---

## Articulate (1 hour)

### Prompt A

> *"Walk me through how you'd roll out a service catalog to an org that's currently using a wiki page for the same purpose."*

This is a DevEx-meets-change-management question. Interviewers want to see whether you understand that the catalog's value only lands if it actually gets populated.

**SRE trap:**
"We'd deploy Backstage and run a crawler that auto-discovers services." Technically fine, operationally empty. Ignores the question of *why the wiki exists*, *what people use it for*, and *whether Backstage's model fits those actual uses*.

**Platform framing:**
Start by asking what the wiki is actually used for. Usually it's three things mashed together: ownership lookup, on-call routing, and new-hire orientation. Each of those has different success criteria. Then:

1. Pick one user job the wiki does *badly* — usually ownership lookup gets stale fast — and prove the catalog does it better.
2. Migrate incrementally. Don't shut down the wiki on day one.
3. Measure: "catalog lookups per day," "services with current metadata," "wiki page edits per week" (should drop as catalog takes over).
4. Handle the political friction: the wiki has owners, too. Talk to them, not past them.
5. Be honest about what the catalog *won't* do as well as the wiki — long-form context, informal team notes, runbooks that aren't paved-path.

### Prompt B

> *"What's an opinionated default in a platform you've built or used that turned out to be the wrong opinion?"*

A test of hindsight and humility.

**SRE trap:**
Either "our defaults were all fine" (not credible) or a minor example ("we defaulted to CPU requests of 100m and it turned out 50m was enough").

**Platform framing:**
Pick a default that had organizational consequences, not just technical ones. Good candidates:

- A required language or framework that was right at the time but didn't survive a technology shift
- A default observability baseline that instrumented too much (cost) or too little (visibility)
- A scaffolder that made it easy to create services, and so teams created too many — accidentally encouraging microservice sprawl
- A CODEOWNERS default that assigned reviews to a team that couldn't keep up

Describe the signal that told you it was wrong, what you changed, and — importantly — the trade-off you accepted in the replacement. Every fix to a platform default is itself a new opinion that will eventually age too.

### Self-check rubric

1–4 per prompt:

- **1** — Tool-centric, no user framing
- **2** — User framing but no change-management thinking
- **3** — User framing, migration plan, metrics, acknowledgment of political friction
- **4** — Above plus: a specific concession (what you explicitly don't try to do as well as the incumbent)

Target: 3+ on both.

---

## Self-assess (30 min)

### From the repo

```bash
prep quiz --topic platform-engineer
```

Alternatively, review `quiz_banks/platform-engineer.json` for questions tagged `catalog`, `scaffolder`, `backstage`, `self-service`, or `templates`.

Target: 80%+.

### Reflection (write your answers)

1. What's the current "service catalog" in your org? (Wiki, spreadsheet, tribal knowledge, actual tool?) What are the three things it's used for?
2. If you shipped a scaffolder for new services today, what would the *defaults* say about your org's engineering culture? What would the *escape hatches* reveal?
3. What piece of metadata in your org is most-stale-most-often? What would a catalog have to do to keep it current?

---

## Outcome checkpoint

Before Week 8:

- [ ] Designed a catalog schema with explicit cuts from Backstage's default entity set
- [ ] Drafted a population strategy that treats decay as a first-class problem
- [ ] Outlined three scaffolder templates with defaults, parameters, and non-goals
- [ ] Can articulate an opinionation principle without defaulting to "flexibility is good"
- [ ] Can answer Prompt A without leading with tool choice
- [ ] Can name a platform default that was wrong, with a specific signal
- [ ] Scored 80%+ on Week 7 quiz subset
- [ ] Wrote your three reflection answers

---

## Connections to later weeks

- Week 8 (Observability as a Platform Product) uses the catalog's ownership and relationship data to route telemetry correctly
- Week 9 (Multi-Tenancy) uses catalog entries as the authoritative source for tenant boundaries
- Week 11 (System Design Deep-Dive) often includes a catalog/scaffolder component in the IDP mock
- Week 12 (Behavioral) revisits Prompt B — the "default I got wrong" story is a strong STAR
