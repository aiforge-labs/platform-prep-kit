# SRE Fundamentals

A reference guide for Site Reliability Engineers — SLOs, error budgets, observability, incidents, and reliability patterns.

---

## 1. SLI / SLO / SLA Definitions

| Term | Definition | Who owns it |
|---|---|---|
| **SLI** (Service Level Indicator) | A quantitative measure of service behavior (e.g., request success rate) | Engineering |
| **SLO** (Service Level Objective) | The target value for an SLI over a time window (e.g., 99.9% success rate over 30 days) | Engineering + Product |
| **SLA** (Service Level Agreement) | A contractual commitment to customers, with consequences for breach | Legal + Business |
| **Error Budget** | 1 - SLO = the allowed amount of unreliability | Engineering |

**Typical SLA vs SLO gap:** SLA = 99.5%, SLO = 99.9%. The gap is the safety margin between what you commit to customers and what you target internally.

---

## 2. Choosing Good SLIs

Not all metrics make good SLIs. Good SLIs are:
- **Directly meaningful** to users (not internal queue depth)
- **Measurable** in near-real-time
- **Actionable** — something engineering can affect

| Service Type | Recommended SLIs |
|---|---|
| Request-based (API, web) | Availability (success rate), Latency (p50/p95/p99), Error rate |
| Data pipeline | Freshness (data age), Completeness (records processed/expected), Correctness |
| Storage | Durability (data loss rate), Availability (read/write success rate) |
| ML inference | Prediction latency, Model availability, Prediction quality |

**The four golden signals (Google SRE):** Latency, Traffic, Errors, Saturation

---

## 3. Error Budget Calculations

**Formula:**
```
Error Budget (in time) = (1 - SLO) × window
99.9% SLO over 30 days: (1 - 0.999) × 30 × 24 × 60 = 43.2 minutes
99.9% SLO over 28 days: 40.3 minutes
99.5% SLO over 30 days: 3.6 hours
99.0% SLO over 30 days: 7.2 hours
```

**Burn rate:** How fast you're consuming the error budget relative to the budget rate.
- Burn rate of 1 = consuming budget at exactly the SLO rate (just sustainable)
- Burn rate of 2 = consuming budget twice as fast (will exhaust in half the window)
- Burn rate of 14.4 = will exhaust monthly budget in 5 hours

**Multi-window burn rate alerting:**
Alert when burn rate is high in BOTH a short window (fast detection) and a long window (high confidence):
- Critical: burn rate > 14.4 over 1h AND > 14.4 over 5m (exhausts budget in 1h)
- High: burn rate > 6 over 6h AND > 6 over 30m (exhausts budget in 5 days)
- Medium: burn rate > 3 over 3 days (exhausts budget in 10 days)

---

## 4. Toil Definition & Measurement

**Toil is operational work that is:**
- Manual (requires a human to execute)
- Repetitive (performed regularly, not one-off)
- Automatable (could be done by a machine)
- Tactical (interrupt-driven, not strategic)
- Lacking enduring value (does not permanently improve the system)

**Examples of toil:** Manually restarting a service that crashes periodically, manually scaling a deployment for a known traffic event, manually copying logs to a ticket, manually rotating certificates.

**Examples of NOT toil:** Post-mortems, on-call response to novel incidents, capacity planning discussions, improving monitoring coverage.

**Measuring toil:** Track time spent per category in weekly/monthly retrospectives. Target: <50% of engineering time on toil. If toil > 50%, the team has a reliability or automation debt problem.

---

## 5. Observability: The Three Pillars

### Metrics
- **What:** Numeric measurements aggregated over time
- **Tools:** Prometheus (collection), Grafana (visualization), Alertmanager (alerting)
- **Best for:** Dashboards, alerting, capacity planning, SLO burn rate calculation
- **Limitation:** High cardinality (per-user, per-request) metrics are expensive

### Logs
- **What:** Timestamped event records from applications and infrastructure
- **Tools:** Loki (Grafana stack), ELK (Elasticsearch + Logstash + Kibana), OpenSearch
- **Best for:** Debugging specific incidents, audit trails, request-level detail
- **Best practice:** Structured (JSON) logs with correlation IDs, consistent log levels

### Traces
- **What:** Records of a request's path through distributed services
- **Tools:** Jaeger, Grafana Tempo, Zipkin, OpenTelemetry (vendor-neutral instrumentation)
- **Best for:** Identifying latency bottlenecks across service boundaries, debugging cascading failures
- **Key concept:** Context propagation — the trace ID must flow through every service call

### USE Method (for resources)
| Resource | Utilization | Saturation | Errors |
|---|---|---|---|
| CPU | % busy | run queue length | errors |
| Memory | bytes used | page faults | OOM kills |
| Disk | % busy | I/O wait | disk errors |
| Network | bytes/s | queue depth | packet errors |

### RED Method (for services)
- **Rate:** Requests per second
- **Errors:** Failed requests per second (or % error rate)
- **Duration:** Distribution of request latencies (p50, p95, p99)

---

## 6. Incident Severity Classification

| Severity | Definition | Example | Response Time |
|---|---|---|---|
| P0 (Critical) | Complete service outage or data loss | Checkout service down for all users | Immediate, all hands |
| P1 (High) | Major degradation, significant user impact | 20% of users experiencing payment failures | < 15 minutes |
| P2 (Medium) | Partial degradation, workaround available | Search results slow but available | < 1 hour |
| P3 (Low) | Minor issue, limited user impact | Error message typo in edge case flow | Next business day |
| P4 (Informational) | No user impact, future risk | Disk usage at 70% on non-critical host | Scheduled work |

---

## 7. Blameless Post-Mortem Template

```
## Incident: [Title]
**Date:** YYYY-MM-DD
**Duration:** Xh Ym
**Severity:** P0/P1/P2
**Incident Commander:** [Name]
**Scribe:** [Name]

## Summary
[2-3 sentences: what happened, what was the user impact, how was it resolved]

## Timeline (UTC)
- HH:MM — [Event or action]
- HH:MM — [Event or action]
...

## Root Cause Analysis
[What was the underlying technical cause. Not "human error" — that's never the root cause.]

## Contributing Factors
- [Environmental or process factor that allowed this to happen or made it worse]
- [...]

## What Went Well
- [Things the team did well during response]

## Action Items
| Action | Owner | Due Date | Priority |
|---|---|---|---|
| [Specific, measurable improvement] | [Name] | YYYY-MM-DD | High/Med/Low |

## Lessons Learned
[What would we do differently with hindsight?]
```

**Action item quality checklist:**
- ✓ Specific: not "improve monitoring" but "add alert for X metric when Y threshold is exceeded"
- ✓ Owned: a named individual, not a team
- ✓ Time-bound: a due date, not "eventually"
- ✓ Preventive or detective: prevents recurrence OR detects it faster

---

## 8. Reliability Patterns

### Circuit Breaker
**Problem:** Calling a degraded downstream service wastes resources and amplifies failures.
**States:** Closed (normal) → Open (failing, reject calls immediately) → Half-open (test if service recovered)
**Implementation:** Resilience4j (Java), Polly (.NET), Hystrix (legacy Java), service mesh (Istio circuit breaking)

### Bulkhead
**Problem:** One slow or failing service consumes all thread pool resources, taking down unrelated services.
**Solution:** Isolate resource pools (thread pools, connection pools) per downstream dependency.
**Analogy:** Ship bulkheads prevent flooding in one compartment from sinking the whole ship.

### Retry with Exponential Backoff + Jitter
```
base_delay = 100ms
max_delay = 30s
retry_delay = min(base_delay * 2^attempt, max_delay)
actual_delay = retry_delay + random(0, retry_delay * 0.1)  # jitter
```
**Jitter** prevents the "thundering herd" problem where all clients retry at the same time.

### Timeout Hierarchy
Set timeouts at every network boundary. Rule of thumb: each tier's timeout < the tier above it.
```
User browser timeout: 30s
Load balancer timeout: 25s
Service A → Service B timeout: 10s
Service B → Database timeout: 5s
```

### Graceful Degradation
Design the system to serve degraded but functional responses when dependencies fail:
- Return cached data when the live data source is unavailable
- Show a simplified UI when a personalization service is down
- Accept writes to a queue when the primary store is degraded

---

## 9. Chaos Engineering Principles

1. **Define steady state** — measurable normal behavior (SLO metrics, key business metrics)
2. **Hypothesize** — "We believe the system will remain in steady state when X fails"
3. **Vary real-world events** — inject failures: instance termination, network latency, disk full, dependency failure
4. **Minimize blast radius** — start small (1 instance, low traffic %, non-prod) and expand gradually
5. **Automate experiments to run continuously** — don't just do game days; automate low-risk experiments

**Game day checklist:**
- [ ] Written hypothesis with measurable success criteria
- [ ] Rollback procedure documented before starting
- [ ] Stakeholders informed (support, on-call team)
- [ ] Blast radius controls in place (kill switch, traffic %)
- [ ] Monitoring active and dashboards ready
- [ ] Post-game-day debrief scheduled
