# Solutions Engineering

A reference guide for Solutions Engineers — discovery methodology, POC design, business value articulation, and demo engineering.

---

## 1. SE vs CSM vs SA vs PSE

| Role | Primary motion | Success metric | When engaged |
|---|---|---|---|
| Solutions Engineer (SE) | Pre-sales: prove value | Deal closed | Qualification → close |
| Customer Success Manager (CSM) | Post-sales: ensure adoption | Retention/expansion | After signature |
| Solutions Architect (SA) | Technical design for implementation | Implementation success | Post-sale, pre-deploy |
| Professional Services Engineer (PSE) | Hands-on implementation | Delivery completion | Post-sale, implementation |

An SE's job ends (mostly) when the contract is signed. A CSM's job begins there.

---

## 2. Technical Discovery Framework

### Question categories (SPIN adapted for technical SE)

**Situation questions** — establish current state:
- "Walk me through your current infrastructure for X."
- "How many teams are affected by this?"
- "What tools do you currently use for Y?"
- "How are you handling Z today?"

**Problem questions** — identify pain:
- "What are the biggest friction points in your current workflow?"
- "Where does your current approach break down at scale?"
- "What does a bad day look like for your team?"
- "What is the most manual, repetitive work your team does?"

**Implication questions** — quantify business impact:
- "When that fails, what is the downstream impact?"
- "How much engineering time does that take per week/month?"
- "Has this caused any compliance issues or audit findings?"
- "What has been the cost of incidents caused by this?"

**Need-payoff questions** — connect to value:
- "If you could eliminate that manual work, what would the team do with the time?"
- "How valuable would it be to have continuous visibility into your compliance posture?"
- "What would it mean for your team if onboarding a new cloud account took minutes instead of weeks?"

### Discovery call structure (60 minutes)
```
0-5 min    Agenda setting and rapport
5-20 min   Current state — let them talk, take notes
20-35 min  Problem probing — implication questions
35-50 min  Solution mapping — show how product addresses specific pain
50-60 min  Next steps — propose POC/demo, identify mutual success criteria
```

---

## 3. Stakeholder Personas

### Developer/Engineer
- **Cares about:** Does it work? Is it easy to use? Does it slow me down?
- **Language:** Technical specifics, code, CLI, integration details
- **Win them with:** A working demo in their environment, technical depth, honest trade-off discussion

### Engineering Manager / Architect
- **Cares about:** Team productivity, maintainability, reliability, vendor risk
- **Language:** Architecture trade-offs, team workflow impact, operational overhead
- **Win them with:** Reference architectures, migration path clarity, support responsiveness

### CTO / VP Engineering
- **Cares about:** Risk, cost, competitive advantage, make-vs-buy
- **Language:** Business outcomes, ROI, organizational impact
- **Win them with:** Business case with numbers, peer company references, strategic fit

### CISO / Security Lead
- **Cares about:** Risk reduction, compliance coverage, data handling
- **Language:** Controls, compliance frameworks, audit evidence
- **Win them with:** Security questionnaire responses, compliance certifications, pen test reports

---

## 4. Business Value Articulation

### Value categories
1. **Cost reduction** — lower cloud spend, fewer headcount needed for manual work
2. **Risk reduction** — fewer breaches, faster incident detection, compliance maintained
3. **Revenue protection** — system reliability, faster recovery from incidents
4. **Productivity gain** — developer time saved, faster onboarding, eliminated toil
5. **Competitive advantage** — faster time to market, better developer experience

### ROI calculation framework
```
Annual Value = (Time saved per week × Engineer hourly rate × 52 weeks)
             + (Risk reduction × Probability of incident × Cost of incident)
             + (Compliance cost reduction — auditor hours, tooling)

Annual Cost = License fee + Implementation cost + Ongoing maintenance

ROI = (Annual Value - Annual Cost) / Annual Cost × 100%
```

### Cost of doing nothing
The most powerful reframe: quantify what the current situation costs, not just what your solution delivers.
- "Your team spends 20 hours/week on manual compliance checks. At $150/hr fully-loaded that's $156,000/year."
- "Your last compliance failure cost $200,000 in remediation and auditor fees."
- "At your current deployment frequency, you're leaving X weeks of developer velocity on the table."

---

## 5. POC Design Principles

### What makes a good POC
1. **Scoped to 3-5 success criteria** — not an unlimited evaluation
2. **Success criteria are measurable and pre-agreed** — no surprise goalpost moves
3. **Timeboxed** — 2-4 weeks maximum for most B2B products
4. **Mutual commitment** — customer provides access, data, and dedicated time
5. **Executive sponsor identified** — someone who can champion the result internally

### Mutual success plan template
```
POC Mutual Success Plan
Product: [Product name]
Customer: [Company]
Duration: [Start date] → [End date]
SE Owner: [Name]    Customer Lead: [Name]

Success Criteria:
1. [Criterion] — Measure: [how to measure] — Owner: [customer]
2. [Criterion] — Measure: [how to measure] — Owner: [customer]
3. [Criterion] — Measure: [how to measure] — Owner: [SE]

Week 1: Environment setup, data access, [deliverable]
Week 2: [Use case 1 demonstration], [milestone]
Week 3: [Use case 2 demonstration], [milestone]
Week 4: Results review, executive presentation, next steps discussion

Dependencies from customer: [Access, data, team time]
Rollback / exit criteria: If [condition], we mutually agree to [action]
```

### Handling a struggling POC
- **Week 1 issues:** Usually environment/access problems — escalate immediately, don't wait
- **Scope creep:** Politely reanchor to the original success criteria document
- **Technical blocker:** Escalate to engineering, set clear timeline, don't let it drift
- **Stakeholder disengagement:** Escalate to executive sponsor, request dedicated customer resource

---

## 6. Demo Engineering Best Practices

### Demo environment principles
- **Reproducible:** Scripted setup, version-controlled, any SE can recreate it
- **Realistic data:** Synthetic but realistic — not `test_user_1`, not real PII
- **Controlled narrative:** Demo script guides the story, no live dependencies that can fail
- **Version-pinned:** Know which product version the demo runs on

### Demo story arc
```
1. Set the scene: "Here's a company like yours..."
2. Show the pain: "This is what their day looks like today..."
3. Introduce the solution: "With [product], here's what changes..."
4. Show the outcome: "And here's the business result..."
5. Invite engagement: "Does this match what you're experiencing?"
```

### Handling live demo failures
- **Stay calm** — your reaction matters more than the failure
- Have a backup: screenshots, a recorded video of key moments
- "This is something we'd fix before production — let me show you the expected behavior"
- If critical: pause, apologize briefly, move to a working section, follow up with a clean recording

---

## 7. Objection Handling Framework

**Structure: Acknowledge → Clarify → Respond → Confirm**

1. **Acknowledge:** Show you heard and respect the concern
   - "That's a fair concern and I've heard it from other teams in your position."
2. **Clarify:** Is this a blocker or a question?
   - "Is this a hard requirement for moving forward, or more something you'd want to understand better?"
3. **Respond:** Address directly with evidence, reference, or next step
   - Facts > assertions. Use customer references, documentation, or propose a test.
4. **Confirm:** Check if the response resolved the concern
   - "Does that address your concern, or would it be helpful to dig into this further?"

### Common objections and responses

| Objection | Response approach |
|---|---|
| "We could build this ourselves" | Total cost of build (engineering time, maintenance, opportunity cost) vs buy. Time-to-value. |
| "Your competitor does X better" | Acknowledge what's true. Reframe to your differentiation. Offer a direct comparison test in POC. |
| "We're already committed to vendor Y" | Understand the depth of commitment. Identify the gaps vendor Y doesn't address. Coexistence story. |
| "We don't have budget" | Is this "no budget exists" or "not budgeted this cycle"? Identify the pain cost. Q1 planning conversation. |
| "It won't integrate with our stack" | Specific integration requirements → propose a technical validation in the POC. |
