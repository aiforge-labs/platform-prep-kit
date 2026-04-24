# Week 8: Observability as a Platform Product

**Phase 3 — Platform-Specific Design & Ops**

> **Terms used in this week**
> - **SRE** — Site Reliability Engineer
> - **Platform Engineer** — the role you're transitioning to
> - **Observability** — the practice of understanding a system's internal state from its external outputs (logs, metrics, traces, profiles, events)
> - **OpenTelemetry** / **OTel** — CNCF graduated project providing vendor-neutral APIs, SDKs, and tools for telemetry collection; Apache 2.0
> - **Prometheus** — CNCF graduated project; pull-based metrics system, Apache 2.0
> - **Grafana OSS** — open-source visualization and dashboarding tool, AGPLv3 upstream / "Grafana OSS"-licensed in recent versions (confirm license terms for your use)
> - **Loki** — Grafana Labs' log aggregation system (AGPL)
> - **Tempo** — Grafana Labs' distributed tracing backend (AGPL)
> - **Jaeger** — CNCF graduated distributed tracing project, Apache 2.0
> - **SLI** — Service Level Indicator (measurement)
> - **SLO** — Service Level Objective (target for an SLI)
> - **MTTR** — Mean Time to Restore (or Resolve)
> - **Cardinality** — the count of unique label combinations on a metric; a key cost driver
> - **Telemetry budget** — the planned cost/volume envelope for a tenant's telemetry
> - **DevEx** — Developer Experience
> - **IDP** — Internal Developer Platform
>
> Full definitions and equivalent titles in the [pack README](../README.md#what-we-mean-by-sre).

"Observability" is the single most-claimed-least-delivered capability in platform engineering. Every platform says it "provides observability." Most provide a Grafana URL and a shared Prometheus that teams either don't use or use badly. Week 8 is about re-framing observability as a *product offering* — with a customer, defaults, tiers, costs, and a clear relationship between what teams get for free and what they opt into.

If you were an SRE, observability was an operational concern: *can I debug this system*. As a Platform Engineer it becomes a product concern: *can 30 product teams each debug their systems, without stepping on each other, without unbounded cost, and without needing me to help*.

---

## Time commitment

~6–8 hours:

- Read: 2 hours
- Apply: 3 hours
- Articulate: 1 hour
- Self-assess: 30 minutes

## Learning objectives

By end of week you should be able to:

1. Distinguish *infrastructure observability* (what ops teams need about the platform) from *platform observability* (what product teams need about their services, provided by the platform)
2. Design an observability offering with a baseline every team gets by default and clearly-scoped opt-ins
3. Reason about cardinality and telemetry cost at the *platform* level — tenant fairness, budget allocation, runaway-metric detection
4. Articulate the OpenTelemetry design principle (signals through a standard API and protocol) and what it unlocks at a platform level
5. Connect observability to the service catalog (Week 7) — ownership routing, on-call surfacing, dashboard auto-provisioning
6. Identify three observability antipatterns: *the "just use Grafana" platform*, *the unbounded metric cardinality incident*, *observability as a tax rather than a service*

---

## Read (2 hours)

### Required

**1. OpenTelemetry — concepts and specification intro**
- [OpenTelemetry documentation — concepts](https://opentelemetry.io/docs/concepts/) — Apache 2.0, free.
- 30 minutes.
- Focus on: the three primary signals (metrics, logs, traces), the split between API, SDK, and Collector, and the vendor-neutrality principle. Skim the spec; don't try to memorize OTLP protobuf.

**2. Prometheus — concepts and operational considerations**
- [Prometheus documentation — concepts](https://prometheus.io/docs/concepts/data_model/) and [best practices](https://prometheus.io/docs/practices/naming/) — Apache 2.0, free.
- 30 minutes.
- Focus on: the data model (metric name + labels = series), the cardinality trap, and the pull model's implications for multi-tenant platforms.

**3. Google SRE Book — Service Level Objectives chapter (free online)**
- [Google SRE Book — Service Level Objectives](https://sre.google/sre-book/service-level-objectives/) — CC-BY-NC-ND, free online.
- 30 minutes. You may have read this already as an SRE; re-read it with platform glasses on.
- Focus on: SLOs as a *contract with users*, not an ops KPI. Every word of this applies to platform SLOs too — just swap "users" for "tenant teams."

**4. Grafana Labs observability blog posts — dashboards as code**
- Search [Grafana Labs blog](https://grafana.com/blog/) for "dashboards as code" or "observability at scale" posts. Pick one.
- 20 minutes.
- Focus on: the *maintenance* story for dashboards — who owns them, how they're versioned, how they stay relevant.

**5. In-repo reference — `knowledge_packs/sre-fundamentals.md`**
- Sections on SLIs, SLOs, and observability basics.
- 15 minutes.

### Recommended (pick one)

**6a. A cost/cardinality case study**
- Search YouTube/blogs for "Prometheus cardinality" post-mortems or "observability cost" talks from KubeCon, PromCon, or PlatformCon. Pick one 30–45 minute talk.
- 30 minutes.
- Focus on: the organizational dynamics of cost growth — who noticed, who paid, how the platform team detected vs enforced.

**6b. OpenTelemetry Collector deep-dive**
- [OpenTelemetry Collector documentation](https://opentelemetry.io/docs/collector/) — Apache 2.0, free.
- 30 minutes.
- Focus on: the Collector as the *platform's* extension point for policy (sampling rules, attribute scrubbing, routing), not just a passthrough.

### Why this source order

OpenTelemetry first because it is the vendor-neutral foundation every serious platform observability strategy now uses. "We're OTel-first" is the platform answer to "what about vendor lock-in."

Prometheus remains the most widely deployed metrics system in the Kubernetes ecosystem and the default backend for many OTel metric pipelines. Understanding its data model is non-negotiable.

The SRE Book SLO chapter is essential because it's the bridge from the SRE frame (reliability metrics) to the platform frame (offering SLOs as a *product capability* teams consume). The content is the same; the framing is different.

---

## Apply (3 hours)

### Exercise: Design Observability as a Platform Product Offering

You are designing the observability offering for a Platform Engineering team serving 40 product teams. Today teams each do their own thing — some have Grafana, some have vendor APM, some have nothing. Leadership wants a consolidated offering.

Produce a 2-page design doc.

#### Part A — The baseline (45 min)

Define the observability baseline every team gets *by default* when they create a service through the scaffolder.

For each of the three signals (metrics, logs, traces), specify:

1. What's captured automatically (zero-config) — e.g., HTTP request rate/duration/error for every endpoint, stdout logs shipped to the platform store, basic trace propagation
2. What's *not* captured at baseline, by design — e.g., business metrics (teams define their own), high-cardinality custom labels, full-payload logging
3. The retention policy — e.g., metrics at 1-minute resolution for 15 days, logs for 7 days, traces sampled at 1%
4. The storage backend (OSS: Prometheus, Loki, Tempo or Jaeger) and any cross-tenant shared infrastructure
5. What teams see by default — a generated dashboard per service, a generated alert-rule set based on SLO templates

#### Part B — Tiers and opt-ins (30 min)

Design 2–3 tiers above the baseline. Examples:

- **Standard** (baseline, free to the team)
- **Enhanced** — longer retention, higher sampling rate, custom dashboards at scale — opt-in, with a budget
- **Premium** — full-fidelity traces, high-cardinality custom metrics, dedicated Grafana folder with elevated quotas

For each tier:
- What's included
- What it costs the team (in dollars, or in an internal-credit currency, or in a budget allocation)
- How they opt in (catalog metadata? Pull request? Platform UI?)

Tiers exist mainly to force the conversation about cost and priority. Defaults must be free; anything premium must be explicit.

#### Part C — Cost and cardinality (30 min)

Write down your approach to:

1. **Cardinality budget per team.** Every team gets an allocation of active metric series (e.g., 10k series per service baseline, plus opt-in increases). When they exceed, what happens?
2. **Runaway-metric detection.** How do you detect — within an hour — that one team's service has blown up to 500k series? What's the automated response?
3. **Log volume budget.** Similar — per-tenant volume limit, with a process for over-budget.
4. **Trace sampling.** Default head-sampling at some low rate, with selective always-on for error traces. Who configures this, you or the tenant?
5. **Visibility.** Teams see their own cost. Leadership sees aggregate cost per team. Platform team sees everything.

The "visibility" part is political, not just technical. Naming the cost is half the control mechanism.

#### Part D — Integration with the catalog (30 min)

Refer back to Week 7's catalog. Specify:

1. When a new service is registered, what observability artifacts are auto-provisioned? (Dashboard, alerts, tracing config, log routing.)
2. When a service's ownership changes, what observability config follows? (Alert routing, dashboard folder, on-call destination.)
3. When a service is deprecated, what observability gets cleaned up automatically?
4. What metadata fields in the catalog drive observability behavior? (Owner team, lifecycle stage, criticality tier, SLO targets.)

The catalog-to-observability wiring is where Week 7 and Week 8 meet. Without it, teams duplicate configuration everywhere.

#### Part E — Antipatterns and honesty (30 min)

Write half a page naming the two observability antipatterns you are most likely to slip into, and what your design does to prevent them. Examples:

- **"Just use Grafana" platform** — you provide infrastructure but not the product layer (dashboards, alerts, SLOs). Teams are on their own.
- **Observability as a tax** — teams resent the instrumentation burden; they view it as overhead rather than a capability that helps them. Prevention: make the baseline genuinely useful with zero work (generated dashboards, pre-configured alerts).
- **Cardinality explosion without detection** — one team's runaway label crashes the platform for everyone. Prevention: per-tenant quotas and fast detection.
- **Dashboard rot** — dashboards exist but nobody trusts them. Prevention: dashboards-as-code versioned with the service, linked to the catalog, and retired when the service is.

### What good looks like

- Baseline is specific and zero-config
- Tiers exist and have explicit costs
- Cardinality budgets with detection and response
- Catalog integration is named, not hand-waved
- Antipatterns are acknowledged with specific countermeasures

### What weak looks like

- "We'll deploy Grafana and Prometheus and teams can use them"
- No per-tenant isolation or budget
- Baseline is so minimal teams won't use it, or so maximal it's expensive at scale
- No acknowledgment of dashboard / alert rot
- Vendor-lock-in debate ignored

---

## Articulate (1 hour)

### Prompt A

> *"Design the observability offering for a new platform team serving 20 product teams. What do teams get by default, and what do they opt in to?"*

This prompt tests whether you treat observability as a product, not an infrastructure concern.

**SRE trap:**
Diving into tool choice (Prometheus vs vendor X) without first asking what the product teams need. Or conflating "we have Grafana deployed" with "teams have observability."

**Platform framing:**
Start with the user. What does a product team want from observability? Usually: *when my service breaks, I can find out fast and diagnose without a platform engineer*. Design for that. Then:

1. Name the baseline (what's free, zero-config). Make it genuinely useful.
2. Name the tiers (what's paid/opted-in, with an explicit cost signal).
3. Name what you *don't* provide — e.g., "we don't ship a universal 'observability platform,' we ship the capabilities that plug into OpenTelemetry, and you can wire them to whatever visualization you want. We have an opinion on the default, not a mandate."
4. Name the cost and cardinality mechanisms — because the first thing that goes wrong at scale is cost.

### Prompt B

> *"A product team's metric cardinality blows up and causes a platform-wide Prometheus incident. Walk me through response, comms, and the longer-term fix."*

This is a mini on-call scenario disguised as an observability question.

**SRE trap:**
Go straight to the technical mitigation ("I'd restart the ingesters, drop the offending metric, scale up storage") without the product-team framing.

**Platform framing:**
Three threads in parallel:

1. **Mitigation** — immediately limit the blast radius. Options: drop the offending metric at the Collector, apply a per-tenant rate limit, or roll back the team's recent change if you can trace it.
2. **Comms** — tell all 40 tenants what's happening *before* they notice. Separate message for the team that triggered it (private, factual, not blaming).
3. **Longer-term** — this was a platform-level systemic failure, not just a team error. Per-tenant cardinality isolation should have prevented a one-team incident from hurting everyone. The blameless post-mortem focuses on the platform's missing control, not the team's mistake.

A strong answer distinguishes between *the team that caused it* (a symptom) and *the platform that allowed it* (the root cause), and assigns most of the corrective-action weight to the platform.

### Self-check rubric

1–4 per prompt:

- **1** — Tool- or infrastructure-centric
- **2** — User-framing but no cost / cardinality thinking
- **3** — Baseline + tiers + cost + tenant-isolation + clear product framing
- **4** — Above plus: explicit non-goals, antipattern awareness, and a lived-experience detail

Target: 3+ on both.

---

## Self-assess (30 min)

### From the repo

```bash
prep quiz --topic platform-engineer --tag observability
```

Alternatively, review `quiz_banks/platform-engineer.json` and `quiz_banks/sre-fundamentals.json` for questions tagged `observability`, `slo`, `cardinality`, `opentelemetry`, or `grafana`.

Target: 80%+.

### Reflection (write your answers)

1. In your current org, who owns "observability"? Is it the SRE team, the platform team, every product team individually, or an ambiguous mix? What changes if it moves to a clear owner?
2. What's one metric series in your current environment that you *know* is high-cardinality and probably not worth the cost? Why has it not been fixed?
3. If you redesigned your org's observability from zero, what would you *not* carry over?

---

## Outcome checkpoint

Before Week 9:

- [ ] Designed a baseline observability offering with zero-config defaults
- [ ] Designed 2–3 tiers with explicit cost signals
- [ ] Specified per-tenant cardinality budget and runaway detection
- [ ] Wired the observability offering to the service catalog (ownership, lifecycle)
- [ ] Named two observability antipatterns and countermeasures
- [ ] Can answer Prompt A with baseline-and-tiers framing, not tool-choice framing
- [ ] Can answer Prompt B with platform-level root cause, not team-level blame
- [ ] Scored 80%+ on Week 8 quiz subset
- [ ] Wrote your three reflection answers

---

## Connections to later weeks

- Week 9 (Multi-Tenancy) is where the per-tenant cardinality budget becomes a first-class tenant-isolation concern
- Week 10 (Platform Reliability) treats observability platform uptime / ingestion lag as a platform SLI
- Week 11 (System Design) often includes an observability component in the IDP mock
- Week 12 (Behavioral) — Prompt B is close to a canonical "tell me about an incident" STAR
