# Policy-as-Code

A reference guide for cloud compliance engineers — OPA/Rego, CIS benchmarks, CSPM tools, and compliance framework mapping.

---

## 1. OPA / Rego Primer

### OPA architecture
- **OPA (Open Policy Agent):** A general-purpose policy engine that evaluates Rego policies against structured data (JSON/YAML)
- **Rego:** The policy language — logic-based, declarative
- **Input:** The document being evaluated (e.g., a Terraform plan, Kubernetes resource, API request)
- **Data:** Background reference data (e.g., allowed image registries, approved regions)

### Rego fundamentals
```rego
package main

# Allow rule — if this evaluates to true, the input is allowed
allow {
    input.user == "admin"
}

# Deny rule — if any deny rule evaluates to a message, the input is denied
deny[msg] {
    input.method == "DELETE"
    not input.user == "admin"
    msg := sprintf("User %v cannot delete resources", [input.user])
}

# Comprehension — build a set from matching elements
high_severity_findings := {finding.id |
    finding := input.findings[_]
    finding.severity == "HIGH"
}
```

### Conftest usage (policy testing against config files)
```bash
# Test Terraform plan
conftest test plan.json --policy policies/

# Test Kubernetes manifests
conftest test deployment.yaml --policy policies/kubernetes/

# Test multiple files with specific namespace
conftest test *.tf --namespace main
```

---

## 2. CIS Benchmark Structure

### Profile levels
| Level | Description | Suitable for |
|---|---|---|
| L1 | Minimum baseline — essential security, no performance impact | All environments |
| L2 | Defense-in-depth — higher security, may impact functionality | Sensitive/regulated environments |

### CIS AWS Foundations Benchmark key control areas

| Section | Control examples |
|---|---|
| IAM | MFA for root account, no root access keys, password policy, access key rotation |
| Logging | CloudTrail enabled in all regions, S3 bucket access logging, VPC flow logs |
| Monitoring | CloudWatch alarms for root activity, unauthorized API calls, IAM changes |
| Networking | No security groups with 0.0.0.0/0 on port 22/3389, VPC default security group blocks all |
| Storage | S3 buckets not publicly accessible, S3 encryption enabled |

### Automated CIS assessment
```bash
# Prowler — most comprehensive AWS CIS tool
prowler -g cislevel1  # Level 1 checks only
prowler -g cislevel2  # Level 2 checks
prowler -g pci        # PCI-DSS
prowler -c check_id   # Specific check

# Output options
prowler -M json -o results/
prowler -M csv -o results/
```

---

## 3. Compliance Framework Comparison

| Framework | Primary audience | Scope | Assessment type |
|---|---|---|---|
| CIS Benchmarks | Technical teams | Configuration hardening | Technical |
| SOC 2 Type II | SaaS/cloud vendors | Security controls | Audit-based |
| ISO 27001 | Enterprise, global | ISMS (information security management) | Certification |
| PCI-DSS | Payment processors | Cardholder data security | Assessment/QSA |
| HIPAA | US healthcare | PHI protection | Self-attestation + OCR |
| FedRAMP | US federal suppliers | Cloud security | Third-party assessment |
| NIST CSF | US critical infrastructure | Risk management | Self-assessment |

### Framework cross-mapping (selected)

| Control Area | SOC 2 CC | ISO 27001 Annex A | NIST CSF | CIS Section |
|---|---|---|---|---|
| Access control | CC6.1, CC6.2 | A.9 | PR.AC | IAM (Section 1) |
| Encryption | CC6.7 | A.10 | PR.DS | Storage, Networking |
| Logging/monitoring | CC7.2 | A.12.4 | DE.AE | Logging (Section 3) |
| Incident response | CC7.3, CC7.4 | A.16 | RS.RP | — |
| Change management | CC8.1 | A.12.1 | PR.IP | — |

Cross-mapping reduces audit duplication: pass CIS checks → provides evidence for SOC 2 CC6 and ISO 27001 A.9.

---

## 4. CSPM Tool Landscape

### Native cloud CSPM

| Tool | Cloud | Key capabilities |
|---|---|---|
| AWS Security Hub | AWS | Aggregates findings from GuardDuty, Inspector, Macie, Config. CIS Benchmark standard built-in |
| AWS Config | AWS | Continuous configuration recording, managed rules, conformance packs |
| Microsoft Defender for Cloud | Azure | Secure score, recommendations, CIS benchmark, regulatory compliance dashboard |
| GCP Security Command Center | GCP | Asset inventory, vulnerability findings, misconfigurations, threat detection |

### Open-source CSPM
| Tool | Coverage | Strengths |
|---|---|---|
| Prowler | AWS (primary), Azure, GCP | Most comprehensive AWS CIS checks, great for CLI/CI use |
| ScoutSuite | AWS, Azure, GCP, others | Multi-cloud, HTML report output, broad coverage |
| CloudSploit (Aqua) | Multi-cloud | API-based, CI-friendly |

### CSPM vs CWPP
| | CSPM | CWPP |
|---|---|---|
| Focus | Infrastructure misconfigurations | Workload runtime security |
| What it scans | IAM, S3, security groups, network config | Container images, runtime processes, memory |
| When it triggers | Configuration change or scheduled | Continuously at runtime |
| Example | S3 bucket is publicly accessible | Container process spawned a shell |

---

## 5. AWS Config Conformance Packs

Conformance packs group related Config rules for a compliance framework. AWS provides managed conformance packs for:
- `Operational-Best-Practices-for-CIS-AWS-v1.4-Level1`
- `Operational-Best-Practices-for-PCI-DSS`
- `Operational-Best-Practices-for-HIPAA-Security`
- `Operational-Best-Practices-for-NIST-CSF`

Deploy via CloudFormation or Terraform:
```hcl
resource "aws_config_conformance_pack" "cis_l1" {
  name          = "cis-aws-foundations-level1"
  template_body = file("conformance-packs/cis-l1.yaml")
}
```

Custom rules use AWS Lambda:
```python
def evaluate_compliance(configuration_item, rule_parameters):
    if configuration_item["resourceType"] != "AWS::S3::Bucket":
        return "NOT_APPLICABLE"

    config = configuration_item["configuration"]
    if config.get("PublicAccessBlockConfiguration", {}).get("BlockPublicAcls"):
        return "COMPLIANT"
    return "NON_COMPLIANT"
```

---

## 6. SOC 2 Controls in Cloud Environments

### Automating SOC 2 evidence collection

| Control category | Evidence source | Automation approach |
|---|---|---|
| Access control (CC6) | IAM users, roles, policies | AWS IAM Access Analyzer, scheduled export |
| Encryption (CC6.7) | S3 encryption config, RDS encryption | AWS Config rule: `s3-bucket-server-side-encryption-enabled` |
| Monitoring (CC7.2) | CloudTrail logs, CloudWatch alarms | CloudTrail org trail → S3 → quarterly export |
| Change management (CC8.1) | Deploy logs, infrastructure PRs | GitHub Actions logs, Terraform Cloud run history |
| Availability (A1) | SLO metrics, incident reports | Prometheus/Grafana exports, PagerDuty reports |

### Continuous vs point-in-time compliance
- **Point-in-time:** Manual evidence pull at audit time. Labor-intensive, gaps possible.
- **Continuous compliance:** AWS Config + Security Hub continuously assesses. Evidence is always available. Audit prep = export the report.

Target: **continuous compliance** where the compliance dashboard is the audit artifact.

---

## 7. Multi-Account Governance Patterns

### AWS Control Tower guardrails

| Type | How it works | Example |
|---|---|---|
| Preventive | SCP that blocks the action | "Disallow creation of unencrypted S3 buckets" |
| Detective | AWS Config rule that alerts | "Detect if MFA is not enabled for root accounts" |
| Proactive | CloudFormation hooks that validate before deploy | "Block IAM policies with * resources" |

### Account factory automation
```
New account request → Account Factory → CloudFormation StackSet →
  - GuardDuty enrollment
  - Security Hub enrollment
  - CloudTrail org trail attachment
  - Default VPC deletion
  - Baseline Config rules deployment
```

### Security Hub aggregation
Enable Security Hub in a dedicated security account as the delegated administrator. All member accounts' findings aggregate automatically. Build a single compliance dashboard covering the entire organization from one pane of glass.
