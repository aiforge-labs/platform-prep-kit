# STAR Story Prompts

20 prompts to practice translating SRE experience into platform-engineering framing. Used mainly in Week 12 (Behavioral + Closing).

---

## Why this exists

Interviewers for platform engineer roles listen for a specific *framing*, not specific technologies. The same experience — e.g., "I automated our deployment pipeline" — reads as a strong SRE story, a weak platform story, or a strong platform story depending on how it's told.

**SRE framing (what not to do):**
> "We had a lot of deploy failures, so I wrote a pipeline that validated manifests and rolled back on failure. It cut our deploy incidents by 40%."

**Platform framing (what to do):**
> "Our product teams were blocked by slow, unreliable deploys. I treated them as customers and ran a DevEx survey — lead-time and deploy confidence were the top two pains. I built a paved-path pipeline with built-in validation and automatic rollback, then measured adoption. Within a quarter, 18 of 24 teams had self-migrated; deploy-related incidents dropped 40%; developer-reported deploy confidence went from 3.2 to 4.4 out of 5. The unexpected lesson: the automation was secondary — the biggest unlock was that teams now trusted the process."

Same underlying work. Completely different signal to the interviewer.

---

## Structure

Each prompt includes:

- **Prompt** — an interview-style question
- **SRE trap** — how an SRE typically answers this (and why it reads as weak)
- **Platform framing** — what the interviewer is actually listening for
- **Coaching rubric** — 4–5 criteria to self-score your answer
- **Example shape** — a sample answer scaffold (replace with your real story)

## Categories

The 20 prompts are organized into 6 category files:

| File | Prompts | Focus |
|---|---|---|
| [`01-technical-leadership.md`](01-technical-leadership.md) | 3 | Designing, trade-offs, deprecating |
| [`02-customer-empathy.md`](02-customer-empathy.md) | 4 | Finding pain, saying no, migration, validation |
| [`03-reliability-to-platform.md`](03-reliability-to-platform.md) | 4 | On-call learnings, postmortems, cross-team reliability, runbook-to-capability |
| [`04-influence-without-authority.md`](04-influence-without-authority.md) | 3 | Adoption, alignment, skeptics |
| [`05-failure-stories.md`](05-failure-stories.md) | 3 | Nobody used, wrong abstraction, missed signal |
| [`06-career-motivation.md`](06-career-motivation.md) | 3 | Why platform, why now, what you'd change |

## How to use them

1. Work through the categories in order (Week 12 recommends 1.5 hours of review, 2–3 hours of practice).
2. For each prompt, identify the story from your career that maps to it.
3. Draft a 2–3 minute answer following the Example shape.
4. Score with the rubric for that prompt.
5. Record yourself delivering it. Listen back.
6. Revisit in Week 12 for the final polish — pick your strongest 8 of the 20 for interview day.

## The "point of view" question

A common additional prompt at senior level — *"tell me something you believe about platform engineering that many of your peers disagree with"* — is covered in [`../weeks/week-12-behavioral.md`](../weeks/week-12-behavioral.md), because it's meta to the 20 STAR prompts.
