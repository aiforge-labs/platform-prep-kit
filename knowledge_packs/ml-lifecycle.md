# ML Lifecycle

A reference guide covering the end-to-end production ML lifecycle — from feature engineering to monitoring and retraining.

---

## 1. Production ML vs Research ML

| Dimension | Research ML | Production ML |
|---|---|---|
| Goal | Find the best model | Build a reliable system |
| Data | Fixed dataset | Continuously arriving data |
| Success metric | Accuracy on test set | Business metric + reliability |
| Iteration | Experiment freely | Controlled, tested changes |
| Failure mode | Wrong predictions | Silent degradation, system outage |
| Code quality | Notebooks acceptable | Production software standards |

**Key insight:** "It's mostly a software engineering problem." — after the initial model, most work is data pipelines, serving infrastructure, and monitoring.

---

## 2. ML Project Lifecycle Stages

```
Problem Framing
      ↓
Data Collection & Validation
      ↓
Feature Engineering
      ↓
Model Training & Experiment Tracking
      ↓
Offline Evaluation
      ↓
Model Registry (staging)
      ↓
Deployment (shadow → canary → production)
      ↓
Online Monitoring
      ↓
Retraining (triggered or scheduled)
```

---

## 3. Feature Store Architecture

### Why feature stores exist
1. **Consistency (train-serve skew prevention):** Same feature logic used in training and serving
2. **Sharing:** Feature engineering work is reusable across teams and models
3. **Point-in-time correctness:** Training data reflects what was known at prediction time (no data leakage from the future)
4. **Online serving:** Pre-computed features served at low latency for real-time predictions

### Components
```
┌────────────────────────────────────────────────┐
│                Feature Store                    │
│                                                 │
│  ┌──────────────┐    ┌──────────────────────┐  │
│  │ Offline Store│    │   Online Store        │  │
│  │ (S3/BigQuery)│    │ (Redis/DynamoDB)      │  │
│  │ for training │    │ for <10ms serving     │  │
│  └──────────────┘    └──────────────────────┘  │
│                                                 │
│  ┌──────────────────────────────────────────┐  │
│  │           Feature Registry               │  │
│  │  (metadata, owners, lineage, versions)   │  │
│  └──────────────────────────────────────────┘  │
│                                                 │
│  ┌──────────────────────────────────────────┐  │
│  │         Feature Pipelines                │  │
│  │  (batch: Spark/dbt, stream: Flink/Kafka) │  │
│  └──────────────────────────────────────────┘  │
└────────────────────────────────────────────────┘
```

### Train-serve skew
Train-serve skew = feature values at training time ≠ feature values at serving time.

**Common causes:**
- Training uses a Pandas transformation; serving uses a different implementation
- Training uses historical averages calculated over the full dataset; serving uses only recent data
- Feature pipeline has a bug that affects serving but not the static training snapshot

**Prevention:** Use the same feature computation code for training and serving (feature store enforces this).

---

## 4. Experiment Tracking Reference

### What to always log per run
```python
# MLflow example
with mlflow.start_run():
    # Hyperparameters
    mlflow.log_param("learning_rate", 0.001)
    mlflow.log_param("max_depth", 6)

    # Metrics
    mlflow.log_metric("train_auc", train_auc)
    mlflow.log_metric("val_auc", val_auc)

    # Artifacts
    mlflow.log_artifact("feature_importance.png")
    mlflow.sklearn.log_model(model, "model")

    # Environment
    mlflow.log_param("python_version", sys.version)
    mlflow.log_param("dataset_version", "v2.3.1")
```

### MLflow vs Weights & Biases

| | MLflow | Weights & Biases |
|---|---|---|
| Self-hostable | Yes (free OSS) | No (SaaS only) |
| Hyperparameter sweep | MLflow Projects + custom | W&B Sweeps (first-class) |
| Collaboration | Basic | Strong (comments, reports) |
| Model registry | Yes | Yes |
| Best for | Self-hosted, OSS, Databricks | Team collaboration, research |

---

## 5. Model Deployment Patterns

### Deployment strategy comparison

| Strategy | How it works | Risk | When to use |
|---|---|---|---|
| Blue-green | Two identical environments, switch traffic | Low (instant rollback) | Major model updates |
| Canary | Route small % of traffic to new model | Low | Version upgrades |
| Shadow (dark launch) | New model runs alongside, results discarded | Zero (no production impact) | Validate before exposing |
| A/B test | Split users between models, measure business metric | Medium | Comparing model variants |
| Multi-armed bandit | Dynamically route more traffic to better-performing model | Medium | Online optimization |

### Shadow mode implementation
```
Request → Production Model → Response to user
        ↘ Shadow Model → Results logged (not returned)

Compare shadow vs production results to validate
new model before promoting.
```

### Canary deployment math
If new model has a 2% failure rate vs old model's 0.5%:
- 5% canary = 0.05 × 2% + 0.95 × 0.5% = 0.575% overall failure rate
- Acceptable if overall SLO target is met
- Monitor for 24-48h before expanding

---

## 6. ML Monitoring Taxonomy

### Types of drift
| Type | What changes | Detection method |
|---|---|---|
| Data drift (covariate shift) | Input feature distribution | KS test, PSI, JSD |
| Concept drift | P(Y\|X) changes — same features, different correct output | Model performance metrics |
| Label drift | Output distribution changes | Output distribution monitoring |
| Prediction drift | Model output distribution changes | Monitor output histograms |

### Statistical tests for drift detection
| Test | Use case | Key property |
|---|---|---|
| KS test (Kolmogorov-Smirnov) | Continuous features | Non-parametric, distribution-free |
| PSI (Population Stability Index) | Categorical or binned continuous | PSI > 0.2 = significant shift |
| Jensen-Shannon Divergence | Any distribution | Bounded 0-1, symmetric |
| Chi-squared test | Categorical features | Based on expected vs observed counts |

### PSI interpretation
| PSI Value | Meaning |
|---|---|
| < 0.1 | No significant shift |
| 0.1 - 0.2 | Moderate shift, investigate |
| > 0.2 | Significant shift, retrain or investigate |

### Monitoring stack: Evidently AI
```python
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset

report = Report(metrics=[DataDriftPreset()])
report.run(reference_data=training_df, current_data=production_df)
report.save_html("drift_report.html")
```

---

## 7. Retraining Triggers

| Trigger type | How it works | Pros | Cons |
|---|---|---|---|
| Schedule-based | Retrain weekly/monthly | Simple, predictable | May retrain when not needed |
| Data volume-based | Retrain when N new samples arrive | Tied to data growth | Doesn't detect quality issues |
| Drift-triggered | Retrain when drift exceeds threshold | Efficient | Drift threshold tuning required |
| Performance-triggered | Retrain when business metric degrades | Directly tied to outcome | Requires label feedback loop |

**Champion-challenger pattern:**
1. Train new model (challenger) without deploying
2. Shadow mode: run challenger alongside champion
3. Compare challenger vs champion metrics over evaluation window
4. If challenger wins → promote to champion, retire old champion
5. If challenger loses → discard, investigate why

---

## 8. MLOps Maturity Levels

| Level | Description | Characteristics |
|---|---|---|
| 0 | Manual process | Notebooks, manual deploy, no tracking |
| 1 | ML pipeline automation | Automated training pipeline, model registry |
| 2 | CI/CD for ML | Automated retraining, model testing, monitored serving |

Most organizations aim for Level 1. Level 2 requires significant platform investment but provides real reliability for business-critical models.
