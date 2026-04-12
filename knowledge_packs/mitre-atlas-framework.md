# MITRE ATLAS (Adversarial Threat Landscape for Artificial-Intelligence Systems)

## Overview

MITRE ATLAS is a knowledge base of adversarial tactics, techniques, and case studies for machine learning systems. Modeled after the widely adopted MITRE ATT&CK framework for cybersecurity, ATLAS provides a structured vocabulary and reference for understanding how adversaries target AI/ML systems specifically.

**Key distinction from ATT&CK:** While ATT&CK focuses on attacks against traditional IT infrastructure (networks, endpoints, identities), ATLAS focuses on attacks against the AI/ML components themselves — the models, training data, inference pipelines, and AI-specific infrastructure.

**Why ATLAS matters:** As organizations deploy more AI/ML systems, the attack surface expands beyond traditional IT. Security teams need a framework to systematically identify, communicate, and defend against AI-specific threats. ATLAS provides that common language.

**Current version:** ATLAS is actively maintained and updated. Check [atlas.mitre.org](https://atlas.mitre.org/) for the latest.

---

## ATLAS vs. ATT&CK Comparison

| Aspect | ATT&CK | ATLAS |
|--------|--------|-------|
| **Target** | IT systems (networks, endpoints, cloud) | AI/ML systems (models, data, pipelines) |
| **Maturity** | Established (2013+), widely adopted | Newer (2021+), growing adoption |
| **Tactics** | 14 tactics (Reconnaissance through Impact) | 14 tactics (mirroring ATT&CK structure) |
| **Techniques** | 200+ techniques | 40+ techniques (growing) |
| **Case studies** | Extensive real-world examples | Growing collection, many academic |
| **Navigator tool** | ATT&CK Navigator | ATLAS Navigator |
| **Use in threat modeling** | Standard practice | Emerging practice |

**They complement each other.** A real attack against an AI system will likely use both ATT&CK techniques (gaining initial access to infrastructure) and ATLAS techniques (manipulating the ML model). Comprehensive threat modeling should reference both.

---

## ATLAS Tactics

ATLAS tactics represent the adversary's objective at each stage of an attack. They follow a similar progression to ATT&CK but include AI-specific objectives.

### 1. Reconnaissance (AML.TA0001)
Gathering information about the target AI system: what model is used, what training data was used, what API is exposed, what framework (TensorFlow, PyTorch) is in use, and what the model's intended purpose is.

**AI-specific elements:** Discovering model architecture through published papers, identifying training datasets through data provenance disclosures, and profiling model behavior through systematic queries.

### 2. Resource Development (AML.TA0002)
Acquiring or creating resources for the attack: adversarial toolkits (Adversarial Robustness Toolbox, CleverHans), shadow models for transferability attacks, poisoned datasets, and computational resources for attack generation.

### 3. Initial Access (AML.TA0003)
Gaining the ability to interact with the target AI system. This could be through a public API, a model marketplace, physical access to sensors (cameras, microphones), or compromised credentials to an ML platform.

### 4. ML Model Access (AML.TA0004)
Obtaining some level of access to the ML model itself. This ranges from **black-box access** (can only send inputs and observe outputs) to **white-box access** (has the model weights, architecture, and training data).

### 5. Execution (AML.TA0005)
Running adversarial techniques against the AI system. This includes crafting adversarial examples, executing model inference, running model extraction queries, and triggering backdoors.

### 6. Persistence (AML.TA0006)
Maintaining access to or influence over the AI system across model updates, retraining cycles, and infrastructure changes. This includes embedding backdoors in training data that survive retraining.

### 7. Privilege Escalation (AML.TA0007)
Gaining higher-level access to the AI system or its supporting infrastructure. Moving from black-box API access to white-box model access, or from model inference to model training pipelines.

### 8. Defense Evasion (AML.TA0008)
Avoiding detection by AI security monitoring, adversarial detection systems, and human reviewers. This includes crafting adversarial examples that are imperceptible to humans, using transferability to avoid triggering the target model's specific defenses, and mimicking benign usage patterns.

### 9. Discovery (AML.TA0009)
Learning more about the AI system after gaining access: mapping model boundaries, identifying connected systems, discovering training infrastructure, and enumerating available model endpoints.

### 10. Collection (AML.TA0010)
Gathering data from the AI system: extracting training data, collecting model predictions for extraction attacks, harvesting PII from model outputs, and intercepting data in the ML pipeline.

### 11. ML Attack Staging (AML.TA0011)
Preparing the conditions for the primary attack: building proxy models, generating adversarial perturbations, preparing poisoned data batches, and testing attacks against shadow models before deployment against the target.

### 12. Exfiltration (AML.TA0012)
Extracting valuable assets from the AI system: model weights, training data, proprietary algorithms, and confidential information embedded in model responses.

### 13. Impact (AML.TA0013)
Achieving the adversary's ultimate objective: causing the model to produce incorrect outputs, degrading model performance, destroying training data, manipulating business decisions, or causing financial/reputational damage.

### 14. Command and Control (AML.TA0014)
Maintaining covert communication channels with compromised AI components: backdoors that respond to specific trigger patterns, compromised model endpoints that exfiltrate data, and persistent access to ML infrastructure.

---

## Key Techniques (Top 20)

### AML.T0000 — ML Model Inference API Access
**Tactic:** Initial Access
**Description:** Adversary accesses the ML model through a legitimate inference API. Many ML models are exposed through APIs that accept inputs and return predictions, classifications, or generated content.
**Example:** Querying a sentiment analysis API to understand its behavior and identify potential evasion patterns.

### AML.T0001 — Adversarial Perturbation (Evasion Attack)
**Tactic:** Execution, Defense Evasion
**Description:** Crafting small, often imperceptible modifications to inputs that cause the model to produce incorrect outputs. This exploits the model's sensitivity to specific input features.
**Example:** Adding carefully computed noise to an image so a classifier misidentifies a stop sign as a speed limit sign.

### AML.T0002 — Backdoor ML Model
**Tactic:** Persistence
**Description:** Inserting a hidden trigger into the model during training so that the model produces attacker-chosen outputs when the trigger is present in the input, but behaves normally otherwise.
**Example:** A model fine-tuned to always classify loan applications as approved when the application contains a specific rare phrase in the comments field.

### AML.T0003 — Data Poisoning
**Tactic:** Persistence, Impact
**Description:** Corrupting the training data to manipulate model behavior. Can be targeted (affect specific inputs) or indiscriminate (degrade overall performance).
**Example:** Injecting mislabeled images into a training dataset so the model learns incorrect associations for a specific class.

### AML.T0004 — ML Supply Chain Compromise
**Tactic:** Initial Access, Persistence
**Description:** Compromising components in the ML supply chain: pre-trained models, training datasets, ML libraries, or model serving infrastructure.
**Example:** Uploading a trojanized pre-trained model to a public model hub, named similarly to a popular model.

### AML.T0005 — Model Extraction (Model Stealing)
**Tactic:** Exfiltration
**Description:** Creating a functionally equivalent copy of a model by systematically querying it and using the input-output pairs to train a replica. Enables offline analysis and further attacks.
**Example:** Sending thousands of carefully chosen queries to a proprietary classification API, recording the responses, and training a local model that replicates the API's behavior.

### AML.T0006 — Training Data Extraction (Membership Inference)
**Tactic:** Collection, Exfiltration
**Description:** Determining whether a specific data point was used in the model's training data. Can be extended to extract actual training examples from the model.
**Example:** Querying a language model with specific phrases to determine if it memorized those phrases from training data, potentially revealing proprietary or personal information.

### AML.T0007 — Model Inversion
**Tactic:** Collection
**Description:** Inferring sensitive features of training data by observing model outputs. Given a model trained on faces, model inversion can reconstruct approximate images of individuals in the training set.
**Example:** Using a facial recognition model's confidence scores to iteratively reconstruct facial images of enrolled individuals.

### AML.T0008 — Prompt Injection
**Tactic:** Execution, Defense Evasion
**Description:** Manipulating an LLM by embedding instructions in the input that override or extend the system's intended behavior. Specific to language models.
**Example:** Embedding hidden instructions in a document that an LLM-powered assistant will process, causing it to perform unauthorized actions.

### AML.T0009 — Transfer Learning Attack
**Tactic:** ML Attack Staging
**Description:** Adversarial examples created against one model (a proxy) often work against a different model (the target), even when the models have different architectures. This enables black-box attacks using white-box techniques.
**Example:** Training a local copy of a model, generating adversarial examples against it, and deploying those examples against the actual target system.

### AML.T0010 — Functional Extraction
**Tactic:** Exfiltration
**Description:** Extracting the functionality of a model without necessarily replicating its exact architecture. The goal is a model that produces the same outputs for the inputs of interest.
**Example:** Using active learning techniques to efficiently query a target model and build a distilled version that matches its behavior on the relevant input distribution.

### AML.T0011 — Exploit Public-Facing ML Application
**Tactic:** Initial Access
**Description:** Identifying and exploiting vulnerabilities in ML applications exposed to the internet, including insecure API endpoints, default credentials on ML platforms, and exposed model serving infrastructure.
**Example:** Discovering an unprotected Jupyter notebook server exposed to the internet with access to model training code and data.

### AML.T0012 — Input Manipulation (Physical Domain)
**Tactic:** Execution
**Description:** Manipulating physical-world inputs to deceive ML models: adversarial patches on objects, specialized clothing to evade person detection, or acoustic signals to manipulate voice recognition.
**Example:** Wearing a specially printed T-shirt that causes a surveillance camera's person-detection model to fail to identify the wearer.

### AML.T0013 — Discover ML Model Ontology
**Tactic:** Reconnaissance, Discovery
**Description:** Mapping the structure and capabilities of a target ML system: input/output formats, model type, classes/categories, confidence thresholds, and rate limits.
**Example:** Sending diverse probe inputs to a classification API and analyzing the response format, error messages, and class labels to understand the model's scope.

### AML.T0014 — Denial of ML Service
**Tactic:** Impact
**Description:** Causing an ML service to become unavailable or degrade to unusable quality. Includes resource exhaustion, input-triggered crashes, and systematic accuracy degradation.
**Example:** Sending inputs that trigger maximum computational cost, exhausting GPU resources and causing timeouts for legitimate users.

### AML.T0015 — Evade ML Model
**Tactic:** Defense Evasion
**Description:** Modifying malicious content so that an ML-based detection system fails to flag it. This is the adversarial ML version of antivirus evasion.
**Example:** Modifying malware binaries so they evade an ML-based malware classifier while retaining their malicious functionality.

### AML.T0016 — Obtain Capabilities
**Tactic:** Resource Development
**Description:** Acquiring tools, datasets, computational resources, or expertise needed for ML attacks. This includes both custom development and use of publicly available adversarial ML toolkits.
**Example:** Setting up an Adversarial Robustness Toolbox environment and pre-training proxy models for a transfer attack.

### AML.T0017 — Develop Proxy Model (Shadow Model)
**Tactic:** ML Attack Staging
**Description:** Training a local model that approximates the target model's behavior. Used as a stand-in for developing and testing attacks before deploying them against the actual target.
**Example:** Using the target model's API to label a dataset, then training a local model on that dataset to create an approximate copy for white-box attack development.

### AML.T0018 — Craft Adversarial Data
**Tactic:** ML Attack Staging
**Description:** Generating adversarial inputs tailored to the target model. Includes gradient-based methods (FGSM, PGD, C&W), optimization-based methods, and generative approaches.
**Example:** Using Projected Gradient Descent (PGD) to generate images that are imperceptibly different from originals but cause misclassification.

### AML.T0019 — Insert Backdoor Trigger
**Tactic:** Persistence
**Description:** Embedding a specific pattern (trigger) into training data or model weights so the model produces a predetermined output when the trigger is detected in an input.
**Example:** Adding a small, specific watermark pattern to a subset of training images and relabeling them, so the trained model misclassifies any image containing that watermark.

---

## Case Studies (Generic)

### Case Study 1: Chatbot Manipulation via Indirect Prompt Injection
**Scenario:** An organization deployed a customer service chatbot backed by an LLM with access to a knowledge base. An attacker embedded adversarial instructions in a publicly editable wiki page that was part of the knowledge base. When users asked questions that triggered retrieval of the poisoned page, the chatbot followed the injected instructions instead of its system prompt.

**ATLAS mapping:** Reconnaissance (T0013) to understand the chatbot's knowledge sources, Persistence (T0002) by embedding the payload in training/retrieval data, Execution (T0008 - Prompt Injection) when the payload was triggered.

**Lessons:** Knowledge bases should be treated as untrusted input. Content retrieved for RAG should be sanitized before inclusion in prompts.

### Case Study 2: Adversarial Evasion of Malware Detection
**Scenario:** A security vendor deployed an ML-based malware classifier. Attackers studied the model by submitting thousands of samples through the vendor's public scanning API. Using transfer learning attacks, they modified their malware to evade detection while preserving functionality. Detection rates for the modified malware dropped from 95% to below 10%.

**ATLAS mapping:** Reconnaissance (T0013) to profile the model, ML Attack Staging (T0017 - proxy model, T0018 - craft adversarial data), Execution (T0001 - adversarial perturbation), Defense Evasion (T0015).

**Lessons:** ML-based detection should be layered with rule-based detection. Rate limiting and anomaly detection on the scanning API could have identified the reconnaissance phase.

### Case Study 3: Training Data Extraction from Language Model
**Scenario:** Researchers demonstrated that a large language model would reproduce verbatim passages from its training data when prompted with the correct prefix. By systematically probing the model, they extracted email addresses, phone numbers, and code snippets that had appeared in the training corpus.

**ATLAS mapping:** ML Model Inference API Access (T0000), Training Data Extraction (T0006), Collection (T0010).

**Lessons:** Models should be tested for memorization of training data. Differential privacy during training, output filtering, and deduplication of training data are important mitigations.

### Case Study 4: Supply Chain Attack via Model Repository
**Scenario:** An attacker uploaded a pre-trained model to a public model hub using a name nearly identical to a popular model (typosquatting). The model file contained a serialized Python payload that executed when loaded. Several developers downloaded and loaded the model, unknowingly executing the payload.

**ATLAS mapping:** Resource Development (T0016), ML Supply Chain Compromise (T0004), Initial Access (T0011).

**Lessons:** Use safe serialization formats (SafeTensors), verify model checksums and signatures, and only download models from verified authors on model hubs.

---

## How to Use ATLAS for Threat Modeling

### Step-by-Step Process

**1. Define the AI System Scope**
- What ML models are used?
- What are the inputs and outputs?
- What data sources feed the model?
- What actions can the model trigger?
- Who interacts with the system (users, admins, other systems)?

**2. Identify Relevant ATLAS Tactics**
Walk through each ATLAS tactic and assess whether it applies to your system:
- Does the system have a public API? (Initial Access, ML Model Access)
- Does the system process external data? (Data Poisoning, Prompt Injection)
- Is the model's architecture publicly known? (Reconnaissance)
- Does the system make consequential decisions? (Impact)

**3. Map Techniques to Components**
For each relevant tactic, identify specific techniques that could be applied to your system components. Use the ATLAS Navigator to visualize your threat landscape.

**4. Assess and Prioritize Risks**
For each applicable technique:
- How likely is this attack? (Consider attacker motivation and capability)
- What is the impact if it succeeds?
- What existing controls mitigate this risk?
- What residual risk remains?

**5. Define Mitigations**
For each prioritized risk, define specific mitigations:
- **Preventive controls:** Input validation, access controls, secure model loading
- **Detective controls:** Anomaly detection on queries, model monitoring, audit logging
- **Responsive controls:** Incident response procedures, model rollback capability, circuit breakers

**6. Document and Review**
Create a threat model document that maps:
- System components to ATLAS techniques
- Techniques to mitigations
- Residual risks to acceptance decisions

Review the threat model whenever the system changes, new ATLAS techniques are published, or after a security incident.

### Template: Threat Model Mapping Table

| Component | ATLAS Technique | Likelihood | Impact | Current Controls | Residual Risk | Additional Mitigation |
|-----------|----------------|-----------|--------|-----------------|---------------|----------------------|
| Public API | T0000 (API Access) | High | Medium | Rate limiting | Medium | Add anomaly detection |
| RAG retrieval | T0008 (Prompt Injection) | High | High | None | High | Input sanitization, output validation |
| Training pipeline | T0003 (Data Poisoning) | Low | Critical | Manual review | Medium | Automated data validation |

---

## Self-Test Questions

1. **Explain the relationship between MITRE ATLAS and MITRE ATT&CK. Why would a security team need both?** Provide a scenario where an attack chain uses techniques from both frameworks.

2. **You are threat modeling a computer vision system that inspects products on a manufacturing line. Which ATLAS techniques are most relevant, and why?** Consider both digital and physical attack vectors.

3. **Describe the difference between model extraction (T0005) and functional extraction (T0010). In what scenarios would an attacker prefer one over the other?**

4. **A company's spam filter uses an ML model. Describe how an attacker could use the adversarial perturbation technique (T0001) combined with transfer learning (T0009) to bypass it, even without direct access to the model weights.**

5. **Walk through how you would use ATLAS to create a threat model for an LLM-powered code review assistant that has access to a company's private code repositories.** Identify the top 5 risks and propose mitigations for each.

---

## Resources

- [MITRE ATLAS Official Site](https://atlas.mitre.org/)
- [ATLAS Navigator](https://atlas.mitre.org/navigator)
- [ATLAS Case Studies](https://atlas.mitre.org/studies)
- [MITRE ATT&CK (for comparison)](https://attack.mitre.org/)
- [Adversarial Robustness Toolbox (IBM)](https://adversarial-robustness-toolbox.readthedocs.io/)
- [CleverHans Library](https://github.com/cleverhans-lab/cleverhans)
- [NIST AI 100-2e2023 — Adversarial Machine Learning Taxonomy](https://csrc.nist.gov/pubs/ai/100/2/e2023/final)
