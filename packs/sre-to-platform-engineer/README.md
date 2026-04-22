# SRE → Platform Engineer

A structured 12-week transition pack for senior SREs moving into Platform Engineering IC roles.

---

## Who this is for

You've been an SRE for 5+ years. You know on-call, SLOs, incident response, automation, and what it feels like to carry a pager for a business-critical system. You're considering — or already interviewing for — a Platform Engineer role at a team that's building an Internal Developer Platform (IDP), a golden-path toolchain, or a self-service infrastructure abstraction.

You are *not* a junior on-ramp. This pack assumes working familiarity with Linux, Kubernetes, Terraform/IaC, at least one cloud provider, and incident response fundamentals. We don't re-cover those.

## Who this is *not* for

- Junior engineers wanting their first SRE or Platform role
- SREs considering a move into engineering management (different skill set — a separate pack is planned)
- Product SWEs moving into infrastructure (also a different pack)
- People chasing "platform engineer" as a title rename of their current DevOps role without a real scope change

## Why this transition is hard

Most prep material treats Platform Engineering as "DevOps plus Kubernetes" or "SRE with more automation." It isn't. The core shift is a mindset change:

| From (SRE) | To (Platform Engineer) |
|---|---|
| Reactive operations | Proactive product thinking |
| Alerts and incidents | Internal developer experience (DevEx) |
| System availability | Developer productivity + platform reliability |
| Team-specific fixes | Reusable platforms, golden paths |
| "Ops for apps" | "Platform as a product" |
| Success = no pages | Success = developer NPS + adoption |

The technical overlap is large. The *framing* is completely different. Interviewers can tell in 15 minutes whether a candidate has made that shift or is still thinking like an SRE who happens to build tools. This pack is designed to help you make the shift and articulate it cleanly.

## What you get

- **12-week structured plan** — see [`plan.md`](plan.md). Roughly 6–8 hours/week, part-time alongside a day job.
- **20 STAR story prompts** — see [`stories/`](stories/). Each maps a typical SRE experience to a platform-engineering framing that interviewers are listening for.
- **3 scored mock exercises** — see [`mock/`](mock/). Platform system design, IaC review, on-call-to-platform translation.
- **Scoring rubrics** — see [`rubrics/`](rubrics/). How each exercise is evaluated, so you can self-score or have a peer evaluate.
- **Links into repo knowledge packs + quiz banks** — see [`links.md`](links.md). Maps every week to relevant reference material already in the repo.

## How to use it

The plan is designed for ~6–8 hours/week over 12 weeks. If you have more time, compress to 8 weeks. Less time, stretch to 16 — but don't drop the exercises, only the reading.

Each week follows the same rhythm:

1. **Read** — specific sections from public sources + repo knowledge packs
2. **Apply** — a small hands-on exercise (build, configure, review)
3. **Articulate** — 2–3 STAR prompts to practice talking about your existing experience in platform-engineer framing
4. **Self-assess** — short quiz from the repo's quiz banks

Weeks 11–12 are dedicated to interview simulation: system design, behavioral, and closing.

## Prerequisites

- Comfortable with: Linux, Kubernetes (can describe how a Deployment reconciles), Terraform, at least one cloud (AWS/GCP/Azure), CI/CD fundamentals
- Experience: 5+ years in SRE, DevOps, or infrastructure roles
- Hands-on environment: a sandbox you control (local kind/minikube, personal cloud account, or lab) — a few weeks have build exercises that require this

## What this pack does *not* include

- Kubernetes or Terraform fundamentals — use the official docs + CNCF training
- Coding interview prep (DSA, leetcode-style) — most platform roles don't require it; if yours does, this isn't the right resource
- People management / Engineering Manager prep
- Vendor-specific cloud certifications — adjacent but different goal
- Resume writing — this pack assumes your resume is already strong

## Outcomes

By week 12, you should be able to:

- Articulate the platform-as-product mindset using your own experience
- Design an internal developer platform from scratch in a 60-minute interview
- Explain GitOps, IaC governance, and policy-as-code in platform-engineering framing (not SRE framing)
- Translate 10+ of your SRE war stories into platform-engineering STAR format
- Critically review someone else's IaC or platform design and give actionable feedback
- Answer "why platform engineering for you, and why now?" in a way that isn't generic

## Feedback

This pack is a work in progress. If something is wrong, missing, or unclear, open an issue. Transition-specific content is most useful when it evolves with the community going through the transition.
