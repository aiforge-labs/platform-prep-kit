# Week 10: Platform Reliability (not App Reliability)

**Phase 4 — Leadership, Interviews, Closing**

> **Terms used in this week**
> - **SRE** — Site Reliability Engineer
> - **Platform Engineer** — the role you're transitioning to
> - **SLI** — Service Level Indicator (a measured thing)
> - **SLO** — Service Level Objective (a target for the SLI)
> - **SLA** — Service Level Agreement (contractual, usually external)
> - **Error budget** — the permissible un-reliability in a given window (e.g., 0.1% in a quarter)
> - **Error-budget policy** — the agreed response when the budget is burned (pause feature work, revert, etc.)
> - **Platform SLI** — an SLI that measures the *platform's* service to its tenants, distinct from app-level SLIs
> - **Tenant** — a team, app, or environment consuming the platform
> - **Blast radius** — the set of tenants affected by a single platform failure
> - **Postmortem** / **Post-incident review (PIR)** — written analysis after an incident
> - **Toil** — manual, repetitive, automatable ops work; a first-class SRE concept that carries into platform work
> - **IDP** — Internal Developer Platform
> - **RTO / RPO** — Recovery Time Objective / Recovery Point Objective (disaster-recovery terms)
>
> Full definitions and equivalent titles in the [pack README](../README.md#what-we-mean-by-sre).

Week 10 is the most deceptively familiar week of the pack. You already know SRE. The shift is that you are now running reliability for a product whose customers are 40 internal engineering teams, and whose failure modes are fundamentally different from any single app's. A platform that is "up" by app-SLI measures can still be badly failing its tenants.

This week is about porting your SRE skills to the platform frame without losing what made them strong.

---

## Time commitment

~6–8 hours:

- Read: 1.5 hours (lighter — you already know much of this)
- Apply: 3 hours
- Articulate: 1.5 hours (more, because this is the most interview-dense week)
- Self-assess: 30 minutes

## Learning objectives

By end of week you should be able to:

1. Define SLIs for a *platform* — not an app — that reflect the experience of tenant teams (deploy-pipeline availability, template-provisioning latency, catalog freshness, observability ingestion lag, cost-report accuracy)
2. Write an error-budget policy appropriate for a platform team serving many tenants
3. Handle a platform incident that affects many downstream teams — mitigation, comms, blast-radius containment, and multi-tenant postmortem
4. Distinguish *platform toil* from *tenant toil* and allocate engineering time between them
5. Design disaster-recovery thinking appropriate for a platform — the platform is infrastructure; if it goes down, every tenant's workflow stops
6. Articulate the platform-reliability version of the reliability-vs-velocity trade-off, where the platform team has *two* velocities to manage — their own and their tenants'

---

## Read (1.5 hours)

Less reading this week; more exercise and articulation.

### Required

**1. Google SRE Book — selected chapters, re-read with platform lens**
- [Google SRE Book online](https://sre.google/sre-book/) — CC-BY-NC-ND, free.
- Re-read: Service Level Objectives (chapter 4), Eliminating Toil (chapter 5), Handling Overload (chapter 21, skim).
- 45 minutes. If these chapters are already familiar, move fast and focus only on the parts that require translation to platform terms.

**2. Google SRE Workbook — postmortem chapter**
- [Google SRE Workbook — Postmortem Culture](https://sre.google/workbook/postmortem-culture/) — CC-BY-NC-ND, free.
- 20 minutes.
- Focus on: blameless postmortems and the structural-improvement focus, which is especially important when the blame could fall on one tenant who triggered a platform-level failure.

**3. CNCF Post-Incident Review (PIR) examples**
- Search for public post-mortems from cloud providers, CNCF projects, or large platform teams (Cloudflare, Heroku historical, Datadog, others publish detailed public ones).
- 30 minutes.
- Focus on: the style of the writeup — what's included, what's deliberately not included (no naming-and-blaming of individuals), and how corrective actions are scoped at the *system* level.

**4. In-repo reference — `knowledge_packs/sre-fundamentals.md`**
- 15 minutes. Use the repo reference as the consolidated summary.

### Recommended

Skim one recent public postmortem from a major platform failure — an outage you remember, ideally. Pay attention to the *platform-level* corrective actions vs the *app-level* ones.

### Why this source order

Most of the reading this week is re-reading. The point is not to learn new SRE material — it's to translate existing SRE knowledge into platform-engineering framing. You should be doing a running mental find-and-replace: "app" → "platform," "user" → "tenant," "incident" → "platform incident affecting N tenants."

---

## Apply (3 hours)

### Exercise: Design Platform Reliability for Your IDP

You are the senior Platform Engineer for the IDP you designed in Week 4 (or pick your own realistic platform). Design the reliability program.

#### Part A — Platform SLIs (45 min)

List 6–8 *platform* SLIs. These are not app SLIs. Examples to start you thinking:

- **Deploy pipeline availability** — % of deploy attempts that succeed within the expected time window (not just: deploy CI uptime)
- **Scaffolder / new-service-creation latency** — p95 time from "start template" to "service registered and ready to accept first commit"
- **Catalog freshness** — % of services whose owner metadata is less than 90 days old (decay-aware)
- **Observability ingestion lag** — p95 time from event generation to visibility in Grafana/Prometheus
- **Policy evaluation latency** — p95 admission-controller decision time (slow admission = slow deploys)
- **Tenant onboarding time** — hours from "team requested" to "team can ship first service"
- **Cost-report accuracy** — attributed cost / total cloud spend (90%+ expected)
- **Break-glass event rate** — manual overrides per month (a reliability metric of the *process*, not the system)

For each SLI you choose:

1. Name the measurement
2. Specify the target SLO (e.g., 99.5% monthly, p95 < 30s)
3. Specify the error-budget window (monthly, quarterly)
4. Name the tenant experience it protects (the *user-facing* outcome)

#### Part B — Error-budget policy (30 min)

Write your platform's error-budget policy. For each SLI above, specify:

1. What happens when 25% of the budget is consumed (early warning)
2. What happens when 50% is consumed (formal stop on non-critical feature work in the related area)
3. What happens when 100% is consumed (freeze; focus on recovery)

Specific to platform teams: the freeze affects *your* team's roadmap. Your tenants' roadmaps are not frozen by your error budget — but they may be effectively paused if the platform is degraded. Acknowledge this dependency explicitly.

#### Part C — A platform-wide incident (60 min)

Walk through the following scenario in writing. Write as if you were the on-call engineer.

> **Scenario:** Your GitOps controller has been silently failing to reconcile for 90 minutes. Teams have been merging to main assuming deploys are happening. They are not. The controller's own metrics look fine (it's making API calls, it's running), but the actual apply step is failing for a subset of manifests because of a recent admission-controller policy update.
>
> Across the 40 tenants: 12 have merged changes in the last 90 minutes, 3 of those are in prod paths, 1 is a release-day deploy. Your paging system didn't fire because the controller's self-metrics look healthy.

Answer:

1. **First 10 minutes.** What do you do? (Priorities: detect scope, notify tenants, prevent more damage.)
2. **Mitigation.** You can either (a) roll back the admission-controller policy or (b) bypass the controller for the failing tenants. Which, and why?
3. **Comms.** Draft the tenant-facing comms (2–3 short paragraphs). Include what's happening, the scope, the expected recovery, and what tenants should/shouldn't do right now.
4. **Postmortem framing.** What's the root cause — policy update, observability gap, controller design? In a multi-tenant platform, "one team's policy broke the controller" is almost always the *symptom*. What's the systemic cause, and what's the platform-level corrective action?
5. **Contrast with single-app outage.** Name two things about this scenario that are specifically about *platform* reliability, not app reliability.

#### Part D — Toil and disaster recovery (30 min)

Briefly answer:

1. **Toil audit.** Name three kinds of toil your platform team likely does: (1) tenant-facing (onboarding, quota changes, break-glass), (2) infra-facing (cluster upgrades, cert rotations), (3) data-facing (catalog cleanup, cost-attribution fixes). For each, what's the right next step — automate, self-serve, or accept?
2. **Disaster recovery.** If your entire GitOps controller + catalog + observability backend went offline, and you had to rebuild from backups, what's your RTO (recovery time objective)? What's your RPO (how much data loss is acceptable)? What's in your runbook?

#### Part E — The tenant-velocity trade-off (15 min)

Write half a page: platform teams balance *their* velocity (shipping platform features) with *their tenants'* velocity (tenants shipping their products). What's the meta-trade-off, and how does it show up differently from classic SRE-vs-developer velocity tension? Be specific.

### What good looks like

- SLIs are tenant-experience-oriented, not infrastructure-uptime-oriented
- Error-budget policy has a real effect on *your* roadmap
- The incident scenario is handled with comms-first thinking and systemic root-cause analysis
- Toil is categorized with a clear next-step for each
- The tenant-velocity trade-off is named, not glossed over

### What weak looks like

- Platform SLIs that are infrastructure-uptime re-wrapped
- Error-budget policy that's toothless ("we'll prioritize fixes")
- Incident response centered on blame for the team that triggered it
- No disaster-recovery thinking
- Missing the insight that the platform's velocity affects tenants' velocity

---

## Articulate (1.5 hours)

### Prompt A

> *"What SLIs do you set for a platform, and how are they different from SLIs for an application?"*

This is a definitional prompt that separates candidates who have thought about platform reliability from those who haven't.

**SRE trap:**
List the standard four (availability, latency, throughput, error rate) for the platform control plane. Technically correct, conceptually thin — it misses the tenant-experience framing.

**Platform framing:**
Platform SLIs measure the tenant experience of consuming the platform, not the uptime of the platform's components. Examples:

1. *Deploy pipeline success rate* — not "CI uptime" but "% of developer-initiated deploys that completed within expected time"
2. *Catalog freshness* — decay-aware, because a "working" catalog full of stale data is a failed platform
3. *Tenant onboarding time* — an operational SLO that reveals platform-as-product health
4. *Break-glass rate* — measuring how often the platform falls short of its self-service promise

Close with the difference: app SLIs protect end users; platform SLIs protect internal engineering teams. Both matter; both require different instincts.

### Prompt B

> *"Your platform caused a production incident for three tenants. Walk me through the postmortem — who is responsible, what goes in the report, and what changes."*

A test of honesty, systems-thinking, and multi-tenant awareness.

**SRE trap:**
"We identified the root cause in our change and rolled back." Fine for a single-app incident, thin for a platform one.

**Platform framing:**
Three expansions over the SRE instinct:

1. **Responsibility is shared structurally.** The platform team is responsible for the platform's behavior. Individual tenants may have triggered the failure, but the platform allowed it. The corrective action weight is on the platform.
2. **Blast radius matters.** Three tenants is three different sets of consequences. The postmortem quantifies the impact (# of tenants, # of end-users downstream, business impact). Without this, platform incidents get under-prioritized relative to single-app ones because the platform team sees them and the affected tenants don't always see each other.
3. **Corrective actions are platform-level.** Not "we'll be more careful"; specific system changes — better canary for platform changes, better per-tenant isolation so one team's misuse can't blast radius to others, better observability of the platform's own reconciliation behavior.

### Prompt C

> *"Tell me about a time your platform's roadmap was slowed because you had to freeze for reliability work. How did you communicate that to stakeholders?"*

This is both a STAR story and a leadership test.

**SRE trap:**
Hide the freeze as an internal matter ("we just spent some time on reliability work"). Misses the opportunity to talk about how you *used* the error budget.

**Platform framing:**
Describe the freeze as a *decision*, not a passive event. The error budget triggered; you (or your team) made a call; you told stakeholders; you did the work; you came out with a platform that was stronger.

Include:

- The specific SLI that was burning
- The specific non-critical work you paused
- The specific communication (who, when, what)
- The cost (what tenants didn't get) and benefit (what they got later)
- What you learned about the error-budget policy itself

Strong closings acknowledge the error-budget policy *as a product* — does it need adjusting, is it too strict or too loose, does it need a different cadence?

### Self-check rubric

1–4 per prompt:

- **1** — Infrastructure-uptime framing; no tenant experience
- **2** — Some platform framing but no concrete SLIs / consequences
- **3** — Tenant-experience SLIs, error-budget teeth, multi-tenant blast radius awareness
- **4** — Above plus: a specific number, a specific trade-off accepted, or a policy adjustment as an outcome

Target: 3+ on all three.

---

## Self-assess (30 min)

### From the repo

```bash
prep quiz --topic sre-fundamentals
```

Alternatively, review `quiz_banks/sre-fundamentals.json` for questions tagged `slo`, `error-budget`, `platform-reliability`, or `postmortem`.

Target: 80%+.

### Reflection (write your answers)

1. Of the SLIs you currently measure as an SRE, which three translate cleanly to platform SLIs, and which three do not? Why?
2. The last time your platform (or any platform you've used) had an incident that affected multiple teams, what was the comms like? What would you have done differently?
3. If you had to freeze your platform roadmap for one reliability issue, what would it be in your current org?

---

## Outcome checkpoint

Before Week 11:

- [ ] Defined 6–8 platform SLIs with tenant-experience framing
- [ ] Wrote an error-budget policy with real consequences for the platform team's roadmap
- [ ] Walked through a multi-tenant platform incident (mitigation, comms, postmortem framing)
- [ ] Categorized platform toil and named the next step for each
- [ ] Specified RTO/RPO for platform-core components
- [ ] Can answer Prompt A with tenant-experience framing
- [ ] Can answer Prompt B with platform-level corrective actions (not tenant blame)
- [ ] Can tell Prompt C as a decision story, not a passive event
- [ ] Scored 80%+ on Week 10 quiz subset
- [ ] Wrote your three reflection answers

---

## Connections to later weeks

- Week 11 (System Design) — platform reliability components appear in every mock
- Week 12 (Behavioral) — Prompt C is a STAR story in the "influence without authority" category
- The reliability story connects every prior week: Week 4 (what's being kept reliable), Week 5 (GitOps as reconciliation), Week 6 (policies as platform-reliability primitives), Week 7 (catalog as reliability-visible), Week 8 (observability as reliability's instrument), Week 9 (tenancy as blast-radius control)
