# Week 5: GitOps at Scale

**Phase 2 — Technical Foundations**

> **Terms used in this week**
> - **SRE** — Site Reliability Engineer
> - **Platform Engineer** — the role you're transitioning to
> - **GitOps** — an operating model where Git is the source of truth for desired system state, and a controller continuously reconciles actual state toward it
> - **IaC** — Infrastructure-as-Code
> - **Reconciliation** — the controller loop that compares actual state to desired state and converges them
> - **Drift** — the divergence between actual cluster state and the Git-declared desired state
> - **Pull-based** / **Push-based** — whether the in-cluster agent pulls from Git (pull) or an external CI pipeline pushes to the cluster (push). GitOps is pull-based by definition.
> - **ArgoCD** — CNCF graduated GitOps controller, CNCF project, Apache 2.0
> - **Flux** — CNCF graduated GitOps toolkit, Apache 2.0
> - **Crossplane** — CNCF incubating project for managing external resources (cloud infra) from Kubernetes using CRDs, Apache 2.0
> - **CRD** — Custom Resource Definition
> - **App-of-apps** — an ArgoCD pattern where one Application object declares a Git path that itself contains other Application manifests
> - **ApplicationSet** — ArgoCD's templating engine for generating many Applications from a single definition
> - **Multi-tenancy** — multiple teams / apps / environments sharing one platform; covered in depth in Week 9
> - **RBAC** — Role-Based Access Control
> - **PR** — Pull Request
> - **OpenGitOps** — the CNCF working group and spec that defines GitOps principles (opengitops.dev)
>
> Full definitions and equivalent titles in the [pack README](../README.md#what-we-mean-by-sre).

GitOps is often the first technical skill listed on Platform Engineer job descriptions, and often the most shallowly understood. "We use ArgoCD" is not a GitOps strategy. This week is about moving from *operating* a GitOps tool to *designing* GitOps for an organization — drift, multi-cluster, multi-tenant, disaster recovery, and the political question of who owns what file in which repo.

You already know `kubectl apply`. This week is about the systems around it.

---

## Time commitment

~6–8 hours:

- Read: 2 hours
- Apply: 3–4 hours (hands-on — spin up a local cluster, run a real GitOps tool)
- Articulate: 1 hour
- Self-assess: 30 minutes

## Learning objectives

By end of week you should be able to:

1. Recite the four OpenGitOps principles (declarative, versioned & immutable, pulled automatically, continuously reconciled) and explain what each *excludes*
2. Compare ArgoCD and Flux on structure, extension points, UI, and operational model — and state when each is a better fit
3. Describe three multi-cluster patterns (hub-and-spoke, cluster-per-team, cluster-per-environment) and their trade-offs
4. Explain the repo-topology question: one monorepo vs repo-per-team vs repo-per-env, and when each breaks down
5. Identify three GitOps antipatterns: *push-based pipeline calling itself GitOps*, *ClickOps for the "emergencies"*, *manifests generated at apply-time*
6. Distinguish *application GitOps* (Kubernetes workloads) from *infrastructure GitOps* (cloud resources via Crossplane or controllers)

---

## Read (2 hours)

### Required

**1. OpenGitOps principles (CNCF) — the canonical short definition**
- [opengitops.dev](https://opengitops.dev/) — the four principles, one paragraph each. Also read the GitOps Principles v1.0.0 document linked from the site.
- 15 minutes. Memorize the four principles — you will be asked to recite them.

**2. ArgoCD documentation — Core Concepts and Architecture**
- [ArgoCD Core Concepts](https://argo-cd.readthedocs.io/en/stable/core_concepts/) and [Architecture](https://argo-cd.readthedocs.io/en/stable/operator-manual/architecture/) — Apache 2.0, free.
- 30 minutes.
- Focus on: Application and AppProject, the sync waves / hooks model, the controller-manager / repo-server / application-controller split.

**3. Flux documentation — GitOps Toolkit Components**
- [Flux architecture](https://fluxcd.io/flux/components/) and [concepts](https://fluxcd.io/flux/concepts/) — Apache 2.0, free.
- 30 minutes.
- Focus on: the toolkit model (source-controller, kustomize-controller, helm-controller, notification-controller, image-automation-controller) and *why* Flux is split this way. Contrast with ArgoCD's more monolithic model.

**4. A scale case study — pick one public conference talk**
- Search YouTube for "ArgoCD at scale" or "Flux at scale" talks from KubeCon, GitOpsCon, or PlatformCon. Pick one 25–45 minute talk from the last two years.
- Some specific talk topics worth looking for: Intuit's ArgoCD architecture, Weaveworks/Flux multi-cluster patterns, D2iQ/Mirantis multi-tenant GitOps, or any "lessons learned" retrospective from a platform team.
- 30–40 minutes.
- Focus on: the organizational topology they adopted (repo structure, team boundaries), not the YAML.

**5. In-repo reference — `knowledge_packs/iac-gitops.md`**
- 15 minutes. Use this as a cross-check for vocabulary and as your consolidated reference during the Apply exercise.

### Recommended (pick one)

**6a. Crossplane documentation — overview + composition concepts**
- [Crossplane concepts](https://docs.crossplane.io/latest/concepts/) — Apache 2.0, free.
- 30 minutes.
- Focus on: Compositions and XRDs (Composite Resource Definitions). This is the clearest current example of *infrastructure GitOps* — managing AWS/GCP/Azure resources through the same GitOps tool you use for workloads.

**6b. Terraform + GitOps patterns (public blog posts from platform teams)**
- Search for public blog posts on "Terraform in a GitOps workflow," "Atlantis," or "Terraform Cloud with Git" from platform engineering blogs.
- 30 minutes.
- Focus on: the honest trade-offs — Terraform's pre-apply plan is hard to reconcile with GitOps's "controller applies continuously" model. This is a live architectural debate.

### Why this source order

OpenGitOps first because it's the definitional filter. When someone claims they're doing "GitOps," you should reflexively check against the four principles.

ArgoCD and Flux are the two CNCF graduated projects in this space, and every serious platform interview will assume you know both. Reading one is not enough — the contrast between the two teaches you more than depth in either.

The case study is where most of the *design* judgment lives. Official docs describe the mechanics; case studies describe the organizational trade-offs that dominate real decisions.

Crossplane vs Terraform-with-GitOps is the most interesting current debate in the field. Being able to articulate the trade-off — controller-driven vs plan-and-apply — signals that you have thought about GitOps beyond Kubernetes workloads.

---

## Apply (3–4 hours)

This week has two Apply exercises: one hands-on, one design. Do both. The hands-on one keeps your skills sharp; the design one trains your interview reflex.

### Exercise 1: Run GitOps locally (90 min)

Pick **one** of ArgoCD or Flux. Both are fine choices — picking either is better than trying both and getting surface-level exposure to each.

#### Setup

- Install [kind](https://kind.sigs.k8s.io/) (Kubernetes in Docker), Apache 2.0, or use minikube if you already have it installed.
- Create a kind cluster: `kind create cluster --name gitops-lab`
- Install your chosen controller per its official docs. Both ArgoCD and Flux have 5-minute quick-starts.
- Create a public GitHub repo (or use a private one with a PAT) with a `manifests/` directory containing a simple Deployment + Service (nginx or any small image).

#### Tasks

1. Configure the controller to sync your repo's `manifests/` directory to a new namespace.
2. Observe the initial reconciliation. How does the controller tell you what it did?
3. **Introduce drift:** `kubectl edit` the live Deployment to change the replica count. Watch what happens in the UI / CLI. How long until reconciliation notices? How is the change reported?
4. **Delete a resource out-of-band:** `kubectl delete svc ...`. Does it get re-created? How fast?
5. **Make a change in Git and observe:** update the image tag in your manifest, commit, push. How is the sync triggered — polling, webhook, both?
6. **Break it on purpose:** push a manifest with a syntax error. What does the controller report? Where does it surface failures?
7. **Pause reconciliation for a specific app**, then unpause. When would you actually want to do this in production?

Take notes as you go — these observations are STAR material later.

### Exercise 2: Design a multi-cluster GitOps topology (90 min)

You are designing GitOps for an org with:

- 50 product teams
- 3 environments (dev, staging, prod)
- 15 Kubernetes clusters (some regional, some environment-scoped)
- Central platform team of 4 engineers
- Compliance requirement: prod changes must have an auditable Git history and two-person approval

Answer the following in a written design doc (aim for 1–2 pages):

1. **Repo topology.** One repo, repo-per-team, repo-per-cluster, or repo-per-env? Justify.
2. **Tool placement.** One ArgoCD/Flux install managing all clusters (hub-and-spoke)? Or one per cluster? Trade-off?
3. **Tenancy model.** How do teams interact with the platform — do they write raw manifests, or a higher-level abstraction (Helm chart, Kustomize overlay, custom CRD)? Where do they write them?
4. **Environment promotion.** How does a change move from dev to staging to prod? What's the trigger? Who approves?
5. **The two-person-approval requirement.** Implement as a branch-protection rule on the prod manifests repo? Or as an ArgoCD/Flux-level approval step? Both? Why?
6. **Secrets.** You will not solve secrets fully (Week 9 for that), but name the approach you'd use and why it's compatible with GitOps.
7. **The break-glass case.** What's the documented procedure for an emergency manual change to prod? How do you prevent that becoming the default?
8. **What would cause this design to break?** Name two failure modes and what you'd monitor to detect them early.

#### What good looks like

- Your repo topology has an explicit reasoning, not just a preference
- You name specific trade-offs for hub-and-spoke vs per-cluster tooling, and pick based on blast radius
- The break-glass procedure is *both* documented and *observable* — you can tell when it's used
- You acknowledge at least one thing your design deliberately does *not* solve well

#### What weak looks like

- Defaulting to "one repo, one ArgoCD install" without engaging with blast-radius or multi-cluster trade-offs
- Handling the two-person-approval as "Git branch protection" without thinking about the race between merge and sync
- No mention of drift, no mention of break-glass, no failure-mode analysis

---

## Articulate (1 hour)

### Prompt A

> *"We have a team that's skeptical of GitOps — they feel like it slows them down. How do you roll it out?"*

This prompt tests whether you view GitOps as a *mandate* or a *product*.

**SRE trap:**
"We'd enforce it. GitOps is the standard." That answer earns a polite nod and a weak hire signal.

**Platform framing:**
Start by validating the skepticism. Most GitOps pilots *do* feel slower initially — there's a compile step between "I want to change something" and "the thing is changed." Then describe adoption as onboarding: start with a low-risk workload, measure the trade-off honestly (loss: seconds of latency on change; gain: auditability, rollback, reviewability, on-call clarity), and let the team opt in to the next workload only when the first feels better than the alternative. Emphasize that GitOps gives the skeptical team *something they'll value* — usually faster and cleaner rollback, which every on-call engineer cares about.

Example shape:
> "Rolling out GitOps to a skeptical team is a DevEx problem more than a tooling one. The skepticism is almost always right about the immediate slowdown — a Git commit and a sync cycle really are slower than a manual kubectl apply for a one-off change. What sells GitOps is the second week, not the first day: auditable history, rollback in 30 seconds by reverting a commit, parity between what staging and prod run. I'd start by finding one workload where *rollback* is currently painful, migrate that one workload first, and let them feel the rollback story. The skeptical team is usually an early-adopter team in disguise if you let them see the value you actually have, not the value you've claimed."

### Prompt B

> *"Describe a GitOps antipattern you've seen, and what the organization should have done differently."*

This tests the depth of your GitOps understanding. Surface-level candidates repeat slogans; deep candidates identify the specific failure modes.

**SRE trap:**
Generic answers like "they didn't have good Git hygiene." Not specific enough to signal experience.

**Platform framing:**
Pick a specific concrete antipattern. Good candidates:

- *"Push-based `kubectl apply` from CI called GitOps."* The Git commit triggers a pipeline that runs `kubectl apply`. No in-cluster reconciliation, no drift detection, and when the cluster diverges, there's no way to catch it. The fix: run a real GitOps controller in-cluster; CI's job ends at "merge to main."
- *"ClickOps for emergencies."* The platform allows a break-glass manual change, and everyone starts using break-glass. Fix: make break-glass observable (every override fires an alert), track the number of overrides as a metric that leadership cares about, and run quarterly reviews on why they happened.
- *"Manifests generated at apply-time."* Someone uses a templating tool with random inputs, so the manifest in Git doesn't match what got applied. Fix: commit the rendered manifest, not the template.

Whichever you pick, the structure is: what the antipattern is, why it's seductive (there's always a reason someone did it), and the specific change that fixes it.

### Self-check rubric

1–4 per prompt:

- **1** — Quotes slogans; no specifics
- **2** — Specific but surface-level; describes what rather than why
- **3** — Specific, structural, names a trade-off
- **4** — Above plus: a lived-experience detail that would be hard to fake (a specific number, a specific tool, a specific second-order effect)

Target: 3+ on both.

---

## Self-assess (30 min)

### From the repo

```bash
prep quiz --bank iac-gitops --topic gitops
```

Alternatively, review `quiz_banks/iac-gitops.json` for questions tagged `gitops`, `argocd`, `flux`, `reconciliation`, or `multi-cluster`.

Target: 80%+.

### Reflection (write your answers)

1. In your current (or most recent) org, how close is your deployment pipeline to the four OpenGitOps principles? Where are the gaps?
2. If you had to pick between ArgoCD and Flux for a new 100-engineer org tomorrow, which would you pick and why? Include one reason you *could* be wrong.
3. What's one infrastructure resource (cloud resource, not Kubernetes workload) that you manage today that would be better as GitOps? What's blocking that?

---

## Outcome checkpoint

Before Week 6:

- [ ] Ran ArgoCD or Flux locally; observed drift, reconciliation, and failure handling first-hand
- [ ] Wrote a multi-cluster GitOps design doc with explicit repo topology, tenancy, and break-glass procedure
- [ ] Can recite the four OpenGitOps principles and explain each
- [ ] Can compare ArgoCD and Flux on structure and operational model without lookup
- [ ] Can name at least two concrete GitOps antipatterns and their fixes
- [ ] Can answer Prompt A without defaulting to mandate framing
- [ ] Scored 80%+ on Week 5 quiz subset
- [ ] Wrote your three reflection answers

---

## Connections to later weeks

- Week 6 (Policy-as-Code) often runs as a validation step in the GitOps pipeline (pre-merge Conftest, in-cluster Kyverno)
- Week 7 (Service Catalogs, Self-Service) builds on the scaffolder idea — scaffolding new services usually means generating the GitOps manifests
- Week 9 (Multi-Tenancy) deepens the tenancy model you sketched in Exercise 2
- Week 10 (Platform Reliability) treats "GitOps reconciliation latency" as a platform SLI
- Week 11 (System Design Deep-Dive) often includes a GitOps component in the deployment-pipeline mock
