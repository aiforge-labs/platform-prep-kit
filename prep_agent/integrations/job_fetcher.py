"""Job posting fetcher -- retrieves and parses job descriptions from URLs."""

from __future__ import annotations

import re
import sys
from typing import Optional


class JobFetcher:
    """Fetch and parse job postings from URLs or pasted text."""

    # Default headers to look like a regular browser request
    _DEFAULT_HEADERS: dict[str, str] = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def fetch(self, url: str) -> dict | None:
        """Fetch a job posting from *url* and return structured data.

        Returns ``None`` if the page cannot be retrieved (blocked, timeout, etc.).

        Returned dict keys:
            title, company, location, description, responsibilities,
            required_qualifications, preferred_qualifications, skills,
            experience_years, education, certifications_mentioned, raw_text
        """
        try:
            import httpx  # type: ignore[import-untyped]
        except ImportError:
            print(
                "httpx is required to fetch URLs. Install it with:\n"
                "  pip install httpx",
                file=sys.stderr,
            )
            return None

        try:
            with httpx.Client(
                headers=self._DEFAULT_HEADERS,
                follow_redirects=True,
                timeout=30.0,
            ) as client:
                response = client.get(url)
                response.raise_for_status()
        except Exception as exc:
            print(f"Failed to fetch URL: {exc}", file=sys.stderr)
            return None

        raw_html = response.text
        raw_text = self._html_to_text(raw_html)

        if not raw_text or len(raw_text.strip()) < 50:
            print(
                "Fetched page appears empty or too short. "
                "The site may block automated requests.",
                file=sys.stderr,
            )
            return None

        return self.parse_text(raw_text)

    def fetch_with_fallback(self, url: str) -> dict:
        """Try URL fetch; fall back to asking the user to paste the text."""
        result = self.fetch(url)
        if result is not None:
            return result
        return self._prompt_paste()

    def parse_text(self, text: str) -> dict:
        """Parse raw job-description text into structured data."""
        title = self._extract_title(text)
        company = self._extract_company(text)
        location = self._extract_location(text)
        responsibilities = self._extract_section(
            text,
            [
                "responsibilities",
                "what you'll do",
                "what you will do",
                "job duties",
                "key responsibilities",
                "role responsibilities",
                "duties",
            ],
        )
        required_quals = self._extract_section(
            text,
            [
                "required qualifications",
                "requirements",
                "minimum qualifications",
                "what you'll need",
                "what you need",
                "must have",
                "basic qualifications",
                "required skills",
            ],
        )
        preferred_quals = self._extract_section(
            text,
            [
                "preferred qualifications",
                "nice to have",
                "preferred skills",
                "desired qualifications",
                "bonus qualifications",
                "plus",
                "preferred",
            ],
        )
        skills = self._extract_skills_from_job(text)
        experience_years = self._extract_years_required(text)
        education = self._extract_education(text)
        certs = self._extract_certs_mentioned(text)

        # Build a short description from the top portion if no explicit section found
        description = self._extract_section(
            text,
            [
                "description",
                "about the role",
                "about this role",
                "overview",
                "summary",
                "the opportunity",
                "job description",
                "role overview",
            ],
        )
        if not description:
            # Use the first ~500 chars as a fallback description
            description = text[:500].strip()

        return {
            "title": title,
            "company": company,
            "location": location,
            "description": description,
            "responsibilities": responsibilities,
            "required_qualifications": required_quals,
            "preferred_qualifications": preferred_quals,
            "skills": skills,
            "experience_years": experience_years,
            "education": education,
            "certifications_mentioned": certs,
            "raw_text": text,
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _prompt_paste(self) -> dict:
        """Ask the user to paste a job description interactively."""
        try:
            import click  # type: ignore[import-untyped]

            click.echo(
                "\nCould not fetch the job posting automatically.\n"
                "Please paste the job description below.\n"
                "When done, press Enter twice on an empty line.\n"
            )
        except ImportError:
            print(
                "\nCould not fetch the job posting automatically.\n"
                "Please paste the job description below.\n"
                "When done, press Enter twice on an empty line.\n"
            )

        lines: list[str] = []
        empty_count = 0
        try:
            while True:
                line = input()
                if line == "":
                    empty_count += 1
                    if empty_count >= 2:
                        break
                    lines.append(line)
                else:
                    empty_count = 0
                    lines.append(line)
        except (EOFError, KeyboardInterrupt):
            pass

        text = "\n".join(lines).strip()
        if not text:
            return {
                "title": None,
                "company": None,
                "location": None,
                "description": "",
                "responsibilities": "",
                "required_qualifications": "",
                "preferred_qualifications": "",
                "skills": [],
                "experience_years": None,
                "education": [],
                "certifications_mentioned": [],
                "raw_text": "",
            }

        return self.parse_text(text)

    # ------------------------------------------------------------------
    # HTML handling
    # ------------------------------------------------------------------

    def _html_to_text(self, html: str) -> str:
        """Convert HTML to readable plain text."""
        # Try BeautifulSoup first
        try:
            from bs4 import BeautifulSoup  # type: ignore[import-untyped]

            soup = BeautifulSoup(html, "html.parser")

            # Remove script and style elements
            for tag in soup(["script", "style", "nav", "footer", "header"]):
                tag.decompose()

            text = soup.get_text(separator="\n")
        except ImportError:
            # Bare-bones fallback: strip HTML tags with regex
            text = re.sub(r"<script[^>]*>.*?</script>", "", html, flags=re.S | re.I)
            text = re.sub(r"<style[^>]*>.*?</style>", "", text, flags=re.S | re.I)
            text = re.sub(r"<br\s*/?>", "\n", text, flags=re.I)
            text = re.sub(r"</?(?:p|div|h[1-6]|li|tr)[^>]*>", "\n", text, flags=re.I)
            text = re.sub(r"<[^>]+>", " ", text)

        # Collapse whitespace
        lines = [ln.strip() for ln in text.splitlines()]
        # Remove consecutive blank lines
        cleaned: list[str] = []
        prev_blank = False
        for ln in lines:
            if not ln:
                if not prev_blank:
                    cleaned.append("")
                prev_blank = True
            else:
                prev_blank = False
                cleaned.append(ln)

        return "\n".join(cleaned).strip()

    # ------------------------------------------------------------------
    # Section / field extractors
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_title(text: str) -> str | None:
        """Guess the job title from the text."""
        # Look for explicit "Job Title:" or "Position:" lines
        match = re.search(
            r"(?:job\s+title|position|role)\s*[:|\-]\s*(.+)",
            text,
            re.I,
        )
        if match:
            return match.group(1).strip()

        # Heuristic: the first non-blank, non-company line that contains a
        # role keyword is likely the title.
        role_words = re.compile(
            r"\b(engineer|developer|architect|manager|director|lead|analyst"
            r"|consultant|administrator|specialist|scientist|designer"
            r"|coordinator|devops|sre|principal|staff|senior|junior"
            r"|intern|associate|head\s+of)\b",
            re.I,
        )
        for line in text.splitlines()[:20]:
            stripped = line.strip()
            if stripped and role_words.search(stripped) and len(stripped) < 120:
                return stripped
        return None

    @staticmethod
    def _extract_company(text: str) -> str | None:
        """Guess the company name."""
        match = re.search(
            r"(?:company|employer|organization|about)\s*[:|\-]\s*(.+)",
            text,
            re.I,
        )
        if match:
            return match.group(1).strip()

        # "at <Company>" pattern
        match = re.search(r"\bat\s+([A-Z][\w\s&.,]+?)(?:\s*[-|]|\n)", text)
        if match:
            return match.group(1).strip().rstrip(",.")

        return None

    @staticmethod
    def _extract_location(text: str) -> str | None:
        """Extract location from text."""
        match = re.search(
            r"(?:location|office|based\s+in)\s*[:|\-]\s*(.+)",
            text,
            re.I,
        )
        if match:
            return match.group(1).strip()

        # Common patterns: "City, State" or "Remote"
        match = re.search(r"\b(remote|hybrid|on-?site)\b", text, re.I)
        if match:
            # Try to find a city nearby
            loc_match = re.search(
                r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?,\s*[A-Z]{2})\s*(?:\(|[-|]|\b(?:remote|hybrid|on-?site)\b)",
                text,
            )
            if loc_match:
                return f"{loc_match.group(1)} ({match.group(0)})"
            return match.group(0).strip()

        return None

    @staticmethod
    def _extract_section(text: str, header_variants: list[str]) -> str:
        """Extract text under a section identified by header variants."""
        # Build a pattern that matches any header variant as a line
        escaped = [re.escape(h) for h in header_variants]
        header_pattern = re.compile(
            r"^[\s#*]*(?:" + "|".join(escaped) + r")[\s:]*$",
            re.I | re.M,
        )

        # Also try inline headers (e.g., "Responsibilities:" at start of a line)
        inline_pattern = re.compile(
            r"^[\s#*]*(?:" + "|".join(escaped) + r")\s*:\s*$",
            re.I | re.M,
        )

        lines = text.splitlines()
        start_idx: int | None = None

        for i, line in enumerate(lines):
            if header_pattern.match(line.strip()) or inline_pattern.match(line.strip()):
                start_idx = i + 1
                break

        if start_idx is None:
            return ""

        # Collect lines until the next section header or end of text
        section_header = re.compile(
            r"^[\s#*]*[A-Z][\w\s/&]{2,40}[\s:]*$"
        )
        collected: list[str] = []
        for i in range(start_idx, len(lines)):
            line = lines[i]
            stripped = line.strip()
            # Stop at what looks like a new section header (but not bullet items)
            if (
                stripped
                and section_header.match(stripped)
                and not stripped.startswith(("-", "*", "\u2022", "\u2023"))
                and i > start_idx + 1
            ):
                break
            collected.append(line)

        return "\n".join(collected).strip()

    @staticmethod
    def _extract_years_required(text: str) -> int | None:
        """Extract years-of-experience requirement from the text."""
        patterns = [
            re.compile(r"(\d{1,2})\+?\s*(?:to\s+\d{1,2}\s+)?years?\s+(?:of\s+)?experience", re.I),
            re.compile(r"(\d{1,2})\+?\s*years?\s+(?:of\s+)?(?:relevant|professional|related|industry)", re.I),
            re.compile(r"minimum\s+(?:of\s+)?(\d{1,2})\+?\s*years?", re.I),
            re.compile(r"at\s+least\s+(\d{1,2})\+?\s*years?", re.I),
            re.compile(r"(\d{1,2})-\d{1,2}\s*years?\s+(?:of\s+)?experience", re.I),
        ]
        for pat in patterns:
            match = pat.search(text)
            if match:
                return int(match.group(1))
        return None

    @staticmethod
    def _extract_skills_from_job(text: str) -> list[str]:
        """Extract skills mentioned in a job posting.

        Re-uses the KNOWN_SKILLS set from resume_parser for consistency.
        """
        from prep_agent.integrations.resume_parser import KNOWN_SKILLS

        text_lower = text.lower()
        found: list[str] = []
        for skill in sorted(KNOWN_SKILLS):
            if len(skill) <= 2:
                pattern = rf"(?<![a-zA-Z]){re.escape(skill)}(?![a-zA-Z])"
            else:
                pattern = rf"\b{re.escape(skill)}\b"
            if re.search(pattern, text_lower):
                found.append(skill)
        return found

    @staticmethod
    def _extract_education(text: str) -> list[str]:
        """Extract education requirements."""
        degree_pattern = re.compile(
            r"(?:bachelor|master|ph\.?d|doctor|associate|mba|m\.?s\.?|b\.?s\.?|b\.?a\.?|m\.?a\.?|b\.?eng|m\.?eng)"
            r"(?:'?s?)?"
            r"(?:\s+(?:of|in)\s+[\w\s,&]+)?",
            re.I,
        )
        results: list[str] = []
        seen: set[str] = set()
        for match in degree_pattern.finditer(text):
            deg = match.group(0).strip()
            if deg.lower() not in seen and len(deg) > 3:
                seen.add(deg.lower())
                results.append(deg)
        return results

    @staticmethod
    def _extract_certs_mentioned(text: str) -> list[str]:
        """Extract certifications mentioned in the job posting."""
        from prep_agent.integrations.resume_parser import CERT_PATTERNS

        certs: list[str] = []
        seen_lower: set[str] = set()
        for pat in CERT_PATTERNS:
            for match in pat.finditer(text):
                cert = match.group(0).strip()
                if cert.lower() not in seen_lower:
                    seen_lower.add(cert.lower())
                    certs.append(cert)
        return certs
