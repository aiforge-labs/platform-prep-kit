# Phase 1 — Template Expansion Plan
**Goal:** Expand prep-agent to cover the full AI / Cloud DevOps / CloudSecOps domain.
**Scope:** Generic, per-person, open-source. Zero company-specific content.
**Status:** COMPLETE ✓

---

## Deliverables Overview

| # | Template File | Domain | Knowledge Pack | Quiz Bank | Status |
|---|---|---|---|---|---|
| 1 | `ai-platform-engineer.yml` | LLMOps, RAG, GenAI systems | `llmops-patterns.md` | `ai-platform-engineer.json` | DONE |
| 2 | `platform-engineer.yml` | IDP, Backstage, GitOps, Crossplane | `platform-engineering.md` | `platform-engineer.json` | DONE |
| 3 | `site-reliability-engineer.yml` | SLOs, observability, chaos, toil | `sre-fundamentals.md` | `sre-fundamentals.json` | DONE |
| 4 | `cloud-compliance-engineer.yml` | Policy-as-code, CIS, audit automation | `policy-as-code.md` | `cloud-compliance.json` | DONE |
| 5 | `ml-engineer.yml` | ML pipelines, feature stores, MLOps | `ml-lifecycle.md` | `ml-engineering.json` | DONE |
| 6 | `ai-security-engineer.yml` | LLM red-teaming, adversarial ML, AI threat modeling | *(reuse existing nist-ai-rmf, owasp-llm-top10, mitre-atlas)* | `ai-security.json` | DONE |
| 7 | `solutions-engineer.yml` | Presales, demo engineering, customer onboarding | `solutions-engineering.md` | `solutions-engineer.json` | DONE |
| 8 | `iac-gitops-engineer.yml` | Terraform, CDK, Pulumi, GitOps, ArgoCD | `iac-gitops.md` | `iac-gitops.json` | DONE |

---

## Quality Bar (match existing templates)

Every template must have:
- `name`, `description`, `version: 1`, `suggested_timeline`
- `bridge_from` — 3-4 source role backgrounds, each with `strengths`, `gaps`, `recommended_start`
- `tracks` — 5-7 tracks, each with:
  - `id`, `name`, `description`
  - Topics with: `id`, `name`, `estimated_hours`, `priority` (high/medium/low), `description`
  - Resources with: `title`, `url`, `type`, `free: true/false`
  - `quiz_bank` reference where a quiz bank exists
- `certifications_suggested` — 4-6 certs with `priority` ranking
- `interview_questions` — 8-10 technical + 4-5 leadership questions
- `content_suggestions` — 2-3 portfolio/blog post ideas

**Flexibility rules:**
- All resource URLs must be real, publicly accessible, preferably free
- `bridge_from` keys must be generic role slugs (e.g. `software_engineering`, not company-specific)
- No company names in topic descriptions or resource titles (OK in URLs to vendor docs)
- Each template stands alone — no cross-template dependencies required

---

## Template 1: `ai-platform-engineer.yml`

**Suggested timeline:** 10-12 weeks
**Domain:** Building, deploying, and operating GenAI/LLM-powered systems

### bridge_from
- `software_engineering` → gaps: GenAI architecture patterns, vector databases, model lifecycle
- `ml_engineering` → gaps: production serving at scale, LLMOps tooling, cost/latency tradeoffs
- `cloud_engineering` → gaps: LLM-specific infra (GPU scheduling, model registries), RAG design
- `backend_engineering` → gaps: embedding pipelines, retrieval evaluation, AI observability

### Tracks
1. **GenAI Foundations** — LLMs, tokenization, embeddings, context windows, prompt engineering
2. **RAG & Knowledge Systems** — chunking strategies, vector DBs (Pinecone, pgvector, Chroma, Weaviate), retrieval evaluation, hybrid search
3. **Model Serving & Inference** — vLLM, TGI (Text Generation Inference), Triton, latency/throughput/cost tradeoffs, batching
4. **AI Observability & Evaluation** — LLM eval frameworks (RAGAS, DeepEval), tracing (Langfuse, Phoenix), hallucination detection, drift monitoring
5. **LLMOps & Workflow Orchestration** — LangChain, LlamaIndex, DSPy, prompt versioning, A/B testing models
6. **Cloud AI Services** — AWS Bedrock, Google Vertex AI, Azure OpenAI — API patterns, quotas, cost management, private endpoints
7. **Interview Preparation** — System design for AI systems, RAG architecture walkthroughs

### Key Certifications
- AWS Certified Machine Learning – Specialty
- Google Professional Machine Learning Engineer
- DeepLearning.AI LLMOps Specialization (Coursera)
- Databricks Generative AI Engineer Associate

### Knowledge Pack: `llmops-patterns.md`
Cover: RAG architecture patterns, chunking strategies comparison, eval framework overview, observability tooling landscape, model serving tradeoffs table

### Quiz Bank: `ai-platform-engineer.json`
Topics: embeddings, vector similarity, RAG pipeline stages, model serving concepts, eval metrics (RAGAS scores, faithfulness, relevance)

---

## Template 2: `platform-engineer.yml`

**Suggested timeline:** 8-10 weeks
**Domain:** Building internal developer platforms (IDPs) and golden-path tooling

### bridge_from
- `software_engineering` → gaps: platform thinking, Kubernetes internals, IDP design patterns
- `cloud_engineering` → gaps: developer experience design, Backstage, self-service abstractions
- `devops_sre` → gaps: platform-as-a-product mindset, portal/catalog tooling
- `infrastructure_engineering` → gaps: application developer workflows, golden path templates

### Tracks
1. **IDP Concepts & Backstage** — platform-as-a-product, Backstage catalog, scaffolding plugins, TechDocs
2. **GitOps & Continuous Delivery** — ArgoCD, Flux, ApplicationSets, multi-cluster delivery
3. **Infrastructure Abstraction** — Crossplane, Terraform modules, Helm library charts, Pulumi Component Resources
4. **Self-Service & Developer Experience** — golden path templates, service catalog, developer portals
5. **Platform Observability** — Prometheus, Grafana, OpenTelemetry, platform SLOs
6. **Security & Policy Enforcement** — OPA Gatekeeper, Kyverno, admission controllers, namespace isolation
7. **Interview Preparation** — Platform design scenarios, build-vs-buy decisions

### Key Certifications
- Certified Kubernetes Administrator (CKA)
- ArgoCD Certification (CNCF)
- HashiCorp Terraform Associate
- AWS/GCP/Azure Professional DevOps/Cloud Engineer

### Knowledge Pack: `platform-engineering.md`
Cover: IDP maturity model, Backstage architecture overview, GitOps patterns (push vs pull), Crossplane vs Terraform comparison, golden path anatomy

### Quiz Bank: `platform-engineer.json`
Topics: Backstage concepts, GitOps pull model, Crossplane vs Terraform, OPA Gatekeeper vs Kyverno, ArgoCD sync strategies

---

## Template 3: `site-reliability-engineer.yml`

**Suggested timeline:** 8-10 weeks
**Domain:** Reliability engineering — SLOs, observability, incident response, toil elimination

### bridge_from
- `software_engineering` → gaps: production operations mindset, SLO design, on-call engineering
- `system_administration` → gaps: distributed systems reliability, SLI/SLO/SLA framework, chaos engineering
- `cloud_engineering` → gaps: application-layer reliability patterns, error budgets, post-mortems
- `network_engineering` → gaps: application performance monitoring, distributed tracing, toil automation

### Tracks
1. **SRE Principles & SLOs** — SLI/SLO/SLA definitions, error budget policy, toil measurement, SRE book foundations
2. **Observability** — metrics (Prometheus/Grafana), structured logging (Loki/ELK), distributed tracing (Jaeger/Tempo/OTEL), dashboards
3. **Incident Management** — on-call rotations, runbooks, blameless post-mortems, incident severity classification
4. **Reliability Patterns** — circuit breakers, retry/backoff, bulkheads, graceful degradation, load shedding
5. **Chaos Engineering** — chaos principles, Chaos Monkey/Litmus/Gremlin, game days, blast radius containment
6. **Automation & Toil Reduction** — toil identification, runbook automation, self-healing systems, capacity planning
7. **Interview Preparation** — SLO design exercises, incident walkthroughs, architecture reliability reviews

### Key Certifications
- Google Professional Cloud DevOps Engineer
- AWS Certified DevOps Engineer – Professional
- Certified Kubernetes Administrator (CKA)
- DASA DevOps Fundamentals

### Knowledge Pack: `sre-fundamentals.md`
Cover: SLI/SLO/SLA definitions and examples, error budget calculations, toil definition and measurement, blameless post-mortem template, reliability patterns glossary

### Quiz Bank: `sre-fundamentals.json`
Topics: SLO math (error budget burn rate), incident severity definitions, reliability patterns (circuit breaker vs bulkhead), chaos engineering principles, observability pillars

---

## Template 4: `cloud-compliance-engineer.yml`

**Suggested timeline:** 8-10 weeks
**Domain:** Automated cloud compliance, policy-as-code, CIS benchmarks, audit engineering

### bridge_from
- `cloud_engineering` → gaps: compliance frameworks, audit evidence collection, policy enforcement tooling
- `security_engineering` → gaps: IaC scanning, policy-as-code, automated remediation patterns
- `audit_compliance` → gaps: cloud-native controls, automated evidence, IaC and GitOps workflows
- `devops_engineer` → gaps: compliance-as-code, benchmark automation, regulatory mapping

### Tracks
1. **Compliance Frameworks** — CIS Benchmarks (AWS/Azure/GCP), SOC 2 Type II, PCI-DSS, ISO 27001, FedRAMP basics
2. **Policy-as-Code** — OPA/Rego, HashiCorp Sentinel, AWS SCPs, Azure Policy, GCP Org Policy
3. **Cloud Security Posture Management** — CSPM concepts, automated drift detection, continuous compliance monitoring
4. **IaC Security Scanning** — Checkov, tfsec, KICS, Terrascan — integrating into CI/CD
5. **Audit Automation & Evidence Collection** — automated evidence pipelines, control testing, compliance reporting
6. **Governance at Scale** — multi-account/subscription governance, landing zones, guardrails patterns
7. **Interview Preparation** — compliance design scenarios, policy authoring exercises

### Key Certifications
- AWS Certified Security – Specialty
- Certified Cloud Security Professional (CCSP)
- ISACA CISA (Certified Information Systems Auditor)
- CISSP (for senior roles)

### Knowledge Pack: `policy-as-code.md`
Cover: OPA/Rego primer, CIS benchmark structure, CSPM tool landscape, IaC scanning tools comparison, compliance framework mapping (SOC2 vs ISO vs PCI)

### Quiz Bank: `cloud-compliance.json`
Topics: CIS benchmark control categories, OPA/Rego syntax concepts, SOC 2 trust service criteria, CSPM vs CWPP distinction, SCP vs IAM policy precedence

---

## Template 5: `ml-engineer.yml`

**Suggested timeline:** 10-12 weeks
**Domain:** Building production ML systems — pipelines, feature stores, model lifecycle

### bridge_from
- `software_engineering` → gaps: ML-specific design patterns, experiment tracking, model serving infrastructure
- `data_engineering` → gaps: model training pipelines, experiment management, online feature serving
- `data_scientist` → gaps: production deployment, A/B testing, monitoring for data/concept drift
- `backend_engineering` → gaps: feature stores, ML pipeline orchestration, model versioning

### Tracks
1. **ML Foundations for Production** — supervised/unsupervised/generative overview, loss functions, overfitting/underfitting, production vs research ML
2. **Data Pipelines & Feature Engineering** — feature stores (Feast, Tecton), data versioning (DVC), feature transformation patterns
3. **Experiment Tracking & Model Registry** — MLflow, Weights & Biases, experiment reproducibility, model versioning
4. **Model Training at Scale** — distributed training (Ray, Horovod), GPU/TPU utilization, hyperparameter tuning (Optuna, Ray Tune)
5. **Model Deployment & Serving** — BentoML, Seldon, KServe, A/B testing, shadow mode, canary deployments
6. **ML Monitoring & Observability** — data drift (Evidently, WhyLogs), model performance degradation, alerting strategies
7. **Cloud ML Services** — SageMaker Pipelines, Vertex AI Pipelines, Azure ML — when to use managed vs custom
8. **Interview Preparation** — ML system design, trade-off discussions, debugging scenarios

### Key Certifications
- AWS Certified Machine Learning – Specialty
- Google Professional Machine Learning Engineer
- Databricks Certified Machine Learning Professional
- Azure AI Engineer Associate

### Knowledge Pack: `ml-lifecycle.md`
Cover: ML project lifecycle stages, feature store concepts, experiment tracking comparison, model deployment patterns (blue/green, canary, shadow), drift monitoring taxonomy

### Quiz Bank: `ml-engineering.json`
Topics: feature store online vs offline serving, train/serve skew, model drift types, SageMaker pipeline components, experiment tracking concepts, deployment strategy tradeoffs

---

## Template 6: `ai-security-engineer.yml`

**Suggested timeline:** 8-10 weeks
**Domain:** Securing AI systems — red-teaming, adversarial ML, governance implementation

### bridge_from
- `security_engineering` → gaps: ML-specific attack vectors, AI governance frameworks, LLM-specific testing
- `ml_engineer` → gaps: adversarial robustness, security review processes, compliance frameworks for AI
- `cloud_security` → gaps: AI-specific threat modeling, LLM application security, model supply chain
- `penetration_testing` → gaps: AI/ML attack taxonomy, LLM red-teaming methodology, AI-specific tooling

### Tracks
1. **AI Attack Taxonomy** — MITRE ATLAS tactics, data poisoning, model evasion, model stealing, inference attacks
2. **LLM Security** — prompt injection, jailbreaking, indirect injection, output manipulation, OWASP LLM Top 10
3. **LLM Red-Teaming** — red-team methodology for LLM applications, adversarial prompt libraries, automated fuzzing
4. **AI Governance Implementation** — NIST AI RMF implementation, EU AI Act compliance, model risk management
5. **Secure AI System Design** — security architecture patterns for AI pipelines, model supply chain security, SBOM for ML
6. **AI Incident Response** — detecting model abuse, response playbooks, forensics for AI systems
7. **Interview Preparation** — AI threat modeling exercises, governance scenario discussions

### Key Certifications
- AWS Certified Security – Specialty
- GIAC Cloud Security Automation (GCSA)
- Certified Ethical Hacker (CEH) — for red-team track
- CISSP (for governance-heavy roles)

*(Reuses knowledge packs: nist-ai-rmf.md, owasp-llm-top10.md, mitre-atlas.md)*

### Quiz Bank: `ai-security.json`
Topics: MITRE ATLAS tactic categories, OWASP LLM Top 10 vulnerabilities, NIST AI RMF functions, prompt injection vs jailbreaking distinction, data poisoning types

---

## Template 7: `solutions-engineer.yml`

**Suggested timeline:** 6-8 weeks
**Domain:** Technical presales, demo engineering, proof-of-concept, customer onboarding

### bridge_from
- `software_engineering` → gaps: presales process, customer discovery, commercial awareness
- `cloud_engineering` → gaps: solution narrative, business value articulation, multi-stakeholder communication
- `customer_success` → gaps: technical depth, architecture solutioning, proof-of-concept execution
- `technical_support` → gaps: proactive solution design, sales cycle, competitive differentiation

### Tracks
1. **Technical Discovery** — qualification questions, pain point mapping, stakeholder mapping, technical requirements gathering
2. **Solution Architecture for Sales** — designing lightweight, compelling architectures, scope management, trade-off communication
3. **Demo Engineering** — building reusable demo environments, scripted vs live demos, handling objections
4. **Proof-of-Concept Delivery** — scoping POCs, success criteria definition, timeboxed delivery, POC-to-production narrative
5. **Technical Communication** — writing RFP responses, solution briefs, technical slide decks, whiteboarding techniques
6. **Domain Depth** — deep-dive in one of: cloud governance, DevSecOps, AI/ML, platform engineering (user's choice)
7. **Interview Preparation** — mock discovery calls, demo walkthroughs, business case construction

### Key Certifications
- AWS Certified Solutions Architect – Professional
- Google Professional Cloud Architect
- Azure Solutions Architect Expert
- Challenger Sales Methodology (for SE-specific skills)

### Knowledge Pack: `solutions-engineering.md`
Cover: SE vs CSM vs SA distinction, discovery question frameworks, POC scoping guide, demo environment patterns, business value articulation techniques

### Quiz Bank: `solutions-engineer.json`
Topics: discovery question types, POC success criteria design, objection handling patterns, cloud architecture trade-offs for sales context, stakeholder communication frameworks

---

## Template 8: `iac-gitops-engineer.yml`

**Suggested timeline:** 8-10 weeks
**Domain:** Infrastructure as Code, GitOps, policy-as-code, cloud automation

### bridge_from
- `devops_engineer` → gaps: declarative IaC at scale, GitOps pull model, policy enforcement in pipelines
- `cloud_engineer` → gaps: IaC testing strategies, module design patterns, multi-environment management
- `software_engineering` → gaps: infrastructure lifecycle management, state management, cloud resource modeling
- `system_administration` → gaps: declarative vs imperative automation, version-controlled infra, CI/CD for infra

### Tracks
1. **IaC Fundamentals** — declarative vs imperative, Terraform HCL deep dive, state management, workspaces, backends
2. **IaC at Scale** — module design patterns, Terragrunt, CDK constructs, Pulumi component resources, monorepo vs multi-repo
3. **GitOps Patterns** — pull vs push models, ArgoCD, Flux, ApplicationSets, multi-cluster management, drift detection
4. **IaC Testing & Validation** — Terratest, checkov, tfsec, KICS, contract testing, integration testing for infrastructure
5. **Policy-as-Code for IaC** — OPA/Rego for Terraform, Sentinel, Kyverno for Kubernetes manifests, pre-commit hooks
6. **Multi-Cloud & Multi-Environment Patterns** — environment promotion pipelines, secrets injection, cloud-agnostic abstractions
7. **Interview Preparation** — IaC architecture design, refactoring legacy infra scenarios, policy enforcement design

### Key Certifications
- HashiCorp Terraform Associate / Professional
- AWS DevOps Engineer – Professional
- Google Professional Cloud DevOps Engineer
- Certified Kubernetes Administrator (CKA)

### Knowledge Pack: `iac-gitops.md`
Cover: Terraform state management primer, GitOps pull model explanation, IaC testing pyramid, Terragrunt vs Terraform workspaces, ArgoCD vs Flux comparison

### Quiz Bank: `iac-gitops.json`
Topics: Terraform state locking, remote backend types, GitOps sync strategies, ArgoCD ApplicationSet generators, Rego policy basics, IaC testing levels

---

## Implementation Order

Build in this priority sequence (highest demand / most cross-template value first):

```
Round 1 (build first):
  [1] ai-platform-engineer    — highest market demand, AI-native
  [2] site-reliability-engineer — universal pivot target, well-defined domain
  [3] platform-engineer       — IDP space growing fast, Backstage adoption rising

Round 2:
  [4] ml-engineer             — complements ai-platform-engineer
  [5] iac-gitops-engineer     — foundational, complements platform-engineer

Round 3:
  [6] ai-security-engineer    — extends existing AI security content
  [7] cloud-compliance-engineer — extends existing cloud security content
  [8] solutions-engineer      — broadest audience, good community draw
```

---

## Per-Template Checklist

For each template, complete these artifacts:
- [ ] `templates/<slug>.yml` — full template with all required fields
- [ ] `knowledge_packs/<slug>.md` — knowledge pack (if new, not reusing existing)
- [ ] `quiz_banks/<slug>.json` — quiz bank with ≥15 questions in existing format
- [ ] Template validated: `prep template validate templates/<slug>.yml`
- [ ] Linked from `README.md` templates table

---

## Notes on Flexibility

"Flexible" means:
1. **bridge_from** covers all realistic incoming backgrounds (not just one path)
2. **Resource mix** — free resources prioritized, paid optional, multi-cloud where relevant
3. **Priority levels** — `high`/`medium`/`low` let users skip lower-priority topics if time-constrained
4. **quiz_bank** is optional per topic — core theory topics always have one; niche topics may not
5. **Content suggestions** — portfolio ideas, not prescriptive deliverables
6. No assumed starting knowledge beyond stated `bridge_from` backgrounds
