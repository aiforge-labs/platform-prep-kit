# 12-Week Plan: SRE → Platform Engineer

Scaffold only — content for each week will be filled in during milestones 1.2 and 1.3.

Time commitment: ~6–8 hours/week. Compress to 8 weeks by doubling up, or stretch to 16 by taking each week slower.

---

## Phase 1 — Mindset & Foundations (Weeks 1–3)

The point of Phase 1 is not to learn new tools. It's to rewire how you think about infrastructure work — from reactive reliability to proactive developer experience.

### Week 1: Platform as a Product

**Learning objectives**
- Articulate what "platform engineering" actually is and isn't
- Explain the product-thinking shift that distinguishes Platform Eng from DevOps/SRE
- Identify the internal customer (your platform's users = product engineers)

**Full week content:** [`weeks/week-01-platform-as-product.md`](weeks/week-01-platform-as-product.md)

### Week 2: Team Topologies

**Learning objectives**
- Understand Stream-aligned, Platform, Enabling, and Complicated-subsystem team types
- Diagnose interaction modes: X-as-a-service, Collaboration, Facilitating
- Map your org's current shape and identify friction points

**Full week content:** [`weeks/week-02-team-topologies.md`](weeks/week-02-team-topologies.md)

### Week 3: Developer Experience (DevEx)

**Learning objectives**
- Define DevEx and its measurable components (flow, friction, feedback)
- Identify common DevEx antipatterns in SRE-built tooling
- Propose DevEx improvements as a platform engineer would, not as an SRE would

**Full week content:** [`weeks/week-03-developer-experience.md`](weeks/week-03-developer-experience.md)

---

## Phase 2 — Technical Foundations (Weeks 4–6)

Phase 2 covers the building blocks most platform teams work with today. If you're already strong in any of these, use the week for depth rather than breadth.

### Week 4: Internal Developer Platforms (IDP)

**Learning objectives**
- Describe IDP components: service catalog, paved paths, abstractions, workflow automation
- Compare reference architectures (Backstage-centric, Humanitec-style, custom)
- Position a "minimum viable platform" vs a mature IDP

**Full week content:** [`weeks/week-04-internal-developer-platforms.md`](weeks/week-04-internal-developer-platforms.md)

### Week 5: GitOps at Scale

**Learning objectives**
- Explain GitOps beyond "kubectl apply from a repo" — pull-based reconciliation, drift detection, multi-cluster patterns
- Compare Flux and ArgoCD for platform-team use cases
- Understand infrastructure GitOps (Crossplane, cluster API) vs application GitOps

**Full week content:** [`weeks/week-05-gitops-at-scale.md`](weeks/week-05-gitops-at-scale.md)

### Week 6: Policy-as-Code and Guardrails

**Learning objectives**
- Distinguish guardrails (preventive, automated, opinionated) from gates (manual, slow, frustrating)
- Compare OPA/Rego, Kyverno, Conftest for different enforcement points (CI, admission, runtime)
- Design a policy set for a multi-team Kubernetes platform

**Full week content:** [`weeks/week-06-policy-as-code.md`](weeks/week-06-policy-as-code.md)

---

## Phase 3 — Platform-Specific Design & Ops (Weeks 7–9)

Phase 3 is where the work stops looking like "infra engineering" and starts looking like "product engineering for infrastructure."

### Week 7: Service Catalogs, Self-Service, Templates

**Learning objectives**
- Design a service catalog that developers actually use
- Build a golden-path template (scaffolder) that handles 80% of cases without configuration
- Decide where to be opinionated vs flexible

**Full week content:** [`weeks/week-07-service-catalogs.md`](weeks/week-07-service-catalogs.md)

### Week 8: Observability as a Platform Product

**Learning objectives**
- Distinguish "infrastructure observability" (ops view) from "platform observability" (consumed by product teams)
- Design an observability offering: what teams get by default, what they opt in to
- Understand telemetry cost allocation and tenant fairness

**Full week content:** [`weeks/week-08-observability-as-platform-product.md`](weeks/week-08-observability-as-platform-product.md)

### Week 9: Multi-Tenancy, Isolation, Cost Allocation

**Learning objectives**
- Compare multi-tenancy models (namespace-per-team, cluster-per-team, cluster-per-environment)
- Design tenant isolation (network, compute, data) at a platform level
- Build cost attribution that product teams can act on

**Full week content:** [`weeks/week-09-multi-tenancy.md`](weeks/week-09-multi-tenancy.md)

---

## Phase 4 — Leadership, Interviews, Closing (Weeks 10–12)

Phase 4 is about shipping the transition — turning everything learned into interview performance.

### Week 10: Platform Reliability (not App Reliability)

**Learning objectives**
- Define SLOs for a platform (not for a specific app): availability of deploy pipeline, accuracy of cost reporting, latency of template provisioning
- Design error-budget policies for platform teams
- Handle platform incidents that affect many downstream teams

**Full week content:** [`weeks/week-10-platform-reliability.md`](weeks/week-10-platform-reliability.md)

### Week 11: System Design Interview Deep-Dive

**Focus**
- Mock 1: design an IDP from zero for a 200-engineer org — [`mock/mock-1-idp-design.md`](mock/mock-1-idp-design.md)
- Mock 2: IaC review and redesign — [`mock/mock-2-iac-review.md`](mock/mock-2-iac-review.md)
- Mock 3: Platform incident response — [`mock/mock-3-platform-incident.md`](mock/mock-3-platform-incident.md)

Rubrics in [`rubrics/`](rubrics/).

**Full week content:** [`weeks/week-11-system-design.md`](weeks/week-11-system-design.md)

### Week 12: Behavioral + Closing

**Focus**
- Walk through your 20 STAR stories (see [`stories/`](stories/)) and pick your strongest 8
- Practice: "tell me about a time you built something and nobody used it" (a platform-specific favorite)
- Draft answers to: "why platform engineering?", "why now?", "what would you change about your current role?"
- Rest, taper, don't over-prep the day before

**Full week content:** [`weeks/week-12-behavioral.md`](weeks/week-12-behavioral.md)

---

## Progress tracking

Simple checklist — tick as you complete each week's Read / Apply / Articulate / Self-assess.

- [ ] Week 1: Platform as a Product
- [ ] Week 2: Team Topologies
- [ ] Week 3: Developer Experience
- [ ] Week 4: Internal Developer Platforms
- [ ] Week 5: GitOps at Scale
- [ ] Week 6: Policy-as-Code and Guardrails
- [ ] Week 7: Service Catalogs, Self-Service, Templates
- [ ] Week 8: Observability as a Platform Product
- [ ] Week 9: Multi-Tenancy, Isolation, Cost Allocation
- [ ] Week 10: Platform Reliability
- [ ] Week 11: System Design Deep-Dive
- [ ] Week 12: Behavioral + Closing

---

## Cut-lines (if you have less than 12 weeks)

If you only have 8 weeks, cut: Week 8 (Observability), Week 9 (Multi-tenancy), Week 10 (Platform Reliability) to lighter reading, and focus Week 11–12 on mocks.

If you only have 6 weeks, do: Week 1, Week 2, Week 4, Week 5, Week 11, Week 12. Skip Phase 3 entirely.

If you only have 4 weeks, this pack is not the right tool. Use it as a reference and focus on 5 strong STAR stories + 1 mock system design.
