"""Tests for resume parser."""
import os
import pytest


def get_fixture_path(name: str) -> str:
    return os.path.join(os.path.dirname(__file__), "fixtures", name)


class TestResumeParser:
    def test_parse_text_resume(self):
        from prep_agent.integrations.resume_parser import ResumeParser
        parser = ResumeParser()
        result = parser.parse(get_fixture_path("sample-resume.txt"))
        assert result is not None
        assert "raw_text" in result
        assert len(result["raw_text"]) > 0

    def test_extract_skills(self):
        from prep_agent.integrations.resume_parser import ResumeParser
        parser = ResumeParser()
        result = parser.parse(get_fixture_path("sample-resume.txt"))
        skills_lower = [s.lower() for s in result.get("skills", [])]
        assert "python" in skills_lower or "aws" in skills_lower

    def test_extract_certifications(self):
        from prep_agent.integrations.resume_parser import ResumeParser
        parser = ResumeParser()
        result = parser.parse(get_fixture_path("sample-resume.txt"))
        certs = result.get("certifications", [])
        assert len(certs) > 0
        cert_text = " ".join(certs).lower()
        assert "aws" in cert_text or "cissp" in cert_text

    def test_estimate_experience(self):
        from prep_agent.integrations.resume_parser import ResumeParser
        parser = ResumeParser()
        result = parser.parse(get_fixture_path("sample-resume.txt"))
        years = result.get("experience_years", 0)
        assert years >= 10  # Jane Doe has 13 years

    def test_unsupported_extension(self):
        from prep_agent.integrations.resume_parser import ResumeParser
        parser = ResumeParser()
        with pytest.raises((ValueError, FileNotFoundError)):
            parser.parse("/tmp/fake-resume.xyz")

    def test_extract_name(self):
        from prep_agent.integrations.resume_parser import ResumeParser
        parser = ResumeParser()
        result = parser.parse(get_fixture_path("sample-resume.txt"))
        # Should detect name from first line
        assert result.get("name") is not None


class TestJobFetcher:
    def test_parse_text_job(self):
        from prep_agent.integrations.job_fetcher import JobFetcher
        fetcher = JobFetcher()
        with open(get_fixture_path("sample-job-posting.txt")) as f:
            text = f.read()
        result = fetcher.parse_text(text)
        assert result is not None
        assert "title" in result or "raw_text" in result

    def test_extract_years_required(self):
        from prep_agent.integrations.job_fetcher import JobFetcher
        fetcher = JobFetcher()
        years = fetcher._extract_years_required("Must have 10+ years of experience in security")
        assert years == 10

    def test_extract_skills_from_job(self):
        from prep_agent.integrations.job_fetcher import JobFetcher
        fetcher = JobFetcher()
        with open(get_fixture_path("sample-job-posting.txt")) as f:
            text = f.read()
        skills = fetcher._extract_skills_from_job(text)
        skills_lower = [s.lower() for s in skills]
        assert "python" in skills_lower or "aws" in skills_lower
