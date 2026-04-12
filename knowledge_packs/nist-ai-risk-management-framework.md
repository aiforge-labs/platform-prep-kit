# NIST AI Risk Management Framework (AI RMF 1.0)

## Overview

The NIST Artificial Intelligence Risk Management Framework (AI RMF 1.0), published in January 2023, provides a voluntary framework for managing risks throughout the AI system lifecycle. Unlike prescriptive regulatory requirements, the AI RMF is designed to be flexible, adaptable to any sector, and usable by organizations of all sizes.

The framework was developed through an open, consensus-driven process involving hundreds of stakeholders from industry, academia, civil society, and government. It complements existing risk management standards (NIST Cybersecurity Framework, NIST RMF for information systems) and is intended to be used alongside, not as a replacement for, sector-specific guidance.

**Key documents:**
- **AI RMF 1.0** (NIST AI 100-1): The core framework
- **AI RMF Playbook**: Suggested actions for each function/category
- **AI RMF Crosswalk**: Mapping to other frameworks (ISO 42001, EU AI Act, etc.)
- **NIST AI 600-1**: Generative AI Profile (companion document for GenAI-specific risks)

**Central premise:** AI risk management should be integrated into broader organizational risk management, not treated as a separate silo.

---

## The Four Core Functions

The AI RMF organizes AI risk management into four functions: **GOVERN**, **MAP**, **MEASURE**, and **MANAGE**. These are not sequential steps but concurrent, iterative activities. GOVERN is foundational and informs the other three functions.

### 1. GOVERN

**Purpose:** Establish and maintain the organizational structures, policies, and processes for AI risk management.

GOVERN is the only function that applies across the entire organization rather than to individual AI systems. It sets the foundation for how the other three functions operate.

#### Categories

**GV-1: Policies and procedures are in place to map, measure, and manage AI risks.**
- Documented AI governance policies
- Clear roles and responsibilities for AI risk management
- Integration with existing enterprise risk management (ERM)
- Regular policy review and updates

**GV-2: Accountability structures are in place.**
- Designated AI risk management leadership
- Cross-functional oversight (legal, compliance, engineering, ethics)
- Escalation paths for high-risk findings
- Board or senior executive visibility into AI risks

**GV-3: Workforce diversity, equity, inclusion, and accessibility (DEIA) considerations are built into AI risk management.**
- Diverse teams involved in AI development and oversight
- Consideration of impacts on underrepresented communities
- Accessibility requirements for AI systems

**GV-4: Organizational teams are committed to a culture of responsible AI.**
- Training programs on AI risks and responsible practices
- Incentive structures that reward responsible AI development
- Mechanisms for reporting concerns without retaliation
- Regular communication about AI risk expectations

**GV-5: Processes are in place for robust stakeholder engagement.**
- Input from affected communities and end users
- Feedback mechanisms throughout the AI lifecycle
- Third-party auditing when appropriate
- Transparency about AI system capabilities and limitations

**GV-6: Policies and procedures are in place to address AI risks from third-party entities.**
- Vendor assessment for AI components (models, data, APIs)
- Contractual requirements for AI providers
- Supply chain risk management for AI
- Incident response coordination with third parties

#### Key Takeaway
GOVERN is not a one-time setup — it requires ongoing attention as AI capabilities, organizational needs, and the regulatory landscape evolve.

---

### 2. MAP

**Purpose:** Identify and document the context, risks, and potential impacts of an AI system before and during development.

MAP is about understanding what you are building, who it affects, and what can go wrong. It happens early in the AI lifecycle and is revisited as the system evolves.

#### Categories

**MP-1: Context is established and understood.**
- Define the AI system's intended purpose and operational environment
- Document the target users and affected populations
- Identify legal, regulatory, and ethical requirements
- Understand the deployment context (high-stakes vs. low-stakes)

**MP-2: AI actors and their responsibilities are mapped.**
- Identify all stakeholders (developers, deployers, operators, end users, affected parties)
- Document data flows and decision points
- Map human-AI interaction points and handoff mechanisms
- Clarify who has override authority

**MP-3: AI system risks and benefits are identified.**
- Conduct risk identification workshops
- Document potential failure modes and their consequences
- Assess both individual and societal impacts
- Identify benefits and ensure they are achievable and distributed equitably

**MP-4: Risks are prioritized.**
- Assess likelihood and severity of identified risks
- Consider cascading and systemic risks
- Prioritize based on organizational risk tolerance
- Document risk acceptance decisions and rationale

**MP-5: Impacts to individuals, groups, communities, organizations, and society are characterized.**
- Assess impacts across demographics and communities
- Consider both intended and unintended consequences
- Evaluate impacts over different time horizons
- Document assumptions and limitations of impact assessments

#### Key Takeaway
MAP produces the risk register and context documentation that MEASURE and MANAGE will work from. Skipping MAP means you are managing risks blindly.

---

### 3. MEASURE

**Purpose:** Quantify, assess, and monitor AI risks using appropriate methods and metrics.

MEASURE is about turning the qualitative risks identified in MAP into quantifiable, trackable indicators. It covers both pre-deployment testing and ongoing monitoring.

#### Categories

**MS-1: Appropriate measurement approaches are identified and applied.**
- Select metrics relevant to the identified risks (accuracy, fairness, robustness, etc.)
- Use validated measurement tools and methodologies
- Consider both quantitative metrics and qualitative assessments
- Document measurement limitations and confidence levels

**MS-2: AI systems are evaluated for trustworthy characteristics.**
- Test for each of the seven trustworthy AI characteristics (see below)
- Use red-teaming and adversarial testing
- Conduct bias audits across protected groups
- Assess explainability and interpretability

**MS-3: Mechanisms for tracking AI risks over time are in place.**
- Continuous monitoring of model performance in production
- Data drift and concept drift detection
- Automated alerting for metric degradation
- Regular re-evaluation against evolving benchmarks

**MS-4: Feedback about AI system performance is collected and integrated.**
- End-user feedback mechanisms
- Incident reporting and analysis
- External audit findings
- Comparison with peer systems and industry benchmarks

#### Key Takeaway
Measurement is not a one-time activity. AI systems degrade over time as data distributions shift, user behavior changes, and new attack vectors emerge. Continuous measurement is essential.

---

### 4. MANAGE

**Purpose:** Allocate resources and implement actions to address the risks identified through MAP and quantified through MEASURE.

MANAGE is where decisions are made and actions are taken: mitigate, accept, transfer, or avoid identified risks.

#### Categories

**MG-1: AI risks are prioritized and acted upon.**
- Implement risk mitigation plans for high-priority risks
- Allocate resources proportional to risk severity
- Track mitigation effectiveness over time
- Escalate risks that exceed organizational tolerance

**MG-2: Strategies to maximize AI benefits and minimize negative impacts are planned and documented.**
- Design mitigations for identified harms
- Plan for graceful degradation when AI components fail
- Document fallback procedures (human override, safe defaults)
- Prepare communication plans for stakeholders

**MG-3: AI risks and benefits from third-party resources are managed.**
- Ongoing vendor monitoring and assessment
- Contract enforcement for AI service providers
- Incident response coordination
- Contingency plans for vendor failures

**MG-4: Risk treatments are documented and monitored for effectiveness.**
- Maintain risk treatment records
- Regularly review whether treatments remain effective
- Update treatments as the threat landscape evolves
- Share lessons learned across the organization

#### Key Takeaway
MANAGE closes the loop. Without it, risks are identified and measured but never actually addressed. MANAGE also feeds back into GOVERN (do policies need updating?) and MAP (are there new risks to document?).

---

## Trustworthy AI Characteristics

The AI RMF identifies seven characteristics of trustworthy AI systems. These are not independent — they interact and sometimes create tensions that must be balanced.

### 1. Valid and Reliable
The AI system performs as intended under expected conditions and produces consistent results. Validation confirms the system meets its requirements; reliability means it does so consistently over time.

### 2. Safe
The AI system does not endanger human life, health, property, or the environment. Safety considerations include fail-safe mechanisms, operational limits, and graceful degradation.

### 3. Secure and Resilient
The AI system can withstand adversarial attacks, recover from disruptions, and maintain confidentiality, integrity, and availability. This encompasses cybersecurity, adversarial ML, and supply chain security.

### 4. Accountable and Transparent
The organization can explain the AI system's decisions and operations to stakeholders. There is a clear chain of accountability for the system's outcomes. Transparency does not mean revealing all model internals — it means providing sufficient information for stakeholders to understand and challenge decisions.

### 5. Explainable and Interpretable
The AI system's outputs can be understood by its intended audiences. Explainability refers to the ability to describe the mechanism (how the model works); interpretability refers to the ability to describe the meaning (why the model produced this output).

### 6. Privacy-Enhanced
The AI system protects individuals' privacy throughout its lifecycle: data collection, training, inference, and storage. This includes data minimization, de-identification, consent management, and compliance with privacy regulations.

### 7. Fair — with Harmful Bias Managed
The AI system treats individuals and groups equitably. Harmful biases (systemic, statistical, human) are identified, measured, and mitigated. Fairness is context-dependent — the appropriate fairness metric depends on the use case and affected communities.

### Interactions and Tensions

| Tension | Example |
|---------|---------|
| Transparency vs. Security | Revealing model architecture helps users understand decisions but also helps attackers craft adversarial inputs |
| Privacy vs. Fairness | Removing demographic data protects privacy but makes it harder to detect and correct bias |
| Performance vs. Explainability | Simpler, more explainable models may sacrifice accuracy compared to complex black-box models |
| Safety vs. Innovation | Strict safety constraints may limit the system's ability to handle novel situations |

---

## Generative AI Profile (NIST AI 600-1)

NIST AI 600-1, the Generative AI Profile, is a companion document that maps GenAI-specific risks to the AI RMF functions. Published in 2024, it addresses risks that are unique to or amplified by generative AI systems.

### Key GenAI-Specific Risks

**CBRN Information (Chemical, Biological, Radiological, Nuclear):** GenAI systems may provide detailed instructions for creating dangerous materials, lowering the barrier to harm.

**Confabulation (Hallucination):** GenAI produces plausible-sounding but fabricated information, including fake citations, invented facts, and nonexistent entities.

**Data Privacy:** GenAI models may memorize and reproduce training data, including PII, copyrighted content, and confidential business information.

**Environmental Impact:** Training and running large GenAI models requires significant computational resources, contributing to energy consumption and carbon emissions.

**Homogenization:** Widespread use of the same GenAI models leads to homogenized outputs, reduced diversity of thought, and systemic fragility if the model has a common failure mode.

**Human-AI Configuration:** Users may over-trust, under-trust, or misunderstand GenAI capabilities, leading to inappropriate use or missed value.

**Information Integrity:** GenAI enables creation of deepfakes, synthetic media, and misinformation at scale, threatening the integrity of information ecosystems.

**Information Security:** GenAI can be exploited for phishing at scale, automated vulnerability exploitation, and social engineering attacks.

**Intellectual Property:** GenAI systems trained on copyrighted content may produce outputs that infringe IP rights, creating legal liability.

**Obscene, Degrading, and/or Abusive Content (ODAC):** GenAI can produce harmful content including hate speech, sexual content, and content that targets vulnerable populations.

**Value Chain and Component Integration:** GenAI systems rely on complex supply chains (foundation model providers, fine-tuning services, retrieval systems) where risk propagates through components.

### Mapping to AI RMF Functions

The GenAI Profile maps each risk to specific GOVERN, MAP, MEASURE, and MANAGE actions. For example, confabulation risk maps to:
- **GOVERN:** Establish policies on acceptable hallucination rates for different use cases
- **MAP:** Identify where confabulation has the highest impact (medical, legal, financial)
- **MEASURE:** Implement automated fact-checking, ground-truth comparison, and user feedback loops
- **MANAGE:** Deploy retrieval augmentation, constrained generation, and user-facing disclaimers

---

## Implementation Guidance

### Getting Started
1. **Start with GOVERN:** Establish organizational commitment and assign responsibility before building systems.
2. **Use the AI RMF Playbook:** NIST provides suggested actions for each subcategory. Start with a self-assessment.
3. **Integrate, don't silo:** Embed AI risk management into existing risk management processes rather than creating a parallel structure.
4. **Right-size your approach:** A customer-facing autonomous system requires more rigorous risk management than an internal summarization tool.

### Common Implementation Patterns

**Tiered approach:** Classify AI systems by risk level (critical, high, medium, low) and apply proportional rigor to each tier.

**Risk register integration:** Add AI-specific risks to the organization's existing risk register rather than maintaining a separate AI risk register.

**Cross-functional AI governance committee:** Bring together representatives from engineering, security, legal, compliance, privacy, and business units.

**Red team + blue team:** Establish adversarial testing (red team) and monitoring (blue team) specifically for AI systems.

---

## Comparison with Other Frameworks

| Framework | Scope | Mandatory? | Focus |
|-----------|-------|-----------|-------|
| NIST AI RMF | All AI systems, all sectors | Voluntary | Risk management processes |
| EU AI Act | AI systems in EU market | Mandatory (phased 2024-2027) | Risk classification and compliance |
| ISO/IEC 42001 | AI management systems | Voluntary (certifiable) | Management system standard |
| OECD AI Principles | National AI policies | Voluntary (intergovernmental) | High-level principles |
| Singapore Model AI Governance Framework | All AI, focused on deployment | Voluntary | Practical governance guidance |
| IEEE 7000 | Ethical systems design | Voluntary | Values-based design methodology |

**Key differentiator of NIST AI RMF:** It is process-oriented (how to manage risk) rather than outcome-oriented (what outcomes to achieve). This makes it broadly applicable but requires organizations to define their own risk thresholds and success criteria.

---

## Self-Test Questions

1. **Explain the GOVERN function and why it is described as "foundational" to the other three functions.** What happens to MAP, MEASURE, and MANAGE if GOVERN is weak?

2. **A startup is building an LLM-powered medical triage chatbot. Walk through how you would apply the MAP function to this system.** What risks would you identify, and how would you prioritize them?

3. **Describe the tension between explainability and security in the trustworthy AI characteristics.** Give an example where optimizing for one degrades the other, and explain how you would balance them.

4. **What is the difference between the base AI RMF 1.0 and the GenAI Profile (AI 600-1)?** Why was a separate GenAI profile needed?

5. **Compare the NIST AI RMF with the EU AI Act. How could an organization use both?** What does each provide that the other does not?

6. **A company has deployed an AI-powered hiring tool. Six months after deployment, they discover it is disproportionately rejecting candidates from a specific demographic. Map this situation to the MEASURE and MANAGE functions.** What should they have been monitoring, and what actions should they take?

7. **Explain the concept of "confabulation" as described in NIST AI 600-1. How does it differ from a traditional software bug?** Why does it require different mitigation strategies?

---

## Resources

- [NIST AI RMF 1.0 (AI 100-1)](https://www.nist.gov/artificial-intelligence/executive-order-safe-secure-and-trustworthy-artificial-intelligence)
- [AI RMF Playbook](https://airc.nist.gov/AI_RMF_Knowledge_Base/Playbook)
- [NIST AI 600-1: GenAI Profile](https://airc.nist.gov/Docs/1)
- [AI RMF Crosswalk (mapping to other frameworks)](https://airc.nist.gov/Crosswalks)
- [NIST Trustworthy and Responsible AI Resource Center](https://airc.nist.gov/)
