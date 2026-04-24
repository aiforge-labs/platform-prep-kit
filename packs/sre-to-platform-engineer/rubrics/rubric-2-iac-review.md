# Rubric — Mock 2: IaC Review and Redesign

**Scoring rubric for [`../mock/mock-2-iac-review.md`](../mock/mock-2-iac-review.md)**

> **Terms used in this rubric**
> - **IaC** — Infrastructure-as-Code
> - **CODEOWNERS** — GitHub's file-path-to-owner mapping
> - **Blast radius** — set of tenants / services affected by a change or failure
> - **ROI** — Return on Investment
> - **Audit mode / Enforce mode** — policy-as-code states (Week 6)
> - **Rubber-stamp review** — a PR review approved without meaningful scrutiny
> - **Staff-level signal** — depth and breadth of thinking expected at senior/staff platform engineer level
>
> Full definitions and equivalent titles in the [pack README](../README.md#what-we-mean-by-sre).

This rubric scores the 45-minute IaC review mock. Six criteria, scored 1–4.

---

## Scoring scale

- **1** — Did not address, or addressed incorrectly (code-first without context)
- **2** — Addressed superficially; missed the platform-product framing
- **3** — Addressed well; platform-engineering framing clear
- **4** — Addressed with depth; articulated trade-offs; staff-level signal

**Score interpretation:**

- Average ≥ 3.5 — ready for senior/staff platform interviews
- Average 3.0–3.4 — close; cold re-run after 48 hours
- Average < 3.0 — re-prep needed; revisit Weeks 4, 5, 6 before re-running

---

## Criteria

### 1. Context before critique

The candidate asked about context, ownership, and incident history before critiquing code.

- **1** — Started listing issues in the code structure from minute 0
- **2** — Asked one generic context question, then launched into review
- **3** — Asked 3–5 substantive context questions (ownership, charter, incident history, business context) before review
- **4** — Above, plus explicitly said why context mattered — e.g., "I'm asking about incident history because code structure issues that aren't causing outages might be lower priority than ones that are"

This is the single most-weighted criterion. Reviewing code without context is the clearest SRE-framing tell.

### 2. Wrong vs outdated vs acceptable-trade-off distinction

The candidate distinguished between problems that are *structurally wrong*, *outdated but tolerable*, and *acceptable trade-offs someone made for a reason*.

- **1** — Labeled everything as wrong
- **2** — Labeled some things wrong; didn't articulate which were tolerable
- **3** — Clearly put at least 3 items in each of the three categories (wrong / outdated / acceptable)
- **4** — Above, plus acknowledged that the categorization itself depends on context the candidate hasn't been given — and named what they'd need to know to refine

### 3. Sequencing by blast radius and ROI

The candidate sequenced changes by impact and risk, not by what was most technically interesting.

- **1** — Presented a laundry list with no prioritization
- **2** — Prioritized, but by "what's easiest to fix" or "what's most bothering to me"
- **3** — Prioritized explicitly by blast radius + ROI — real-near-miss issues first, structural smells second, cosmetic issues last
- **4** — Above, plus named a specific item they would NOT prioritize (a deliberate de-prioritization with reason)

### 4. Process / ownership issues surfaced

The candidate recognized that some of the issues in the setup were organizational/process, not technical — and addressed them with at least equal weight.

- **1** — Focused entirely on code/structure issues
- **2** — Mentioned CODEOWNERS or docs-staleness but didn't treat as important
- **3** — Treated process issues (CODEOWNERS, stale docs, rubber-stamp PR template) as equally important
- **4** — Above, plus argued that process issues may matter *more* than the code issues — because code issues are fixable in weeks but ownership shapes culture

### 5. Stakeholder and political awareness

The candidate acknowledged that refactoring the Terraform structure, changing the state file approach, or deprecating the audit-mode policy will have political resistance from specific people.

- **1** — Treated the review as purely technical
- **2** — Mentioned "teams might not like this" generically
- **3** — Named specific stakeholders who'd object (Team A, the person who wrote the "everything-else" module, the policy owner) and had an approach for each
- **4** — Above, plus gave one concrete migration / rollout strategy for a politically-hard change (e.g., how to refactor the big module without making Team A's week painful)

### 6. Execution and communication

The candidate structured the review, managed time, and distinguished recommendations from observations clearly.

- **1** — Disorganized; ran out of time; key recommendations unclear
- **2** — Had structure but occasionally got lost in a code detail
- **3** — Named a structure (review dimensions, then prioritization, then trade-offs), stayed on it, ended on time with clear summary
- **4** — Above, plus explicitly said "what I won't change" as well as what they would — a senior move

---

## Overall score

Sum the 6 criteria scores (max 24). Divide by 6 for average.

- **3.5+ (21+)** — Strong. Ready for real interviews.
- **3.0–3.4 (18–20)** — Close. Cold re-run after 48 hours.
- **< 3.0 (< 18)** — Re-prep needed; revisit Weeks 4, 5, 6.

---

## Follow-up

Write 3–4 sentences after scoring:

1. What was my strongest criterion?
2. What was my weakest?
3. What did I miss that a good reviewer would have caught?
4. Did I fall into the trap of reviewing code without context?

---

## Common failure modes

### "Laundry list without prioritization"

Candidate lists 15 issues with the repo structure, doesn't prioritize, runs out of time. Reads as technically sharp but not executively useful. The prioritization step is what separates senior reviewers from the others.

### "Fix the most interesting thing first"

Candidate prioritizes the Terraform module refactor (technically interesting) over CODEOWNERS (boring but cheap + immediately valuable). Reads as prioritizing self-interest over user value.

### "Missing the political layer"

Candidate proposes changes without considering who'd push back and why. In real platform work, technical recommendations are the easy part; landing them is the hard part. Interviewers specifically look for candidates who show they understand this.

### "Not calling out 'no change needed'"

Candidate treats the review as a hunt for problems and forgets to signal what's *fine*. Strong reviewers explicitly say "I'd leave the environment-per-directory pattern alone — it's working" because it shows calibration, not reflex-criticize.
