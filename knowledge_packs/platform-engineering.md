# Platform Engineering

A reference guide covering internal developer platforms, GitOps patterns, infrastructure abstraction, and developer experience tooling.

---

## 1. Platform Engineering vs DevOps vs SRE

| Dimension | DevOps | SRE | Platform Engineering |
|---|---|---|---|
| Primary focus | Delivery velocity and collaboration | Reliability and operational excellence | Developer experience and self-service |
| Core output | CI/CD pipelines, culture change | SLOs, runbooks, reliability automation | Internal developer platform (IDP) |
| Success metric | Deployment frequency, lead time | SLO compliance, error budget burn | Developer NPS, golden path adoption, DORA |
| Organizational model | Practice/mindset (no dedicated team) | Dedicated reliability team | Dedicated platform product team |

---

## 2. IDP Maturity Model (CNCF)

| Level | Description | Characteristics |
|---|---|---|
| 0 | No platform | Each team provisions infrastructure independently |
| 1 | Scripts & conventions | Shared scripts, naming conventions, no portal |
| 2 | Self-service paved road | Golden path templates, some automation, manual approval |
| 3 | Self-service platform | Portal (Backstage), automated provisioning, standardized workflows |
| 4 | Managed platform | SLOs for platform services, roadmap-driven, developer NPS tracking |
| 5 | Ecosystem | Plugin marketplace, community contributions, external adoption |

Most organizations are at Level 1-2. Level 3 is the target for medium-large engineering orgs.

---

## 3. Backstage Architecture

```
┌─────────────────────────────────────────────────┐
│                   Backstage                      │
│                                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────────┐  │
│  │ Catalog  │  │Templates │  │   TechDocs   │  │
│  │(entities)│  │(scaffold)│  │(docs-as-code)│  │
│  └──────────┘  └──────────┘  └──────────────┘  │
│                                                  │
│  ┌──────────────────────────────────────────┐   │
│  │           Plugin Ecosystem               │   │
│  │  (Kubernetes, CI/CD, Cost, Security...)  │   │
│  └──────────────────────────────────────────┘   │
│                                                  │
│  ┌──────────┐  ┌──────────────────────────┐    │
│  │  Search  │  │  Auth (GitHub/OIDC/LDAP) │    │
│  └──────────┘  └──────────────────────────┘    │
└─────────────────────────────────────────────────┘
```

**catalog-info.yaml anatomy:**
```yaml
apiVersion: backstage.io/v1alpha1
kind: Component
metadata:
  name: payment-service
  description: Handles all payment processing
  tags: [payments, critical]
  annotations:
    github.com/project-slug: myorg/payment-service
    backstage.io/techdocs-ref: dir:.
spec:
  type: service
  lifecycle: production
  owner: payments-team
  system: checkout
  dependsOn:
    - component:fraud-detection-service
  providesApis:
    - payment-api
```

**Entity kinds:** Component, API, Resource, System, Domain, Group, User, Template, Location

---

## 4. GitOps: Push vs Pull Model

### Push model (traditional CI/CD)
```
Code Push → CI builds → CI calls kubectl/helm → Kubernetes
```
- CI system has direct access to the cluster (credential risk)
- No automatic drift correction
- Rollback = re-run the previous pipeline

### Pull model (GitOps)
```
Code Push → CI builds → CI writes to Git → GitOps operator detects diff → operator applies to Kubernetes
```
- Credentials live inside the cluster (not in CI)
- Automatic drift correction: operator continuously reconciles desired vs actual state
- Rollback = git revert (infrastructure change is a code change)

### Pull model operators comparison

| | ArgoCD | Flux |
|---|---|---|
| Architecture | Monolithic app with UI | Composable controllers (source, kustomize, helm, notification) |
| UI | Rich built-in web UI | Minimal (Weave GitOps for full UI) |
| Multi-cluster | ApplicationSets, hub-spoke | Flux with cluster API |
| Multi-tenancy | AppProject isolation | Namespace/tenant reconciliation |
| Learning curve | Moderate | Steeper (multiple controllers) |
| Best for | Teams that want a UI-first experience | Teams that prefer Kubernetes-native, composable approach |

---

## 5. Crossplane vs Terraform

| Dimension | Crossplane | Terraform |
|---|---|---|
| Model | Kubernetes-native (CRDs, reconciliation) | CLI-based (plan/apply, state file) |
| State | Kubernetes etcd (no separate state file) | State file (S3/GCS/Azure Blob) |
| Drift correction | Continuous reconciliation | Manual: must run `terraform plan` |
| Multi-tenancy | Native: namespaced claims | Workspaces (coarser-grained) |
| Developer UX | `kubectl apply` a claim YAML | `terraform apply` |
| Debugging | `kubectl describe`, `kubectl events` | `terraform show`, state inspection |
| Ecosystem | Provider ecosystem, growing fast | Huge ecosystem, mature |
| Best for | Platform teams wanting Kubernetes-native self-service | Teams with existing Terraform expertise |

**Decision rule:** If you're building a self-service IDP where developers should provision resources without knowing Terraform, Crossplane is compelling. If you have existing Terraform modules and expertise, Terraform + Atlantis is lower friction.

---

## 6. Golden Path Anatomy

A golden path is a pre-built, opinionated way to do something that is:
- **Easier** than the alternative (otherwise no one uses it)
- **Safer** than the alternative (security, compliance baked in)
- **Monitored** from day one (observability wired in)
- **Documented** with runbooks and onboarding guides

**What a golden path template should include:**
- Service skeleton (Dockerfile, health endpoints, graceful shutdown)
- Helm chart or Kustomize overlay
- ArgoCD Application / Flux Kustomization
- Prometheus ServiceMonitor (for automatic metrics scraping)
- Pre-wired logging (structured JSON, correlation IDs)
- Secrets integration (External Secrets Operator reference)
- Kyverno/Gatekeeper policy compliance (resource limits, required labels)
- README with local dev setup and deployment instructions

---

## 7. Admission Controllers

### Mutating vs Validating
- **Mutating:** Modifies resources before they are stored (e.g., inject sidecar, add default labels)
- **Validating:** Allows or denies resource creation/update (e.g., enforce resource limits, required annotations)

Both operate via webhooks: the API server calls your webhook before storing the resource.

### OPA Gatekeeper vs Kyverno

| | OPA Gatekeeper | Kyverno |
|---|---|---|
| Policy language | Rego (powerful but has learning curve) | YAML-native (no separate language) |
| Mutation support | Limited | Full (generate, mutate, validate) |
| Audit mode | Yes (reports violations without blocking) | Yes |
| Testing | opa test | kyverno test CLI |
| Best for | Teams with OPA experience, complex logic | Teams wanting simpler YAML-native policies |

**Example Kyverno policy (require resource limits):**
```yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: require-resource-limits
spec:
  validationFailureAction: Enforce
  rules:
    - name: check-container-resources
      match:
        any:
        - resources:
            kinds: [Pod]
      validate:
        message: "CPU and memory limits are required."
        pattern:
          spec:
            containers:
              - resources:
                  limits:
                    memory: "?*"
                    cpu: "?*"
```

---

## 8. Secrets Management Patterns

| Pattern | How it works | Security level | Complexity |
|---|---|---|---|
| Kubernetes Secrets | Base64-encoded in etcd | Low (base64 ≠ encryption unless etcd encryption enabled) | Low |
| Sealed Secrets | Encrypted YAML committed to Git, decrypted by controller | Medium (key stays in cluster) | Low |
| External Secrets Operator | Syncs from AWS Secrets Manager / GCP Secret Manager / Vault | High | Medium |
| Vault Agent Injector | Vault injects secrets as files into pods at runtime | High | High |

**Recommendation:** For most organizations, External Secrets Operator syncing from a managed secrets service (AWS Secrets Manager, GCP Secret Manager) is the right balance of security, operational simplicity, and auditability.

---

## 9. Developer Experience Metrics

### DORA Metrics
| Metric | Elite | High | Medium | Low |
|---|---|---|---|---|
| Deployment frequency | Multiple times/day | Daily-weekly | Weekly-monthly | < Monthly |
| Lead time for changes | < 1 hour | Day-week | Week-month | > Month |
| MTTR (mean time to restore) | < 1 hour | < 1 day | < 1 week | > 1 week |
| Change failure rate | 0-5% | 5-10% | 10-15% | > 15% |

### SPACE Framework (beyond DORA)
- **S**atisfaction and wellbeing
- **P**erformance (business outcomes)
- **A**ctivity (outputs: PRs, deploys, reviews)
- **C**ommunication and collaboration
- **E**fficiency and flow (time in flow, interruptions)

### Platform-specific metrics
- Golden path adoption rate (% services using paved road vs custom)
- Time to first deployment for new services (onboarding speed)
- Self-service provisioning success rate (% of infra requests fulfilled without platform team)
- Platform availability SLO compliance
- Developer NPS (periodic survey)
