# Mock 3 — Platform Incident Response

**Scored mock exercise · 45 minutes · Week 11**

> **Terms used in this mock**
> - **SRE** — Site Reliability Engineer
> - **Platform Engineer** — the role you're transitioning to
> - **Blast radius** — the set of tenants / services affected
> - **MTTR** — Mean Time to Restore
> - **Postmortem** / **PIR** — Post-Incident Review
> - **Mitigation** — the action that stops the bleeding, not necessarily the root-cause fix
> - **GitOps** — Week 5: Git as source of truth, pull-based reconciliation
> - **Admission controller** — Kubernetes API server extension point for validation / mutation
> - **Comms** — short for "communications" — what you say to affected tenants, leadership, and the public (internal or external)
> - **Tenant** — a team, app, or environment consuming the platform
>
> Full definitions and equivalent titles in the [pack README](../README.md#what-we-mean-by-sre).

This mock simulates the operational scenario interview — a structured walk-through of an in-progress incident. It tests your handling of a platform-wide failure, comms, scope management, mitigation vs root-cause thinking, and postmortem framing.

Rubric: [`../rubrics/rubric-3-platform-incident.md`](../rubrics/rubric-3-platform-incident.md) — read **before** attempting.

---

## Setup

You are the senior Platform Engineer on call for your company's Internal Developer Platform. 40 product teams depend on it. The platform runs on Kubernetes, with GitOps (Argo CD) managing deployments, Kyverno at admission time for policy enforcement, and an in-house catalog service that teams use to register services and view ownership.

### The scenario

It's 14:30 on a weekday. Your dashboard flashes yellow and then red. You see:

- **Argo CD** is reporting `Sync` status for many Applications as stuck "Syncing" for 30+ minutes.
- **The Kyverno admission controller** is reporting a backlog of admission requests, with median admission-controller response time climbing from 150ms to 4.2 seconds.
- **The catalog service** seems fine.
- **Your paging system** triggered at 14:30 (15 minutes ago) on the Argo CD stuck-sync rule.

Slack messages are arriving:

- Team A (14:35): "Is anyone else seeing deploys stuck?"
- Team B (14:38): "We merged a PR at 14:05 and it's not deployed yet. Normal lag?"
- Team C (14:41): "Our canary failed to roll out — is the platform broken?"
- Team D (14:43): "We NEED to deploy a hotfix for a P1 customer issue. What's going on?"

You check recent platform changes:

- At 13:45, a platform engineer (not you) merged a PR that updated a Kyverno ClusterPolicy to start enforcing a new label requirement on Deployments. The PR reviewer was on PTO — one-person review, rubber-stamped.
- At 14:00, the new policy synced into production.
- At 14:10, Argo CD started triggering syncs (expected — this is when hourly reconciliations fire).
- Deploys started hanging around 14:15.

### Interviewer prompt

> *"Walk me through the next 45 minutes. What do you do, who do you talk to, how do you think about root cause and mitigation?"*

---

## How to run this mock

### Solo variant

1. Set a timer for 45 minutes.
2. Read the setup once. Re-read the timeline.
3. Write or speak through your response as if you were on the incident bridge.
4. Stop at 45 minutes.
5. Score using the rubric.

### With a practice partner

- Share the setup.
- Have them play the role of the incident commander or a peer engineer. At specific points, they inject updates (see Interviewer notes below).
- Score each other using the rubric.

---

## Suggested structure (for the candidate)

### 0–5 min: Form a hypothesis, don't yet act

Strong candidates resist the urge to fix immediately. First:

- Correlate the timeline: the 13:45 Kyverno policy merge lines up suspiciously with the admission-controller latency climbing
- Form the hypothesis: *the new Kyverno policy is slowing admission for a class of Deployments, which is cascading into Argo CD syncs appearing stuck because Argo is waiting for admission to succeed*
- Name the uncertainty: you don't *know* this yet — there could be a correlated unrelated issue

Before acting, you do two things in parallel:

1. Verify the hypothesis: check Kyverno logs for the specific policy's evaluation time or error rate
2. Start comms

### 5–10 min: Comms first, mitigation in parallel

A key platform-vs-SRE move here: platform incidents have *many* tenants, and silence is worse than imperfect information. Send an initial comms within the first 5 minutes of establishing a hypothesis:

**Initial internal comms (example)**

> 🚨 Platform incident in progress. Deploys are stuck across multiple teams. We believe this is related to a Kyverno policy update at 14:00 and are investigating. We'll have an update in 15 minutes. If you have an urgent deploy (P1 customer impact), message me directly.

Notes on that comms:

- Acknowledges scope ("multiple teams") without overclaiming or underclaiming
- Gives a rough hypothesis without committing to it as root cause
- Sets an update time (15 minutes)
- Offers an escalation path for truly urgent cases — Team D's P1 should not have to sit through general comms

### 10–20 min: Mitigate

Options, ranked:

1. **Revert the Kyverno policy PR.** Fastest path to restoration. Requires a fast-lane GitOps change — arguably you pause Argo briefly to prevent it reconciling a half-state.
2. **Disable the problematic ClusterPolicy.** Faster than revert-and-sync, but less auditable.
3. **Increase Kyverno resource allocation.** Only valid if the hypothesis is about resource starvation, not a pathological policy shape. Longer recovery.

The strong choice is usually (1), with a specific trade-off: the revert means the new policy's value (label enforcement) is lost for a while. That's acceptable during an active incident.

While revert is in flight, continue monitoring. Confirm admission latency returns to baseline. Confirm Argo catches up. Expect a queue-drain period (~5–15 minutes) even after the fix.

For Team D's P1: offer them a platform-assisted deploy that bypasses the admission controller for the specific workload (temporary ValidatingWebhookConfiguration bypass for that namespace). This is break-glass; document it in the incident log.

### 20–30 min: Stabilize and update

Second comms:

> Update: Argo sync queue is draining; admission latency is back to baseline. We've reverted the Kyverno policy that caused this. Deploys should resume in the next 5–10 minutes. We're monitoring. If you're still stuck after 14:30, ping me.

Now shift to:

- Confirm team-by-team that their deploys are recovering (quick check-ins with the 4 teams that Slacked you)
- Confirm no stragglers — Argo Applications that are still stuck after everyone else has drained usually have an additional independent issue
- Document the timeline in the incident doc as you go (not after — memory fades)

### 30–45 min: Postmortem framing

Strong candidates use the last 15 minutes to frame the postmortem — specifically the corrective actions.

**Root-cause framing — multi-layer**

- Proximate: the new Kyverno policy had a pathological shape for a subset of Deployments that caused admission latency to climb
- Process: the PR was reviewed by one person, who rubber-stamped it while the reviewer was on PTO — there's a review-standard gap
- Platform: the platform allowed a high-blast-radius policy to go from merge-to-production in 15 minutes, with no canary, no audit-mode soak, and no per-tenant gradual rollout
- Observability: the paging rule fired at 14:30, 15 minutes after the first sign of trouble; the admission latency climb from 150ms → 4.2s at 14:15 was visible but not paging

**Corrective actions — platform-level, not individual**

- All ClusterPolicy changes must go through audit-mode for 7 days before enforce
- Admission-controller latency SLI with paging at 500ms median (not just "Argo sync stuck")
- Canary rollout for platform-wide policy changes — apply to 1 namespace first, expand over 24 hours
- Two-person review standard for platform changes; PTO-aware review routing
- Break-glass procedure for bypassing admission in an incident — document the one you just used

**Things NOT in the postmortem**

- The engineer who merged the PR is not named and not blamed — the platform allowed it. The postmortem is about the platform's missing controls, not the engineer's mistake.
- "We should be more careful" — not a corrective action.

### Final comms

> Incident resolved. Full postmortem will be published within 72 hours. If you have questions, reach out. Thanks for your patience.

---

## Interviewer notes (for a practice partner)

When running this mock with a partner, the partner should:

### Set the scene

Read the setup aloud. Let the candidate ask clarifying questions for 2–3 minutes before diving into response.

### Inject updates during the session

At specific wall-clock points during the candidate's response, inject:

- **~8 minutes in:** "Team D just DMed you — they say the P1 customer is escalating to their CEO. What do you do?"
- **~12 minutes in:** "You go to revert the PR — but the author is offline and has force-push protection. How do you handle?"
- **~18 minutes in:** "Argo is drained, but 3 Applications are still stuck. On closer look, they're all services that use a shared base Helm chart that references a ConfigMap that referenced the specific policy's target resource. What do you do?"
- **~25 minutes in:** "A leadership person walks up to the incident bridge and asks for a status update. What do you tell them, in 30 seconds?"

Pick 2 or 3 of these — not all four.

### Ask a follow-up

Around minute 35:

- "Walk me through the postmortem as you'd write it. Who is and is not named?"
- "What's one corrective action you'd ship in the next 48 hours, and one in the next 30 days?"
- "In hindsight, is there a platform SLI that should have caught this earlier?"

### Score with the rubric

Use [`../rubrics/rubric-3-platform-incident.md`](../rubrics/rubric-3-platform-incident.md). Compare with candidate's self-score.

---

## Notes for your own future self

After completing this mock, write 3–4 sentences on:

1. Did you comms proactively, or did you handle mitigation first and comms later?
2. Did you separate "the engineer who triggered it" from "the platform that allowed it"?
3. Did you surface platform-level corrective actions, not just incident-specific ones?
4. Did you handle the break-glass case (Team D's P1) with appropriate care?

Keep these notes — they compound across multiple runs.
