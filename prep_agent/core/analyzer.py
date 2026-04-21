"""Fitment analyzer for platform prep kit.

Keyword-based analysis comparing job requirements against resume data.
No AI/LLM dependency required.
"""

import re
from typing import Any, Optional

# Bidirectional alias mapping: each pair maps both directions.
# Keys and values are all lowercase.
SKILL_ALIASES: dict[str, str] = {
    "aws": "amazon web services",
    "amazon web services": "aws",
    "gcp": "google cloud platform",
    "google cloud platform": "gcp",
    "k8s": "kubernetes",
    "kubernetes": "k8s",
    "js": "javascript",
    "javascript": "js",
    "ts": "typescript",
    "typescript": "ts",
    "ml": "machine learning",
    "machine learning": "ml",
    "ai": "artificial intelligence",
    "artificial intelligence": "ai",
    "llm": "large language model",
    "large language model": "llm",
    "dl": "deep learning",
    "deep learning": "dl",
    "nlp": "natural language processing",
    "natural language processing": "nlp",
    "cv": "computer vision",
    "computer vision": "cv",
    "devops": "development operations",
    "development operations": "devops",
    "ci/cd": "continuous integration continuous deployment",
    "continuous integration continuous deployment": "ci/cd",
    "sre": "site reliability engineering",
    "site reliability engineering": "sre",
    "iac": "infrastructure as code",
    "infrastructure as code": "iac",
    "tf": "terraform",
    "terraform": "tf",
    "cdk": "cloud development kit",
    "cloud development kit": "cdk",
    "react.js": "react",
    "react": "react.js",
    "node.js": "node",
    "node": "node.js",
    "vue.js": "vue",
    "vue": "vue.js",
    "next.js": "next",
    "next": "next.js",
    "postgres": "postgresql",
    "postgresql": "postgres",
    "mongo": "mongodb",
    "mongodb": "mongo",
    "dynamo": "dynamodb",
    "dynamodb": "dynamo",
    "es": "elasticsearch",
    "elasticsearch": "es",
    "redis": "redis cache",
    "redis cache": "redis",
    "oop": "object oriented programming",
    "object oriented programming": "oop",
    "api": "application programming interface",
    "rest": "restful api",
    "restful api": "rest",
    "graphql": "graph query language",
    "graph query language": "graphql",
    "sqs": "simple queue service",
    "simple queue service": "sqs",
    "sns": "simple notification service",
    "simple notification service": "sns",
    "s3": "simple storage service",
    "simple storage service": "s3",
    "ec2": "elastic compute cloud",
    "elastic compute cloud": "ec2",
    "ecs": "elastic container service",
    "elastic container service": "ecs",
    "eks": "elastic kubernetes service",
    "elastic kubernetes service": "eks",
    "lambda": "aws lambda",
    "aws lambda": "lambda",
    "rds": "relational database service",
    "relational database service": "rds",
    "iam": "identity and access management",
    "identity and access management": "iam",
    "vpc": "virtual private cloud",
    "virtual private cloud": "vpc",
    "cdn": "content delivery network",
    "content delivery network": "cdn",
    "dns": "domain name system",
    "domain name system": "dns",
    "sql": "structured query language",
    "structured query language": "sql",
    "nosql": "non-relational database",
    "non-relational database": "nosql",
    "ux": "user experience",
    "user experience": "ux",
    "ui": "user interface",
    "user interface": "ui",
    "pm": "project management",
    "project management": "pm",
    "agile": "agile methodology",
    "agile methodology": "agile",
    "scrum": "scrum framework",
    "scrum framework": "scrum",
    "tdd": "test driven development",
    "test driven development": "tdd",
    "bdd": "behavior driven development",
    "behavior driven development": "bdd",
}

# Keywords mapped to priority levels for gap identification
PRIORITY_KEYWORDS: dict[str, str] = {
    # Critical: core technical skills and must-haves
    "required": "critical",
    "must have": "critical",
    "must-have": "critical",
    "essential": "critical",
    "mandatory": "critical",
    "core": "critical",
    "fundamental": "critical",
    "minimum": "critical",
    "prerequisite": "critical",
    # High: strongly preferred skills
    "preferred": "high",
    "strongly preferred": "high",
    "highly desired": "high",
    "important": "high",
    "expected": "high",
    "significant": "high",
    "key": "high",
    "advanced": "high",
    "expert": "high",
    "senior": "high",
    # Moderate: nice-to-haves
    "nice to have": "moderate",
    "nice-to-have": "moderate",
    "bonus": "moderate",
    "plus": "moderate",
    "desirable": "moderate",
    "familiarity": "moderate",
    "exposure": "moderate",
    "awareness": "moderate",
    "beneficial": "moderate",
    "helpful": "moderate",
}

# Default weights for overall score calculation
DEFAULT_WEIGHTS: dict[str, float] = {
    "skills": 0.40,
    "experience": 0.25,
    "certifications": 0.15,
    "education": 0.10,
    "domain": 0.10,
}

# Estimated hours to close a gap, by priority
ESTIMATED_HOURS_BY_PRIORITY: dict[str, int] = {
    "critical": 20,
    "high": 12,
    "moderate": 6,
}

# Stop words to exclude from keyword extraction
_STOP_WORDS: set[str] = {
    "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "is", "are", "was", "were", "be", "been",
    "being", "have", "has", "had", "do", "does", "did", "will", "would",
    "could", "should", "may", "might", "shall", "can", "need", "must",
    "it", "its", "this", "that", "these", "those", "we", "you", "they",
    "our", "your", "their", "my", "his", "her", "who", "what", "which",
    "when", "where", "how", "not", "no", "nor", "as", "if", "than",
    "too", "very", "just", "about", "up", "out", "so", "also", "then",
    "into", "over", "such", "able", "etc", "work", "working", "using",
    "use", "used", "experience", "strong", "good", "well", "new", "team",
    "role", "years", "year", "including", "across", "within", "between",
    "through", "other", "all", "any", "each", "both", "more", "most",
}


class FitmentAnalyzer:
    """Analyze fitment between a job posting and a resume.

    Uses keyword matching and heuristic scoring -- no AI/LLM calls.
    """

    def __init__(
        self,
        skill_aliases: Optional[dict[str, str]] = None,
        weights: Optional[dict[str, float]] = None,
    ) -> None:
        self.skill_aliases = skill_aliases or SKILL_ALIASES
        self.weights = weights or DEFAULT_WEIGHTS

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def analyze(self, job_data: dict, resume_data: dict) -> dict:
        """Run full fitment analysis.

        Args:
            job_data: Dict with keys like 'description', 'requirements',
                      'skills', 'experience_years', 'certifications',
                      'education', 'domain'.
            resume_data: Dict with keys like 'summary', 'skills',
                         'experience_years', 'certifications',
                         'education', 'domain', 'titles'.

        Returns:
            Analysis result dict.
        """
        # Extract and normalize skill sets
        job_skills = self._build_skill_set(job_data)
        resume_skills = self._build_skill_set(resume_data)

        matched, missing, bonus = self._match_skills(job_skills, resume_skills)

        # Component scores
        skill_score = (
            (len(matched) / len(job_skills) * 100) if job_skills else 100.0
        )
        exp_score = self._score_experience(
            job_data.get("experience_years", 0),
            resume_data.get("experience_years", 0),
        )
        cert_score = self._score_certifications(
            job_data.get("certifications", []),
            resume_data.get("certifications", []),
        )
        edu_score = self._score_education(
            job_data.get("education", ""),
            resume_data.get("education", ""),
        )
        domain_score = self._score_domain(
            job_data.get("domain", ""),
            resume_data.get("domain", ""),
        )

        scores: dict[str, float] = {
            "skills": skill_score,
            "experience": exp_score,
            "certifications": cert_score,
            "education": edu_score,
            "domain": domain_score,
        }

        overall = self._calculate_overall_score(scores, self.weights)

        # Build strengths list
        strengths = self._build_strengths(scores, matched, resume_data)

        # Build gaps list
        gaps = self._identify_gaps(job_data, resume_data, missing)

        return {
            "overall_score": overall,
            "strengths": strengths,
            "gaps": gaps,
            "experience_match": {
                "required_years": job_data.get("experience_years", 0),
                "actual_years": resume_data.get("experience_years", 0),
                "score": round(exp_score, 1),
            },
            "certification_match": {
                "required": job_data.get("certifications", []),
                "have": resume_data.get("certifications", []),
                "score": round(cert_score, 1),
            },
            "skills_match": {
                "matched": sorted(matched),
                "missing": sorted(missing),
                "bonus": sorted(bonus),
            },
            "component_scores": {k: round(v, 1) for k, v in scores.items()},
        }

    def generate_report_md(self, analysis: dict) -> str:
        """Generate a markdown report from an analysis result dict.

        Args:
            analysis: Output of ``analyze()``.

        Returns:
            Markdown-formatted string.
        """
        lines: list[str] = []
        score = analysis["overall_score"]

        lines.append("# Fitment Analysis Report")
        lines.append("")
        lines.append(f"**Overall Score: {score}/100**")
        lines.append("")

        # Verdict
        if score >= 80:
            verdict = "Strong fit -- focus on polish and interview preparation."
        elif score >= 60:
            verdict = "Good fit with gaps -- targeted preparation recommended."
        elif score >= 40:
            verdict = "Moderate fit -- significant preparation needed."
        else:
            verdict = "Stretch role -- extensive skill building required."
        lines.append(f"*{verdict}*")
        lines.append("")

        # Component scores
        lines.append("## Component Scores")
        lines.append("")
        lines.append("| Area | Score |")
        lines.append("|------|-------|")
        for area, s in analysis.get("component_scores", {}).items():
            lines.append(f"| {area.title()} | {s} |")
        lines.append("")

        # Skills match
        sm = analysis.get("skills_match", {})
        lines.append("## Skills Match")
        lines.append("")
        if sm.get("matched"):
            lines.append(f"**Matched ({len(sm['matched'])}):** {', '.join(sm['matched'])}")
        if sm.get("missing"):
            lines.append(f"**Missing ({len(sm['missing'])}):** {', '.join(sm['missing'])}")
        if sm.get("bonus"):
            lines.append(f"**Bonus ({len(sm['bonus'])}):** {', '.join(sm['bonus'])}")
        lines.append("")

        # Experience
        em = analysis.get("experience_match", {})
        lines.append("## Experience")
        lines.append("")
        lines.append(
            f"Required: {em.get('required_years', 0)} years | "
            f"Actual: {em.get('actual_years', 0)} years | "
            f"Score: {em.get('score', 0)}"
        )
        lines.append("")

        # Certifications
        cm = analysis.get("certification_match", {})
        lines.append("## Certifications")
        lines.append("")
        if cm.get("required"):
            lines.append(f"Required: {', '.join(cm['required'])}")
        else:
            lines.append("No specific certifications required.")
        if cm.get("have"):
            lines.append(f"Have: {', '.join(cm['have'])}")
        lines.append(f"Score: {cm.get('score', 0)}")
        lines.append("")

        # Strengths
        lines.append("## Strengths")
        lines.append("")
        for s in analysis.get("strengths", []):
            lines.append(f"- **{s['area']}** (score: {s['score']}): {s['evidence']}")
        lines.append("")

        # Gaps
        lines.append("## Gaps & Recommendations")
        lines.append("")
        if analysis.get("gaps"):
            lines.append("| Priority | Area | Est. Hours | Recommendation |")
            lines.append("|----------|------|-----------|----------------|")
            for g in analysis["gaps"]:
                lines.append(
                    f"| {g['priority'].upper()} | {g['area']} | "
                    f"{g['estimated_hours']} | {g['recommendation']} |"
                )
        else:
            lines.append("No significant gaps identified.")
        lines.append("")

        # Total estimated hours
        total_hours = sum(g.get("estimated_hours", 0) for g in analysis.get("gaps", []))
        if total_hours:
            lines.append(f"**Total estimated preparation hours: {total_hours}**")
            lines.append("")

        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _extract_keywords(self, text: str) -> set[str]:
        """Extract meaningful keywords from text.

        Splits on non-alphanumeric boundaries, lowercases, removes stop words,
        and filters out very short tokens.
        """
        if not text:
            return set()

        # Preserve known multi-word terms by checking for them first
        lower_text = text.lower()
        found: set[str] = set()

        # Check for multi-word aliases
        for alias in self.skill_aliases:
            if " " in alias and alias in lower_text:
                found.add(alias)

        # Tokenize remaining
        tokens = re.findall(r"[a-z0-9][a-z0-9./#+-]*[a-z0-9+#]|[a-z0-9]", lower_text)
        for token in tokens:
            if token not in _STOP_WORDS and len(token) >= 2:
                found.add(token)

        return found

    def _normalize_skill(self, skill: str) -> str:
        """Normalize a skill name to its canonical lowercase form.

        If the skill has an alias, returns the shorter/more common form.
        """
        s = skill.strip().lower()
        # Return the alias if it exists and is shorter (prefer abbreviations
        # as canonical form); otherwise return as-is.
        alias = self.skill_aliases.get(s)
        if alias and len(alias) < len(s):
            return alias
        return s

    def _build_skill_set(self, data: dict) -> set[str]:
        """Build a normalized skill set from data dict fields."""
        skills: set[str] = set()

        # Explicit skills list
        for s in data.get("skills", []):
            skills.add(self._normalize_skill(s))

        # Extract from text fields
        for field in ("description", "requirements", "summary"):
            text = data.get(field, "")
            if text:
                for kw in self._extract_keywords(text):
                    skills.add(self._normalize_skill(kw))

        return skills

    def _match_skills(
        self, job_skills: set[str], resume_skills: set[str]
    ) -> tuple[set[str], set[str], set[str]]:
        """Match job skills against resume skills, accounting for aliases.

        Returns:
            (matched, missing, bonus) where:
            - matched: job skills present in resume (directly or via alias)
            - missing: job skills not found in resume
            - bonus: resume skills not required by job
        """
        # Expand each set with aliases for comparison
        resume_expanded = self._expand_with_aliases(resume_skills)
        job_expanded = self._expand_with_aliases(job_skills)

        matched: set[str] = set()
        missing: set[str] = set()

        for skill in job_skills:
            norm = self._normalize_skill(skill)
            alias = self.skill_aliases.get(norm, "")
            if norm in resume_expanded or alias in resume_expanded:
                matched.add(norm)
            else:
                missing.add(norm)

        bonus: set[str] = set()
        for skill in resume_skills:
            norm = self._normalize_skill(skill)
            alias = self.skill_aliases.get(norm, "")
            if norm not in job_expanded and alias not in job_expanded:
                bonus.add(norm)

        return matched, missing, bonus

    def _expand_with_aliases(self, skills: set[str]) -> set[str]:
        """Expand a skill set to include all known aliases."""
        expanded = set(skills)
        for s in skills:
            alias = self.skill_aliases.get(s)
            if alias:
                expanded.add(alias)
        return expanded

    def _score_experience(self, required_years: int, actual_years: int) -> float:
        """Score experience match on a 0-100 scale.

        Full marks if actual >= required.
        Partial credit scales linearly, with a floor at 20 for any experience.
        """
        if required_years <= 0:
            return 100.0
        if actual_years <= 0:
            return 0.0
        if actual_years >= required_years:
            # Bonus capped at 100
            return 100.0
        ratio = actual_years / required_years
        # Floor of 20 for having some experience
        return max(20.0, ratio * 100.0)

    def _score_certifications(self, required: list, have: list) -> float:
        """Score certification match on a 0-100 scale.

        Normalizes names and checks for overlap.
        """
        if not required:
            return 100.0
        if not have:
            return 0.0

        req_norm = {self._normalize_skill(c) for c in required}
        have_norm = {self._normalize_skill(c) for c in have}
        have_expanded = self._expand_with_aliases(have_norm)

        matched = sum(1 for r in req_norm if r in have_expanded)
        return (matched / len(req_norm)) * 100.0

    def _score_education(self, required: str, actual: str) -> float:
        """Score education match on a 0-100 scale.

        Simple keyword-level heuristic.
        """
        if not required:
            return 100.0
        if not actual:
            return 30.0  # Some baseline for unlisted education

        levels = ["high school", "associate", "bachelor", "master", "phd", "doctorate"]
        req_level = -1
        act_level = -1
        req_lower = required.lower()
        act_lower = actual.lower()

        for i, level in enumerate(levels):
            if level in req_lower:
                req_level = i
            if level in act_lower:
                act_level = i

        if req_level < 0:
            return 80.0  # Can't determine requirement
        if act_level < 0:
            return 50.0  # Can't determine actual
        if act_level >= req_level:
            return 100.0
        # Partial credit
        return max(30.0, (act_level / req_level) * 100.0)

    def _score_domain(self, job_domain: str, resume_domain: str) -> float:
        """Score domain/industry alignment on a 0-100 scale."""
        if not job_domain:
            return 80.0  # No specific domain required
        if not resume_domain:
            return 40.0

        job_keywords = self._extract_keywords(job_domain)
        resume_keywords = self._extract_keywords(resume_domain)

        if not job_keywords:
            return 80.0

        overlap = job_keywords & resume_keywords
        return min(100.0, (len(overlap) / len(job_keywords)) * 100.0)

    def _build_strengths(
        self, scores: dict[str, float], matched_skills: set[str], resume_data: dict
    ) -> list[dict[str, Any]]:
        """Build a list of strength areas from scores and matches."""
        strengths: list[dict[str, Any]] = []

        if scores.get("skills", 0) >= 60:
            strengths.append({
                "area": "Technical Skills",
                "score": round(scores["skills"], 1),
                "evidence": f"{len(matched_skills)} matching skills identified",
            })

        if scores.get("experience", 0) >= 70:
            strengths.append({
                "area": "Experience",
                "score": round(scores["experience"], 1),
                "evidence": f"{resume_data.get('experience_years', 0)} years of relevant experience",
            })

        if scores.get("certifications", 0) >= 70:
            certs = resume_data.get("certifications", [])
            strengths.append({
                "area": "Certifications",
                "score": round(scores["certifications"], 1),
                "evidence": f"{len(certs)} relevant certification(s)",
            })

        if scores.get("education", 0) >= 80:
            strengths.append({
                "area": "Education",
                "score": round(scores["education"], 1),
                "evidence": f"Education: {resume_data.get('education', 'meets requirements')}",
            })

        if scores.get("domain", 0) >= 70:
            strengths.append({
                "area": "Domain Knowledge",
                "score": round(scores["domain"], 1),
                "evidence": f"Domain: {resume_data.get('domain', 'aligned')}",
            })

        return strengths

    def _identify_gaps(
        self, job_data: dict, resume_data: dict, skill_gaps: set[str]
    ) -> list[dict[str, Any]]:
        """Generate a prioritized list of gaps to address.

        Args:
            job_data: Job requirements data.
            resume_data: Resume/profile data.
            skill_gaps: Set of missing skill names.

        Returns:
            List of gap dicts sorted by priority (critical first).
        """
        gaps: list[dict[str, Any]] = []
        priority_order = {"critical": 0, "high": 1, "moderate": 2}

        # Determine priority for each missing skill
        job_text = " ".join([
            job_data.get("description", ""),
            job_data.get("requirements", ""),
        ]).lower()

        for skill in skill_gaps:
            priority = self._infer_priority(skill, job_text)
            est_hours = ESTIMATED_HOURS_BY_PRIORITY.get(priority, 8)

            gaps.append({
                "area": skill,
                "score": 0,
                "priority": priority,
                "recommendation": f"Study and practice {skill}",
                "estimated_hours": est_hours,
            })

        # Check experience gap
        req_years = job_data.get("experience_years", 0)
        act_years = resume_data.get("experience_years", 0)
        if req_years > 0 and act_years < req_years:
            diff = req_years - act_years
            priority = "critical" if diff >= 3 else "high" if diff >= 1 else "moderate"
            gaps.append({
                "area": "Experience Gap",
                "score": round(self._score_experience(req_years, act_years), 1),
                "priority": priority,
                "recommendation": (
                    f"Bridge {diff}-year experience gap with projects, "
                    "contributions, or relevant demonstrations"
                ),
                "estimated_hours": min(diff * 10, 40),
            })

        # Check certification gaps
        req_certs = job_data.get("certifications", [])
        have_certs = {self._normalize_skill(c) for c in resume_data.get("certifications", [])}
        have_expanded = self._expand_with_aliases(have_certs)
        for cert in req_certs:
            norm = self._normalize_skill(cert)
            if norm not in have_expanded:
                gaps.append({
                    "area": f"Certification: {cert}",
                    "score": 0,
                    "priority": "high",
                    "recommendation": f"Obtain {cert} certification",
                    "estimated_hours": 30,
                })

        # Sort: critical > high > moderate, then alphabetically within priority
        gaps.sort(key=lambda g: (priority_order.get(g["priority"], 9), g["area"]))
        return gaps

    def _infer_priority(self, skill: str, job_text: str) -> str:
        """Infer priority for a skill gap based on job text context.

        Looks for priority keywords near the skill mention in the job text.
        Falls back to 'high' if no contextual clues are found.
        """
        skill_lower = skill.lower()

        # Check if the skill appears near any priority keywords
        # Use a window of ~100 chars around each skill mention
        idx = 0
        found_priorities: list[str] = []
        while True:
            pos = job_text.find(skill_lower, idx)
            if pos < 0:
                break
            window_start = max(0, pos - 100)
            window_end = min(len(job_text), pos + len(skill_lower) + 100)
            window = job_text[window_start:window_end]

            for keyword, priority in PRIORITY_KEYWORDS.items():
                if keyword in window:
                    found_priorities.append(priority)
            idx = pos + 1

        if found_priorities:
            # Return highest priority found
            priority_rank = {"critical": 0, "high": 1, "moderate": 2}
            return min(found_priorities, key=lambda p: priority_rank.get(p, 9))

        # Default: if skill is in the job requirements at all, it's at least high
        if skill_lower in job_text:
            return "high"
        return "moderate"

    def _calculate_overall_score(
        self, scores: dict[str, float], weights: dict[str, float]
    ) -> int:
        """Calculate weighted overall score.

        Args:
            scores: Dict of component name -> score (0-100).
            weights: Dict of component name -> weight (should sum to ~1.0).

        Returns:
            Weighted score as int, clamped to 0-100.
        """
        total = 0.0
        weight_sum = 0.0
        for component, weight in weights.items():
            if component in scores:
                total += scores[component] * weight
                weight_sum += weight

        if weight_sum <= 0:
            return 0

        # Normalize in case weights don't sum to 1
        raw = total / weight_sum
        return max(0, min(100, round(raw)))
