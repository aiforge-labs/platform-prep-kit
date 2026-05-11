# Mock 2 — IaC Review and Redesign

**Scored mock exercise · 45 minutes · Week 11**

> **Terms used in this mock**
> - **IaC** — Infrastructure-as-Code
> - **SRE** — Site Reliability Engineer
> - **Platform Engineer** — the role you're transitioning to
> - **Terraform** — the most widely used IaC tool (MPL 2.0 historical; now BSL for newer versions — OpenTofu is the community FOSS fork)
> - **OpenTofu** — Linux Foundation fork of Terraform with MPL 2.0 licensing
> - **GitOps** — Week 5: Git as source of truth, pull-based reconciliation
> - **Admission controller** — Kubernetes API server extension point (Week 6)
> - **Blast radius** — the set of tenants / systems affected by a failure
> - **RACI** — Responsible / Accountable / Consulted / Informed (ownership model)
> - **Kyverno, OPA** — policy engines covered in Week 6
>
> Full definitions and equivalent titles in the [pack README](../README.md#what-we-mean-by-sre).

This mock simulates a design-review interview. You're given a platform codebase structure (not the code itself — the *shape*) and asked to critique. Common interview format at companies that want to see your ability to read an existing system critically.

Rubric: [`../rubrics/rubric-2-iac-review.md`](../rubrics/rubric-2-iac-review.md) — read **before** attempting.

---

## Setup

You're reviewing a 3-year-old platform infrastructure repository at a 120-engineer mid-stage company. You've been brought in as a senior platform engineer. The team lead has shared the repo layout and a few Slack notes and asked you to review and propose changes.

### The repository structure (given)

```
platform-infra/
├── terraform/
│   ├── modules/
│   │   ├── vpc/
│   │   ├── eks/
│   │   ├── rds/
│   │   └── everything-else/     # 42 resources in one module
│   ├── environments/
│   │   ├── dev/
│   │   │   ├── main.tf
│   │   │   └── backend.tf       # s3 state, no locking configured
│   │   ├── staging/
│   │   │   └── main.tf
│   │   └── prod/
│   │       └── main.tf          # last substantive change: 11 months ago
│   └── scripts/
│       └── apply-all.sh         # bash loop calling terraform apply
├── kubernetes/
│   ├── argocd/
│   │   └── applicationsets/     # 4 ApplicationSet manifests, one per env
│   ├── manifests/
│   │   ├── team-a/
│   │   ├── team-b/
│   │   └── ... (24 team directories, no CODEOWNERS)
│   └── policies/
│       └── deny-latest-tag.yaml # one Kyverno policy, in audit mode
├── ci/
│   └── deploy.yml               # GitHub Actions workflow; uses 4 secrets pulled from a single org secret
├── docs/
│   └── README.md                # last updated 14 months ago
└── .github/
    └── pull_request_template.md # 7 checkboxes, one about security
```

### Slack notes from the team lead (given)

> "We've been meaning to clean this up. Team A's Terraform apply broke last month because the state file lock timed out — ended up manually unlocking. Prod hasn't been touched much because nobody wants to risk it. Argo's been drifting for some services but we haven't figured out why. Policy rollout stalled — the deny-latest-tag rule is still in audit 18 months in."

### Interviewer prompt

> *"Walk me through your review. What's wrong, what's outdated-but-tolerable, and what's a reasonable trade-off? Prioritize your changes."*

You have 45 minutes.

---

## How to run this mock

### Solo variant

1. Set a timer for 45 minutes.
2. Read the setup once; re-read the Slack notes.
3. Speak or write your review, working through a structure.
4. Stop at 45 minutes.
5. Score using the rubric.

### With a practice partner

- Share the setup (copy the repo tree and Slack notes above).
- Have them play the role of the team lead and push back on your suggestions with realistic objections.
- Score each other using the rubric.

---

## Suggested structure (for the candidate)

### 0–5 min: Orient and ask

Before critiquing, ask:

- What's the platform team's size and charter?
- What's the current on-call burden — are these things actually causing outages?
- What's the business context — growth trajectory, upcoming compliance, etc.?
- Who *owns* this repo today? (Notice there are no CODEOWNERS.)
- What was the last serious incident this caused?

These questions reveal how you'd approach the review — context-first, not code-first.

### 5–25 min: Review

A strong review covers at least these dimensions:

**Terraform structure**
- 42 resources in "everything-else" is a smell; hard to blast-radius, hard to review, hard to plan incrementally
- State file without locking is a real risk — the "manual unlock" story is a near-miss
- Environment-per-directory with separate main.tf files is fine in principle but there's no evidence of module versioning; drift between envs is likely
- Prod unchanged for 11 months — either the team is too scared to touch it (a DevEx / trust problem) or it's genuinely stable (rare)

**GitOps / Kubernetes**
- ApplicationSets per env is reasonable, but no mention of sync waves or canary behavior
- 24 team directories with no CODEOWNERS = no ownership signal; reviews are probably going to whoever's available, not the right team
- Drifting Argo = reconciliation failing silently somewhere, or someone's making manual changes. Either is worth investigating specifically.

**Policy / guardrails**
- One policy in audit for 18 months is a dead policy — it's not a guardrail, it's decoration
- No image-scanning, no required-label enforcement, no resource-quota policy

**CI / secrets**
- 4 secrets in one org secret is a blast-radius risk; any of those compromises all 4
- No mention of branch protection, required reviewers, or environment-scoped secrets

**Process / ownership**
- No CODEOWNERS, docs 14 months stale, PR template with 7 checkboxes and only one about security — these are organizational smells, not technical ones, but they're real

### 25–35 min: Prioritize

Strong candidates don't present a laundry list. They prioritize.

**Recommended sequence**

1. **First 2 weeks:** fix the Terraform state file locking (real near-miss, can't be deferred); add CODEOWNERS (cheap, immediately valuable); decide whether the audit-mode policy gets enforced or deprecated
2. **First 30 days:** split the "everything-else" module into smaller modules with explicit blast radius; separate the CI secrets into per-environment scopes; investigate and fix the Argo drift (symptom of a deeper issue)
3. **First 90 days:** formalize environment promotion (what makes something promotable from staging to prod); add required image-scanning; document ownership for every team directory
4. **Later:** a proper platform roadmap informed by what the 90-day work revealed

### 35–45 min: Trade-offs and honesty

Strong candidates end with:

- **Wrong vs outdated vs acceptable** — the "everything-else" module is *wrong* (structurally bad); the 14-month-stale docs are *outdated* (bad but not urgent); the prod-untouched-11-months is either *wrong* (scared to deploy) or *acceptable trade-off* (genuinely stable), and you'd need data to know
- **What you would NOT change** — the environment-per-directory pattern is fine; the ApplicationSet approach is fine. Signal: you don't change what works.
- **The ownership and process issues are the most interesting** — technology problems are fixable in weeks; ownership problems shape culture. If you only have 30 days, CODEOWNERS and fixing the audit-mode policy matter more than refactoring Terraform modules.

---

## Interviewer notes (for a practice partner)

When running this mock with a partner, the partner should:

### Set the scene

Share the setup. Let the candidate ask clarifying questions. Answer some, don't volunteer information.

### Push back

Pick 1–2 of these during the session:

- "The 'everything-else' module was written by someone who has since left. Nobody really understands it well. How does that change your plan?"
- "We're about to hit a compliance audit in 90 days. Does that change your prioritization?"
- "Team A is going to fight any change to the Terraform structure — they're the biggest user and they've built tooling on the current layout. How do you handle them?"
- "Management wants to know 'what's the ROI of this cleanup' in dollar terms. What do you tell them?"
- "The person who set up the ApplicationSets swears the Argo drift is caused by a bug in Argo itself, not a config issue. Do you accept that or dig further?"

### Ask a follow-up

Around minute 30:

- "Of all the issues you flagged, which one is going to be hardest politically to fix?"
- "If you could only make one change in the next 2 weeks, which?"
- "What does a good version of this repo structure look like, specifically?"

### Score with the rubric

Use [`../rubrics/rubric-2-iac-review.md`](../rubrics/rubric-2-iac-review.md). Compare with candidate's self-score.

---

## Notes for your own future self

After completing this mock, write 3–4 sentences on:

1. Did you ask about context and ownership before critiquing code?
2. Did you distinguish wrong from outdated from acceptable?
3. Did you sequence by blast radius, or by what was most interesting?
4. What did you miss that a reviewer should have caught?

Keep these notes — they compound across multiple runs.
