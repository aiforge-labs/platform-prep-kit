# Rubric — Mock 3: Platform Incident Response

**Scoring rubric for [`../mock/mock-3-platform-incident.md`](../mock/mock-3-platform-incident.md)**

> **Terms used in this rubric**
> - **Mitigation** — the action that stops the bleeding, not necessarily the root-cause fix
> - **Blast radius** — set of tenants affected
> - **Comms** — communications with affected tenants and leadership
> - **Postmortem** / **PIR** — Post-Incident Review
> - **Break-glass** — manual bypass of normal procedure during an incident
> - **Blameless postmortem** — a postmortem that focuses on system-level causes, not individual blame
> - **Staff-level signal** — depth of thinking expected at senior/staff platform engineer level
>
> Full definitions and equivalent titles in the [pack README](../README.md#what-we-mean-by-sre).

This rubric scores the 45-minute platform incident response mock. Seven criteria, scored 1–4.

---

## Scoring scale

- **1** — Did not address, or addressed incorrectly (single-app incident framing)
- **2** — Addressed superficially; missed the platform-tenant framing
- **3** — Addressed well; platform-level framing clear
- **4** — Addressed with depth; staff-level signal

**Score interpretation:**

- Average ≥ 3.5 — ready for senior/staff platform interviews
- Average 3.0–3.4 — cold re-run after 48 hours
- Average < 3.0 — revisit Weeks 6, 9, 10 before re-running

---

## Criteria

### 1. Hypothesis before action

The candidate formed a hypothesis (and named the uncertainty) before acting.

- **1** — Started mitigating immediately without a hypothesis
- **2** — Named a hypothesis but didn't acknowledge uncertainty
- **3** — Stated a specific hypothesis, named what would verify or refute it
- **4** — Above, plus kept verification running in parallel with mitigation — not sequentially

### 2. Comms-first posture

The candidate initiated tenant comms early, in parallel with mitigation, not after resolution.

- **1** — Comms mentioned only after resolution (or not at all)
- **2** — Comms mentioned after mitigation but before second comms
- **3** — Initial comms within the first 5 minutes; second update at expected interval; final comms on resolution
- **4** — Above, plus differentiated the comms: general announcement to all tenants, escalation path for P1 urgency, private factual note to the engineer who merged the triggering change

This is a core platform-vs-SRE-incident signal. App incidents usually have 1 stakeholder (the owning team); platform incidents have many, and silence is costly.

### 3. Mitigation chosen with trade-offs

The candidate chose a mitigation, named alternatives, and articulated the trade-off.

- **1** — Single action, no alternatives considered
- **2** — Named 2+ alternatives but didn't compare
- **3** — Compared revert vs disable vs tune-resources, chose with explicit reasoning
- **4** — Above, plus acknowledged the *cost* of the chosen mitigation (e.g., "reverting loses the new policy's value temporarily; we'll re-enable with a canary rollout when investigated")

### 4. Platform-level root cause vs tenant blame

The candidate distinguished "the engineer who triggered it" from "the platform that allowed it."

- **1** — Root cause centered on the engineer who merged the PR
- **2** — Acknowledged the platform's role but gave it less weight than the engineer's mistake
- **3** — Clearly placed primary weight on the platform-level missing controls; engineer's action was a symptom
- **4** — Above, plus articulated corrective actions that remove the class of failure (audit-mode soak, canary rollout, admission-controller SLI with paging)

This is the single most-weighted criterion. Getting this wrong is a senior-level disqualifier in platform roles.

### 5. Break-glass handled responsibly

The candidate handled the Team D P1 case (or the partner's injected P1 update) with appropriate care — granting the bypass while documenting it, not just denying or ignoring.

- **1** — Ignored the P1 request, or granted access without documentation
- **2** — Granted the bypass but didn't mention documentation or auditability
- **3** — Granted a specific, scoped bypass with documentation in the incident log
- **4** — Above, plus framed the break-glass event as a platform feature (the fact that it exists, is auditable, and has a defined procedure) and flagged that "break-glass usage" is itself a platform-health metric to track

### 6. Postmortem framing

The candidate's postmortem framing is blameless, multi-layer, with platform-level corrective actions.

- **1** — Postmortem names the engineer; corrective actions are "be more careful"
- **2** — Blameless tone but corrective actions are vague
- **3** — Multi-layer root cause (proximate, process, platform, observability); specific corrective actions at each layer
- **4** — Above, plus explicit articulation of what is NOT in the postmortem (the engineer's name, speculation about their state, generic "we should improve")

### 7. Execution under pressure

The candidate handled the time pressure, injected updates, and leadership-facing comms without losing structure.

- **1** — Disorganized; lost the thread when an update was injected; leadership interaction was awkward
- **2** — Mostly held structure; one moment of visible pressure
- **3** — Maintained structure throughout; handled injected updates without losing track of existing work
- **4** — Above, plus handled the leadership-status moment crisply — 30 seconds of clear signal, specific timeline, and appropriate confidence

---

## Overall score

Sum the 7 criteria scores (max 28). Divide by 7 for average.

- **3.5+ (24.5+)** — Strong. Ready for real interviews.
- **3.0–3.4 (21–24)** — Cold re-run after 48 hours.
- **< 3.0 (< 21)** — Re-prep needed; revisit Weeks 6, 9, 10.

---

## Follow-up

Write 3–4 sentences after scoring:

1. Did I lead with comms or with mitigation?
2. Did I distinguish tenant-triggered from platform-allowed?
3. Did I handle the P1 / break-glass case responsibly?
4. What was my weakest criterion?

---

## Common failure modes

### "Mitigation first, comms later"

Candidate spends 20 minutes on the technical mitigation, then sends a single after-the-fact comms. Single-app instinct. Platform incidents need *parallel* comms — tenants can do something with "we're investigating" that they can't do with silence.

### "Root cause = the engineer's mistake"

Candidate's postmortem names the engineer (or implicitly makes them the cause). Interviewers treat this as a senior disqualifier. The correct framing is always: the platform allowed a single-review PR to deploy a high-blast-radius policy with no canary. The engineer is a symptom.

### "The break-glass is the exception, not the norm"

Candidate grants Team D's bypass without documenting it, or without surfacing that break-glass usage is itself a health metric. Strong candidates treat break-glass as a platform feature with its own process — including observability.

### "Laundry-list corrective actions"

Candidate lists 10 corrective actions from the postmortem. Reads as un-prioritized. Strong candidates pick 2 high-priority platform-level changes they'd ship in 48 hours and one larger structural change in 30 days.

### "Running out of time before postmortem framing"

Candidate spends 40 minutes on mitigation details and doesn't have time for postmortem framing. Postmortem framing is where the senior signal lives — don't crowd it out.
