# Scoring Rubrics

Rubrics for the 3 mock exercises.

---

## Why rubrics, not just "correct answers"

Platform engineering interviews are open-ended. There is rarely a single correct answer. What matters is:

- Did you ask the right questions before proposing?
- Did you make trade-offs explicit?
- Did you account for the users of the platform, not just the platform itself?
- Did you sequence work by value and risk, not by technical interest?
- Did you know what you don't know?

Rubrics capture these dimensions as scorable criteria, so you can self-evaluate — or have a peer evaluate — against something concrete.

## The three rubrics

| Rubric | Scores | Criteria |
|---|---|---|
| [`rubric-1-idp-design.md`](rubric-1-idp-design.md) | [`../mock/mock-1-idp-design.md`](../mock/mock-1-idp-design.md) | 7 criteria |
| [`rubric-2-iac-review.md`](rubric-2-iac-review.md) | [`../mock/mock-2-iac-review.md`](../mock/mock-2-iac-review.md) | 6 criteria |
| [`rubric-3-platform-incident.md`](rubric-3-platform-incident.md) | [`../mock/mock-3-platform-incident.md`](../mock/mock-3-platform-incident.md) | 7 criteria |

## Scoring scale (same across all three)

Each criterion scored 1–4:

- **1** — Did not address, or addressed incorrectly
- **2** — Addressed superficially; missed the platform-engineering framing
- **3** — Addressed well, platform-engineering framing clear
- **4** — Addressed with depth, articulated trade-offs, exceeded baseline expectations

### Score interpretation

- **Average ≥ 3.5** — ready for this level of interview
- **Average 3.0–3.4** — close; identify weakest criteria and focus practice; cold re-run after 48 hours
- **Average < 3.0** — more preparation needed; revisit the corresponding weeks of the plan before re-running

## Rubric principle — what's rewarded

- **Users over systems** — platforms exist for developers; prioritize their experience
- **Adoption over correctness** — a technically correct platform nobody uses is a failed platform
- **Sequencing** — what order you do things in matters as much as what you do
- **Honest trade-offs** — every choice costs something; say what
- **Platform vs tenant blame** — in incidents especially, the platform allowed what happened; "the engineer made a mistake" is not a senior framing

## Anti-rewards — things that score low even if technically correct

- Designing for scale you don't have yet
- Reinventing tools when off-the-shelf exists (and not explaining why)
- Proposing a migration with no stakeholder strategy
- Treating platform users as a constraint rather than a customer
- Optimizing for engineering elegance over developer outcomes
- Skipping the "did I talk to users?" question
- Naming the engineer who triggered an incident as the cause

## How to use these rubrics

1. Read the rubric for the mock **before** attempting the mock — know what you're being scored on
2. Attempt the mock under time pressure
3. Score yourself honestly (optimistic scoring wastes the exercise)
4. Write 3–4 sentences of notes on your weakest criterion
5. If the average is below 3.0, cold re-run after 48 hours — no reading the rubric again first; test whether the learning stuck
