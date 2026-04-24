# Week 9: Multi-Tenancy, Isolation, Cost Allocation

**Phase 3 — Platform-Specific Design & Ops**

> **Terms used in this week**
> - **SRE** — Site Reliability Engineer
> - **Platform Engineer** — the role you're transitioning to
> - **Tenant** — a logical unit the platform serves (most often a team, sometimes an app or environment)
> - **Multi-tenancy** — multiple tenants sharing platform capacity with controlled isolation
> - **Noisy neighbor** — when one tenant's resource use degrades another tenant's experience
> - **RBAC** — Role-Based Access Control
> - **NetworkPolicy** — Kubernetes-native network-level access control between pods and namespaces
> - **ResourceQuota / LimitRange** — Kubernetes namespace-level resource controls
> - **vCluster** — Loft Labs' Kubernetes-in-Kubernetes virtual cluster project (Apache 2.0 for core)
> - **Capsule** — CNCF sandbox multi-tenancy project (Apache 2.0)
> - **Kyverno** — CNCF incubating policy engine (Apache 2.0); covered in Week 6
> - **FinOps** — the discipline of financial accountability for cloud spend; see finops.org
> - **Showback / Chargeback** — showback makes cost visible to a team; chargeback actually bills them
> - **Blast radius** — the set of tenants affected by a single failure
> - **IDP** — Internal Developer Platform
>
> Full definitions and equivalent titles in the [pack README](../README.md#what-we-mean-by-sre).

Multi-tenancy is the dimension of platform work that most separates "we run a cluster" from "we run a platform." A single-tenant platform is just infrastructure you own. Multi-tenancy introduces the hard questions: who can see whose data, who pays for what, whose bug slows down whose customer, and who is responsible when those answers get blurry.

Week 9 covers the three tenancy axes that every platform has to answer for: *who has access* (isolation), *what they can use* (quota/fairness), and *what they are paying for* (cost allocation). These three together are the definitional questions of a platform at scale.

---

## Time commitment

~6–8 hours:

- Read: 2 hours
- Apply: 3 hours
- Articulate: 1 hour
- Self-assess: 30 minutes

## Learning objectives

By end of week you should be able to:

1. Compare four multi-tenancy models — namespace-per-team, cluster-per-team, cluster-per-environment, vCluster / logical cluster — on isolation, cost, and operational load
2. Design the three isolation layers (identity/RBAC, network, compute/memory) and reason about their interaction
3. Specify a tenant lifecycle — onboarding, capacity changes, offboarding — that the platform can support without manual toil
4. Distinguish showback from chargeback and articulate which your platform should implement and when
5. Recognize and design against three multi-tenancy antipatterns: *the soft-multi-tenancy fiction*, *the cost showback with no teeth*, *the security model that requires trust*
6. Connect tenancy decisions to Week 7 (catalog as tenant boundary) and Week 8 (per-tenant observability budgets)

---

## Read (2 hours)

### Required

**1. Kubernetes Multi-Tenancy documentation**
- [Kubernetes Multi-Tenancy docs](https://kubernetes.io/docs/concepts/security/multi-tenancy/) — Apache 2.0, free.
- 30 minutes.
- Focus on: the spectrum from soft (namespaces + policies) to hard (clusters per tenant), and the "third option" logical clusters. Don't memorize tools; internalize the trade-offs.

**2. Kubernetes RBAC and NetworkPolicy**
- [Kubernetes RBAC documentation](https://kubernetes.io/docs/reference/access-authn-authz/rbac/) — 20 minutes.
- [Kubernetes NetworkPolicy documentation](https://kubernetes.io/docs/concepts/services-networking/network-policies/) — 15 minutes.
- Focus on: how fine-grained these primitives let you go, and how quickly they become a maintenance burden at scale. Platform teams typically layer a higher-level abstraction on top (tenant CRD, policy-as-code generating RBAC + NetworkPolicy from tenant metadata).

**3. Resource controls — ResourceQuota, LimitRange, Priority Classes**
- [Kubernetes ResourceQuotas](https://kubernetes.io/docs/concepts/policy/resource-quotas/) and [LimitRanges](https://kubernetes.io/docs/concepts/policy/limit-range/) — Apache 2.0, free.
- 20 minutes.
- Focus on: the difference between cluster-level fairness (Priority Classes) and namespace-level bounds (Quota/LimitRange), and the failure mode when teams hit their quota mid-deploy.

**4. FinOps Foundation — Cloud FinOps framework**
- [FinOps Foundation — What is FinOps](https://www.finops.org/framework/) — CC-BY-NC-ND, free reading.
- 30 minutes.
- Focus on: the three phases (Inform, Optimize, Operate) and the principle that cost is a team sport across engineering, finance, and product. Platform observability is how engineering participates.

**5. In-repo reference — `knowledge_packs/platform-engineering.md` and `knowledge_packs/sre-fundamentals.md`**
- Sections on tenant isolation, quota design, and cost visibility.
- 15 minutes.

### Recommended (pick one)

**6a. vCluster / logical-cluster deep-dive**
- [vCluster documentation](https://www.vcluster.com/docs/) or search for vCluster talks from KubeCon.
- 30 minutes.
- Focus on: the trade-off — stronger isolation than namespaces, cheaper than full clusters, but new operational surface area (the virtual cluster itself needs to stay healthy).

**6b. A public multi-tenancy case study**
- Search for talks or blog posts on "multi-tenancy at [company]" from KubeCon, PlatformCon, or SREcon.
- 30 minutes.
- Focus on: the model they landed on, what they tried first, and what the *operational cost* of their model turned out to be.

### Why this source order

Kubernetes docs first because the vocabulary — soft vs hard tenancy, namespace-level vs cluster-level isolation — is the lingua franca of platform-engineering multi-tenancy conversations. Interviewers use these terms assuming you know them.

RBAC + NetworkPolicy + ResourceQuota are the three primitives every platform team composes or abstracts over. You have to understand them raw before you can design the abstraction.

FinOps is included because cost accountability is increasingly part of the platform engineer's job. "Who pays for what" is a tenancy question with organizational teeth. Candidates who have *never* heard the term "FinOps" will read as having narrow exposure to production platforms.

---

## Apply (3 hours)

### Exercise: Design Multi-Tenancy for a Real Org

You are the Platform Engineer for a 50-team org running on Kubernetes. Today, everything is in one giant cluster with one big namespace per environment (dev/staging/prod). Teams step on each other; cost attribution is "the sum is huge, but we can't tell you why."

Design the tenancy model. Produce a 2-page design doc.

#### Part A — Choose the tenancy model (45 min)

Compare four options for *this* 50-team org:

| Model | Isolation | Cost | Ops load | Fit |
|---|---|---|---|---|
| Namespace-per-team (single cluster) | Soft — reliant on RBAC, NetworkPolicy, Quota | Lowest | Low infra, high policy |  |
| Cluster-per-team | Hard — separate control planes | Highest | High — 50 clusters to operate |  |
| Cluster-per-environment (shared dev, shared staging, shared prod) | Medium — env-level hard boundary, soft within | Medium | Medium |  |
| vCluster / logical-cluster per team | Strong — full API isolation, shared node pool | Medium | Medium — virtual-cluster management is new operational surface |  |

Fill in the "fit" column with your reasoning for each. Then pick the model and write half a page justifying your choice.

Common-sense grounding: namespace-per-team is the default for most orgs at this scale. If you deviate, have a reason (regulatory requirements, extreme noisy-neighbor history, per-team compliance boundaries).

#### Part B — Design the three isolation layers (45 min)

Regardless of the model you picked, specify each layer.

1. **Identity / RBAC**
   - Who authenticates (humans, services, CI systems)
   - How tenants map to groups (team-name in catalog → RBAC Group)
   - What they can do in their tenant / not in others
   - How cross-tenant access is granted (the exception flow; Week 6 policy rigor applies)

2. **Network**
   - Default: deny-all between tenants, allow within tenant
   - Shared infrastructure access (platform services, DNS, egress)
   - Internal API egress rules
   - Specific callouts for inter-service communication patterns your org has today

3. **Compute / memory**
   - Per-tenant ResourceQuota (with starting allocations)
   - LimitRange defaults (so pods without explicit limits don't consume the whole quota)
   - Priority Classes (which tenants, if any, get higher priority and why)
   - Runaway-tenant detection (Week 8 applies; this is cardinality's cousin)

#### Part C — Tenant lifecycle (30 min)

Walk through:

1. **Onboarding a new tenant.** What catalog metadata is required? What gets provisioned automatically (namespace(s), RBAC, default Quota, NetworkPolicy, baseline observability, default alerts)? What's the end-to-end time from "team requests" to "team ships their first service" — target under 1 day.

2. **Capacity changes.** A team needs more CPU. What's the process? Self-serve within a cap? Platform-approval above it?

3. **Offboarding.** A team is deprecated. What gets cleaned up, on what timeline, and with what safeguards (no surprise deletes of production data)?

#### Part D — Cost allocation (45 min)

Specify:

1. **Attribution.** How does every dollar of cloud spend get tagged to a tenant? Options: Kubernetes labels → cost-allocation report, per-tenant Kubecost or OSS equivalent, cluster-level tagging plus internal allocation. Pick one and say why.

2. **Showback vs chargeback.**
   - **Showback** — every tenant sees their cost; finance sees aggregate per-tenant
   - **Chargeback** — tenants are actually billed, internal cost center transfer
   - Which does your org start with? Most start with showback; chargeback requires organizational readiness.

3. **Visibility.** Team view (their own cost, trending), platform team view (everyone, with outlier detection), leadership view (aggregate and benchmarks).

4. **Cost-anomaly detection.** Tenant's cost doubled week-over-week. What happens automatically? What requires human follow-up?

#### Part E — Antipatterns (15 min)

Write down the two antipatterns you are most likely to slip into, and what your design does to prevent them. Examples:

- **Soft-multi-tenancy fiction** — claiming "tenant isolation" on a setup where a team with cluster-admin-adjacent permissions can read every other team's secrets
- **Cost showback with no teeth** — cost is visible, but teams have no incentive to act. Prevention: pair showback with leadership-level reviews and team-level goals.
- **The permanent RBAC exception** — a tenant got elevated access in an emergency and never got it revoked
- **Tenant onboarding that takes two weeks** — too slow; teams route around the platform (often into a different cloud account, which makes cost and compliance worse)

### What good looks like

- A tenancy model picked with explicit trade-offs, not the default namespace-per-team with no discussion
- Three isolation layers specified with concrete primitives
- Tenant lifecycle with a target onboarding time
- Cost allocation that distinguishes showback from chargeback, with a reason for the choice
- Antipatterns named, with specific countermeasures

### What weak looks like

- Namespace-per-team with no reasoning
- NetworkPolicy unmentioned or hand-waved
- Onboarding described as "they open a ticket"
- Cost allocation as "we'll build a dashboard someday"
- No acknowledgment that soft-multi-tenancy is *soft* — security claims that aren't actually enforced

---

## Articulate (1 hour)

### Prompt A

> *"A team wants a cluster to themselves because they don't trust the shared cluster. How do you handle the conversation?"*

This is a product-engineering question disguised as a technical one. The team's request is almost never really about the cluster.

**SRE trap:**
Argue on technical merits — "we have strong isolation with namespaces and NetworkPolicy, it's fine." The team will nod and keep wanting a cluster. You've won the argument and lost the relationship.

**Platform framing:**
Ask why. "Don't trust" is a concrete claim — *what specifically happened, or what are you afraid will happen?* Common roots: a noisy-neighbor incident, a security boundary (PCI, HIPAA), an autonomy preference ("we want to upgrade on our own schedule"), or a previous bad experience at another company that the team is pattern-matching.

Each of those has a different right answer:

- Noisy-neighbor concern → *our per-tenant quota and priority class should cover it; let me walk you through what happens if a neighbor spikes.*
- Regulatory → *you may actually be right; we should discuss a regulated-workload cluster, which is a platform feature, not an exception.*
- Autonomy → *what autonomy do you actually need? If it's the upgrade cadence, we can offer a per-tenant upgrade window.*
- Past-experience pattern-match → *let me show you what's different here.*

The meta-point: treat the team as a customer whose request reveals something about your platform's product story, not as a problem to push back on.

### Prompt B

> *"Your org is considering chargeback — teams get actually billed for their cloud usage. What's your platform team's position?"*

This is a values-and-systems question that reveals your platform-vs-business thinking.

**SRE trap:**
"Chargeback is good, it creates accountability." True and unhelpful — fails to address the real questions about implementation readiness and adverse incentives.

**Platform framing:**
Chargeback requires organizational readiness:

1. **Data accuracy.** Can you attribute cost to a tenant with enough precision that a team won't contest the bill every month? If not, chargeback creates friction, not accountability.
2. **Team control.** A team can't be charged for things they can't control. If the platform team's decisions (node type, retention policy) dominate the bill, the team has no way to respond.
3. **Budget visibility and cadence.** Teams need to see cost *before* they spend it, not at end-of-month surprise.
4. **Adverse incentives.** Watch for: teams refusing to adopt platform features that cost them (observability, security scanning), teams hiding workloads in cheaper-but-worse environments, teams under-provisioning to save money and paging the platform team at 3am.

A strong answer says: "start with showback, measure the signal, move to chargeback only when (a) attribution is >95% accurate, (b) teams can act on the data, and (c) leadership is ready to treat cost as a first-class team metric."

### Self-check rubric

1–4 per prompt:

- **1** — Technical arguments, no user / tenant framing
- **2** — Some user framing, but no concrete process
- **3** — Clear diagnosis, options, readiness checks
- **4** — Above plus: acknowledges adverse incentives or organizational prerequisites

Target: 3+ on both.

---

## Self-assess (30 min)

### From the repo

```bash
prep quiz --bank platform-engineer --topic multi-tenancy
```

Alternatively, review `quiz_banks/platform-engineer.json` for questions tagged `multi-tenancy`, `rbac`, `quota`, `cost-allocation`, or `finops`.

Target: 80%+.

### Reflection (write your answers)

1. In your current org, what level of multi-tenancy exists today — soft, hard, or not-at-all? Where does it break down?
2. What's one cost that *nobody* is currently paying for attention to — a runaway metric, an unrotated test environment, an over-provisioned CI fleet? What would it take to make it visible?
3. If your org moved to chargeback tomorrow, which team would feel the most adverse effect, and what would they probably do that's bad for the platform overall?

---

## Outcome checkpoint

Before Week 10:

- [ ] Compared four multi-tenancy models with explicit trade-offs; picked one for a realistic org
- [ ] Specified the three isolation layers (identity, network, compute)
- [ ] Defined a tenant lifecycle with a target onboarding time
- [ ] Chose showback vs chargeback with a readiness rationale
- [ ] Named two tenancy antipatterns and their countermeasures
- [ ] Can answer Prompt A without winning-the-argument framing
- [ ] Can answer Prompt B with readiness checks, not ideology
- [ ] Scored 80%+ on Week 9 quiz subset
- [ ] Wrote your three reflection answers

---

## Phase 3 wrap-up

Weeks 7–9 are the "platform as product" weeks. If they went well:

- You no longer design platform features as standalone systems — you design them as offerings with defaults, tiers, costs, and owners
- You treat tenants as *customers* and their requests as *product signal*
- You can connect catalog, observability, and tenancy as a coherent platform story, not three separate systems

Phase 4 (Weeks 10–12) is about platform reliability (how your *platform* stays up, not just its tenants' apps) and about interview execution. It's the shortest of the four phases but the most interview-focused.

## Connections to later weeks

- Week 10 (Platform Reliability) treats tenant-lifecycle SLIs (onboarding time, quota-change latency) as first-class platform reliability metrics
- Week 11 (System Design) — multi-tenancy is a common second-half interview prompt ("now scale this to 10 teams, 100 teams, 1000")
- Week 12 (Behavioral) — Prompt A maps to a common "tell me about a difficult stakeholder" STAR
