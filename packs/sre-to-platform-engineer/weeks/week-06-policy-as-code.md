# Week 6: Policy-as-Code and Guardrails

**Phase 2 — Technical Foundations**

> **Terms used in this week**
> - **SRE** — Site Reliability Engineer
> - **Platform Engineer** — the role you're transitioning to
> - **Policy-as-code** — defining organizational or security rules in a machine-readable language so they can be versioned, tested, and enforced programmatically
> - **Guardrails** — automated, preventive, opinionated constraints that protect by default (ideally invisible until violated)
> - **Gates** — manual, slow, frustrating checkpoints that require human approval before proceeding
> - **OPA** — Open Policy Agent; CNCF graduated project, Apache 2.0
> - **Rego** — the declarative policy language used by OPA
> - **Kyverno** — CNCF incubating project; Kubernetes-native policy engine that uses YAML instead of a separate DSL, Apache 2.0
> - **Conftest** — a CLI tool built on OPA/Rego for testing configuration files (e.g., Terraform plans, Kubernetes manifests) in CI, Apache 2.0
> - **Admission controller** — Kubernetes API server extension point that validates or mutates resources before they are persisted
> - **ValidatingWebhook / MutatingWebhook** — the Kubernetes admission webhook types
> - **CEL** — Common Expression Language; Kubernetes-native language for validating admission policies (ValidatingAdmissionPolicy, introduced as GA in 1.30)
> - **CI / CD** — Continuous Integration / Continuous Delivery
> - **DSL** — Domain-Specific Language
> - **CIS Benchmarks** — Center for Internet Security's published security baselines (e.g., CIS Kubernetes Benchmark)
> - **Shift-left** — moving checks earlier in the pipeline, before they become expensive to fix
> - **PR** — Pull Request
>
> Full definitions and equivalent titles in the [pack README](../README.md#what-we-mean-by-sre).

Policy-as-code is the cleanest example of platform engineering's core thesis: *encode good judgment into tools, so every team benefits without needing to remember the rules.* Done well, it's invisible. Done badly, it's the single biggest reason developers hate their internal platform.

Week 6 is where you learn the tools (OPA/Rego, Kyverno, Conftest, CEL), the enforcement points (CI, admission, runtime), and — most importantly — the politics. The hard part of policy-as-code is not writing policies. It's deciding *which* policies, *where* to enforce them, and *how* to handle the case where a team legitimately needs an exception.

---

## Time commitment

~6–8 hours:

- Read: 2 hours
- Apply: 3–4 hours (hands-on — write and deploy real policies)
- Articulate: 1 hour
- Self-assess: 30 minutes

## Learning objectives

By end of week you should be able to:

1. Articulate the *guardrails vs gates* distinction and why guardrails are a product-thinking choice
2. Name the four common enforcement points (pre-commit, CI, admission, runtime) and what each is good at and bad at
3. Write a simple Rego policy and a simple Kyverno policy for the same rule, and explain when each tool is a better fit
4. Distinguish OPA/Rego, Kyverno, CEL-based ValidatingAdmissionPolicy, and Conftest — and articulate the current state of the Kubernetes-native admission story
5. Design a policy exception process that doesn't undermine the policy
6. Identify the two most common policy-as-code antipatterns: *the permanent exception* and *the untested policy*

---

## Read (2 hours)

### Required

**1. OPA documentation — Introduction and Rego basics**
- [Open Policy Agent — Introduction](https://www.openpolicyagent.org/docs/latest/) and [Policy Language](https://www.openpolicyagent.org/docs/latest/policy-language/) — Apache 2.0, free.
- 45 minutes.
- Focus on: OPA as a *general-purpose* policy engine (not Kubernetes-specific), the Rego evaluation model (rules, queries, default values), and the decoupling of policy decisions from enforcement.

**2. Kyverno documentation — Introduction and writing policies**
- [Kyverno Introduction](https://kyverno.io/docs/introduction/) and [Writing Policies](https://kyverno.io/docs/writing-policies/) — Apache 2.0, free.
- 30 minutes.
- Focus on: why Kyverno chose YAML over a DSL, the policy types (validate, mutate, generate, cleanup), and the `audit` vs `enforce` modes.

**3. Kubernetes ValidatingAdmissionPolicy and CEL**
- [Kubernetes ValidatingAdmissionPolicy documentation](https://kubernetes.io/docs/reference/access-authn-authz/validating-admission-policy/) — Apache 2.0, free.
- 20 minutes.
- Focus on: this is a built-in alternative to webhook-based admission control, GA in 1.30. For simple validations, it avoids a webhook round-trip. Understand where it fits alongside OPA and Kyverno — not instead of them, but *in addition* for specific cases.

**4. Conftest documentation**
- [Conftest](https://www.conftest.dev/) — Apache 2.0, free.
- 15 minutes.
- Focus on: Conftest as the "test your config files in CI" answer to policy. It uses Rego underneath, but the ergonomics are CI-friendly.

**5. In-repo reference — `knowledge_packs/policy-as-code.md`**
- 15 minutes. Cross-check vocabulary before the Apply exercise.

### Recommended (pick one)

**6a. CIS Kubernetes Benchmark**
- [Center for Internet Security's Kubernetes Benchmark](https://www.cisecurity.org/benchmark/kubernetes) — requires free registration to download the PDF.
- 30 minutes. Skim; don't memorize.
- Focus on: the *kind* of rules a hardened Kubernetes platform enforces. Not every rule is a policy-as-code candidate — some are configuration, some are runtime, some are procedural. Distinguishing them is part of the skill.

**6b. A public platform-team writeup on policy rollout**
- Search for public blog posts: "OPA at scale," "Kyverno rollout," or "policy-as-code at [company]" from engineering blogs.
- 30 minutes.
- Focus on: the *sequencing* — how policies were introduced gradually (audit mode → enforce mode → exceptions → review cadence), and the organizational process around exceptions.

### Why this source order

OPA first because it's the foundation — even if you end up choosing Kyverno, the Rego model is the intellectual reference point for all Kubernetes policy tools.

Kyverno next because it is the most common *pragmatic* choice for Kubernetes-only orgs. Understanding why Kyverno exists (Rego is hard; YAML is familiar) teaches you something about how platform tools succeed.

Kubernetes-native CEL/ValidatingAdmissionPolicy is the "what's new" material most candidates don't know. Demonstrating awareness that the Kubernetes project shipped its own built-in admission mechanism in 1.30 signals you track the ecosystem.

Conftest is short but important — it's the cleanest answer to "shift policy left to CI" and is the right answer for Terraform, Helm charts, and any YAML configuration.

---

## Apply (3–4 hours)

Two exercises: one hands-on (write policies), one design (policy set for a platform).

### Exercise 1: Write the same policy in two tools (90 min)

The policy: **"Every Deployment in production namespaces must have resource requests and limits set on every container."**

Simple. Specific. Enforceable. A real-world baseline.

#### Part A — Write it in Rego (for OPA/Conftest)

Write a Rego policy that, given a Kubernetes Deployment manifest, returns a violation if any container is missing either `resources.requests` or `resources.limits` for CPU or memory.

Test it against three manifests:

1. A compliant Deployment (all resources set)
2. A non-compliant Deployment (missing limits)
3. A partially-compliant Deployment (one container has requests but another doesn't)

Use `conftest test` to run the policy against the manifests as a CI-style check.

Observe: how is the violation reported? How clear is the error message to a developer? What would they need to do to fix it?

#### Part B — Write the same policy in Kyverno

Install Kyverno in your kind cluster from Week 5 (or create a new one). Write a ClusterPolicy that enforces the same rule: production-namespace Deployments must have resource requests and limits.

Deploy in `audit` mode first. Create a compliant Deployment and a non-compliant one. Observe the PolicyReport resources that Kyverno generates.

Switch the policy to `enforce` mode. Try to create the non-compliant Deployment. Observe the rejection message.

#### Part C — Compare

In writing (half a page):

1. Which tool had better developer ergonomics for *writing* the policy?
2. Which tool had better developer ergonomics for *receiving* the violation message?
3. For this specific policy, which is the right tool and why?
4. Would the answer change if the policy was more complex (say, "production Deployments must use an image from an approved registry AND have resource limits AND have a specific label")?

### Exercise 2: Design a policy set for a new platform (90 min)

You are the Platform Engineer for a 100-engineer, regulated-industry org (fintech, healthcare — your choice of fictional vertical; the point is that policy matters). The platform is Kubernetes-based. You need to propose the *initial* policy set and the *rollout plan*.

Produce a 1–2 page design doc covering:

1. **The initial policy set** — 8–12 policies. For each, specify:
   - The rule
   - The risk it mitigates (security, reliability, cost, compliance)
   - The enforcement point (pre-commit, CI, admission, runtime)
   - The tool (Conftest in CI, Kyverno at admission, ValidatingAdmissionPolicy, OPA as sidecar for non-K8s, etc.)
   - `audit` vs `enforce` mode at launch

2. **The exception process.** Every policy will eventually need an exception. How do you:
   - Receive exception requests
   - Time-bound them (exceptions should expire; permanent exceptions are technical debt)
   - Track them as a metric you review

3. **The rollout plan.**
   - Week 1–2: what ships in audit mode, visible to whom
   - Week 3–4: what promotes from audit to enforce, on what criteria
   - Week 5+: steady-state — review cadence, policy ownership, the team of humans who care when a policy starts to generate a lot of violations

4. **Two policies you explicitly chose not to write** and why. (Reasons: too specific to one team; covered better by a non-policy mechanism; not worth the maintenance burden.)

5. **Failure modes.** What would cause this policy set to become a platform liability rather than a platform asset?

#### What good looks like

- Each policy has a *reason* — not just a rule, but a risk
- Enforcement points are matched to the *cost* of the violation (high-blast-radius = earlier enforcement; low-severity = later enforcement, maybe just audit)
- The exception process has a *time-bound* and a *metric*
- The rollout plan starts in audit mode, never in enforce
- Non-policies exist — you didn't try to encode everything

#### What weak looks like

- A list of 20 policies with no reasoning
- All enforcement at admission, none at CI (or vice versa)
- Exception process is "email the platform team"
- Rollout plan is "deploy them all on day one"
- No acknowledgment that policies themselves are code that rots and needs ownership

---

## Articulate (1 hour)

### Prompt A

> *"A senior engineer is pushing back on a policy you've introduced — they say it's blocking a legitimate use case and your response of 'file an exception' isn't fast enough. How do you handle it?"*

This is a values-and-systems test. The interviewer wants to see whether you treat policy as a product with users, or as a rule to enforce.

**SRE trap:**
"The policy is there for a reason. They need to follow the process." A technically-correct answer that communicates nothing about product thinking. Usually combined with an unstated assumption that *the policy-setter is always right*, which is exactly the attitude that makes policy-as-code programs fail.

**Platform framing:**
Validate the complaint first. If the process is slow, that's a real problem and the policy is a liability. Three things to think about out loud:

1. *Is the policy still right?* Policies age. Maybe this one is now encoding out-of-date thinking. A legitimate blocker is a useful signal.
2. *Is the exception process the bottleneck, or the policy itself?* A policy with a 48-hour exception path is different from a policy with a 2-week exception path. The second one will drive workarounds.
3. *What's the short-term unblock and the long-term fix?* Short: grant a time-bound exception. Long: decide whether to modify the policy, add a parameterized allowance, or accept that this workflow has moved outside the policy's original scope.

Example shape:
> "The first question I'd ask is whether the policy is still right. If a smart senior engineer is blocked by it and has a legitimate case, that's a signal — either the policy is stale, or the exception process is too slow to be usable. In the short term I'd unblock them: grant a time-bound exception, say two weeks. In the medium term I'd figure out whether their case is genuinely an edge case or whether it's about to become a common pattern. If common, I'd revise the policy. If edge, I'd make the exception process *itself* faster — because if one senior engineer has hit it, others will. The thing I would not do is repeat that the policy is there for a reason without being able to re-state the reason *to them*. A policy you can't explain live is a policy you've outgrown."

### Prompt B

> *"What's a policy you've seen or shipped that turned out to be a bad idea? What was the signal that told you, and what would you do differently?"*

Candidates who can't answer this have rarely owned policy programs end-to-end.

**SRE trap:**
"We had a few bad ones, but they got fixed." No specifics.

**Platform framing:**
Pick one specific policy. Describe the rule, the reasoning at the time, and the signal that it was wrong (rising exception count, rising workaround count, dropping platform adoption, a specific team blocked for a specific reason). Name the fix, and — more importantly — name the *systemic change* you'd make to notice the same kind of signal earlier next time.

Strong versions include an honest admission that the policy was right in intent but wrong in scope, or that it enforced the wrong *where* (CI instead of admission, or admission instead of runtime), or that it encoded a snapshot of a moment rather than a durable principle.

### Self-check rubric

1–4 per prompt:

- **1** — Mandate framing; treats policy as a rule, not a product
- **2** — Acknowledges trade-offs but no concrete process
- **3** — Has a specific process, time-bound exceptions, a review cadence
- **4** — Above plus: treats exception-count as a leading indicator, names the failure mode where a policy program becomes a liability

Target: 3+ on both. This topic is where "platform engineer" and "security engineer" vocabulary diverge; nailing the product framing here distinguishes candidates.

---

## Self-assess (30 min)

### From the repo

```bash
prep quiz --topic iac-gitops
```

Alternatively, review `quiz_banks/iac-gitops.json` for questions tagged `opa`, `rego`, `kyverno`, `policy-as-code`, `admission-control`, or `guardrails`.

Target: 80%+.

### Reflection (write your answers)

1. In your current org, which rules are currently enforced by convention, wiki page, or tribal knowledge — that should be enforced by code? Pick one and sketch the policy.
2. Name a rule you've seen enforced as a policy-as-code check that was the *wrong* check — either too strict, too early in the pipeline, or not encoding the actual intent. What was it?
3. If you had to pick one tool — OPA, Kyverno, or built-in CEL admission policies — to start a new platform's policy program tomorrow, which would you pick and why? Include one reason your choice could be wrong in two years.

---

## Outcome checkpoint

Before Week 7:

- [ ] Wrote and tested the same policy in Rego (Conftest) and in Kyverno
- [ ] Observed a Kyverno policy running in both audit and enforce modes in a real cluster
- [ ] Designed a starter policy set with 8–12 policies, enforcement points, and a rollout plan
- [ ] Can articulate the guardrails-vs-gates distinction without hand-waving
- [ ] Can answer Prompt A without falling into mandate framing
- [ ] Can name at least two policy-as-code antipatterns and the signals that reveal them
- [ ] Scored 80%+ on Week 6 quiz subset
- [ ] Wrote your three reflection answers

---

## Phase 2 wrap-up

Weeks 4–6 are the technical backbone. If they went well, you should notice:

- You can describe an IDP without reaching for tool names first
- You can reason about GitOps at the *topology* level, not just the `kubectl apply` level
- You can design a policy program that treats exceptions as signal rather than failure

Phase 3 (Weeks 7–9) shifts focus again — from *building platforms* to *designing platform products*. Service catalogs, observability offerings, and multi-tenancy are where platform engineering starts to look less like infra engineering and more like product engineering for internal customers.

Before starting Week 7, spend 30 minutes reviewing the design docs from the Apply exercises in Weeks 4, 5, and 6. They're the raw material for your STAR stories later, and the through-line across all three is the same: *what did you choose not to build, and why?*

## Connections to later weeks

- Week 7 (Service Catalogs, Self-Service) covers how platform capabilities — including policy enforcement — get surfaced to developers
- Week 9 (Multi-Tenancy) revisits Kyverno in the context of namespace isolation and tenant boundaries
- Week 10 (Platform Reliability) treats "mean exception-resolution time" as a platform-program health metric
- Week 11 (System Design Deep-Dive) often includes a policy/guardrails component in the IDP mock
