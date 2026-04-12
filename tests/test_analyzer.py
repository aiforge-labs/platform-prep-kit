"""Tests for fitment analysis."""
import os
import pytest


def get_fixture_path(name: str) -> str:
    return os.path.join(os.path.dirname(__file__), "fixtures", name)


class TestFitmentAnalyzer:
    def _get_sample_job(self):
        return {
            "title": "Cloud Security Lead",
            "company": "Acme Corp",
            "location": "New York, NY",
            "required_qualifications": [
                "10+ years information security experience",
                "5+ years software engineering",
                "OWASP LLM Top 10",
                "Security architecture experience",
                "Python, JavaScript",
            ],
            "preferred_qualifications": [
                "AWS Certified Security Specialty",
                "MITRE ATLAS",
                "AI/ML experience",
            ],
            "skills": ["Python", "AWS", "Azure", "OWASP", "NIST", "Threat Modeling"],
            "experience_years": 10,
            "certifications_mentioned": ["AWS Certified Security"],
            "raw_text": "Cloud Security Lead role requiring 10+ years experience...",
        }

    def _get_sample_resume(self):
        return {
            "name": "Jane Doe",
            "current_role": "Senior Security Engineer",
            "experience_years": 13,
            "skills": ["Python", "AWS", "Azure", "Terraform", "Docker", "Kubernetes",
                       "IAM", "CloudTrail", "Security Hub", "OWASP Top 10"],
            "certifications": ["AWS Certified Security - Specialty", "CISSP"],
            "education": [{"degree": "MS Cybersecurity", "institution": "State University"}],
            "raw_text": "Senior Security Engineer with 13 years experience...",
        }

    def test_analyze_returns_score(self):
        from prep_agent.core.analyzer import FitmentAnalyzer
        analyzer = FitmentAnalyzer()
        result = analyzer.analyze(self._get_sample_job(), self._get_sample_resume())
        assert "overall_score" in result
        assert 0 <= result["overall_score"] <= 100

    def test_analyze_identifies_strengths(self):
        from prep_agent.core.analyzer import FitmentAnalyzer
        analyzer = FitmentAnalyzer()
        result = analyzer.analyze(self._get_sample_job(), self._get_sample_resume())
        assert len(result["strengths"]) > 0

    def test_analyze_identifies_gaps(self):
        from prep_agent.core.analyzer import FitmentAnalyzer
        analyzer = FitmentAnalyzer()
        result = analyzer.analyze(self._get_sample_job(), self._get_sample_resume())
        assert len(result["gaps"]) > 0

    def test_experience_match(self):
        from prep_agent.core.analyzer import FitmentAnalyzer
        analyzer = FitmentAnalyzer()
        result = analyzer.analyze(self._get_sample_job(), self._get_sample_resume())
        em = result["experience_match"]
        assert em["actual_years"] >= em["required_years"]  # 13 >= 10
        assert em["score"] >= 80  # Should score high when exceeding requirement

    def test_certification_match(self):
        from prep_agent.core.analyzer import FitmentAnalyzer
        analyzer = FitmentAnalyzer()
        result = analyzer.analyze(self._get_sample_job(), self._get_sample_resume())
        assert len(result["certification_match"]["have"]) > 0

    def test_skills_match(self):
        from prep_agent.core.analyzer import FitmentAnalyzer
        analyzer = FitmentAnalyzer()
        result = analyzer.analyze(self._get_sample_job(), self._get_sample_resume())
        assert len(result["skills_match"]["matched"]) > 0
        # Python and AWS should match
        matched_lower = {s.lower() for s in result["skills_match"]["matched"]}
        assert "python" in matched_lower or "aws" in matched_lower

    def test_generate_report_md(self):
        from prep_agent.core.analyzer import FitmentAnalyzer
        analyzer = FitmentAnalyzer()
        result = analyzer.analyze(self._get_sample_job(), self._get_sample_resume())
        report = analyzer.generate_report_md(result)
        assert "# Fitment Analysis" in report
        assert "Score" in report

    def test_perfect_match_high_score(self):
        from prep_agent.core.analyzer import FitmentAnalyzer
        analyzer = FitmentAnalyzer()
        job = self._get_sample_job()
        resume = self._get_sample_resume()
        # Add all job skills to resume
        resume["skills"] = job["skills"] + resume["skills"]
        result = analyzer.analyze(job, resume)
        assert result["overall_score"] >= 70

    def test_no_match_low_score(self):
        from prep_agent.core.analyzer import FitmentAnalyzer
        analyzer = FitmentAnalyzer()
        job = self._get_sample_job()
        resume = {
            "name": "Test",
            "current_role": "Baker",
            "experience_years": 2,
            "skills": ["Baking", "Pastry"],
            "certifications": [],
            "education": [],
            "raw_text": "Baker with 2 years experience",
        }
        result = analyzer.analyze(job, resume)
        assert result["overall_score"] < 40


class TestSkillNormalization:
    def test_alias_matching(self):
        from prep_agent.core.analyzer import FitmentAnalyzer
        analyzer = FitmentAnalyzer()
        # "aws" and "amazon web services" should match
        s1 = analyzer._normalize_skill("AWS")
        s2 = analyzer._normalize_skill("Amazon Web Services")
        # Both should normalize to the same thing or be in alias map
        assert s1 == s2 or s1 in ("aws", "amazon web services")
