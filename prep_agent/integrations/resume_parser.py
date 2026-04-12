"""Resume parser -- extracts structured data from PDF, DOCX, or text resumes."""

from __future__ import annotations

import re
from pathlib import Path


# ---------------------------------------------------------------------------
# Known technical skills (~250 entries)
# ---------------------------------------------------------------------------
KNOWN_SKILLS: set[str] = {
    # Cloud platforms
    "aws", "amazon web services", "azure", "microsoft azure", "gcp",
    "google cloud", "google cloud platform", "oci", "oracle cloud",
    "alibaba cloud", "ibm cloud", "digitalocean", "heroku", "cloudflare",
    # AWS services
    "ec2", "s3", "lambda", "rds", "dynamodb", "ecs", "eks", "fargate",
    "cloudformation", "cloudwatch", "iam", "vpc", "route 53", "api gateway",
    "sqs", "sns", "kinesis", "redshift", "athena", "glue", "emr",
    "sagemaker", "bedrock", "step functions", "eventbridge", "aurora",
    "elasticache", "secrets manager", "systems manager", "ssm",
    "codepipeline", "codebuild", "codecommit", "codedeploy",
    # Azure services
    "azure devops", "azure ad", "entra id", "azure functions",
    "azure kubernetes service", "aks", "azure sql", "cosmos db",
    "azure storage", "azure monitor", "azure sentinel",
    # GCP services
    "bigquery", "cloud run", "cloud functions", "gke", "pub/sub",
    "cloud storage", "dataflow", "dataproc", "vertex ai", "cloud sql",
    # Languages
    "python", "java", "javascript", "typescript", "go", "golang", "rust",
    "c", "c++", "c#", "ruby", "php", "swift", "kotlin", "scala", "perl",
    "r", "matlab", "julia", "haskell", "elixir", "erlang", "lua",
    "objective-c", "dart", "groovy", "powershell", "bash", "shell",
    "sql", "plsql", "pl/sql", "t-sql", "graphql", "html", "css",
    # Frameworks & libraries
    "react", "angular", "vue", "vue.js", "svelte", "next.js", "nextjs",
    "nuxt", "express", "express.js", "fastapi", "flask", "django",
    "spring", "spring boot", "rails", "ruby on rails", ".net", "asp.net",
    "node.js", "nodejs", "deno", "bun", "electron", "react native",
    "flutter", "swiftui", "jetpack compose",
    # Data & databases
    "postgresql", "postgres", "mysql", "mariadb", "mongodb", "cassandra",
    "redis", "elasticsearch", "opensearch", "neo4j", "couchdb",
    "sqlite", "oracle db", "sql server", "mssql", "snowflake",
    "databricks", "dbt", "apache spark", "spark", "pyspark",
    "apache kafka", "kafka", "apache flink", "flink", "apache airflow",
    "airflow", "apache beam", "apache hive", "hive", "presto", "trino",
    "apache nifi", "pandas", "numpy", "dask", "polars",
    "etl", "elt", "data warehousing", "data lake", "data mesh",
    "data modeling", "data pipeline", "data engineering",
    # DevOps & infrastructure
    "terraform", "pulumi", "cloudformation", "cdk", "aws cdk",
    "ansible", "puppet", "chef", "saltstack",
    "docker", "podman", "containerd",
    "kubernetes", "k8s", "helm", "kustomize", "istio", "linkerd",
    "jenkins", "github actions", "gitlab ci", "circleci", "travis ci",
    "argo cd", "argocd", "flux", "spinnaker",
    "ci/cd", "continuous integration", "continuous deployment",
    "infrastructure as code", "iac", "gitops",
    "nginx", "apache", "haproxy", "envoy", "traefik",
    "prometheus", "grafana", "datadog", "new relic", "splunk",
    "elk stack", "logstash", "kibana", "fluentd", "jaeger",
    "pagerduty", "opsgenie", "victorops",
    "vagrant", "packer", "consul", "vault", "nomad",
    # Security
    "iam", "kms", "owasp", "siem", "soar", "zero trust",
    "penetration testing", "vulnerability assessment",
    "sso", "saml", "oauth", "oauth2", "oidc", "jwt",
    "waf", "firewall", "ids", "ips", "dlp",
    "encryption", "tls", "ssl", "pki", "certificates",
    "security compliance", "soc 2", "iso 27001", "fedramp", "hipaa",
    "pci dss", "gdpr", "nist", "cis benchmarks",
    "sast", "dast", "devsecops", "snyk", "aqua", "trivy",
    "crowdstrike", "sentinel one", "carbon black",
    # AI / ML
    "machine learning", "deep learning", "nlp",
    "natural language processing", "computer vision",
    "tensorflow", "pytorch", "keras", "scikit-learn", "sklearn",
    "hugging face", "transformers", "langchain", "llamaindex",
    "openai", "gpt", "llm", "large language models",
    "rag", "retrieval augmented generation",
    "sagemaker", "bedrock", "vertex ai", "azure ml",
    "mlflow", "kubeflow", "wandb", "weights and biases",
    "feature engineering", "model training", "model deployment",
    "generative ai", "prompt engineering", "fine-tuning",
    "reinforcement learning", "neural networks", "cnns", "rnns",
    "stable diffusion", "midjourney", "dall-e",
    # Networking
    "tcp/ip", "dns", "http", "https", "rest", "restful",
    "grpc", "websocket", "mqtt", "amqp",
    "load balancing", "cdn", "vpn", "sd-wan",
    # Project / methodology
    "agile", "scrum", "kanban", "jira", "confluence",
    "lean", "safe", "devops", "sre", "site reliability engineering",
    "microservices", "event-driven architecture", "domain-driven design",
    "design patterns", "solid", "clean architecture",
    # Version control & collaboration
    "git", "github", "gitlab", "bitbucket", "svn",
    # Testing
    "unit testing", "integration testing", "e2e testing",
    "selenium", "cypress", "playwright", "jest", "pytest", "junit",
    "testng", "mocha", "chai", "vitest",
    "tdd", "bdd", "load testing", "performance testing",
    "jmeter", "gatling", "locust", "k6",
    # OS & platforms
    "linux", "ubuntu", "centos", "rhel", "debian", "windows server",
    "macos", "unix",
}

# ---------------------------------------------------------------------------
# Certification patterns
# ---------------------------------------------------------------------------
CERT_PATTERNS: list[re.Pattern[str]] = [
    # AWS
    re.compile(r"aws\s+certified\s+[\w\s\-]+(?:associate|professional|specialty)", re.I),
    re.compile(r"aws\s+certified\s+cloud\s+practitioner", re.I),
    re.compile(r"aws\s+solutions?\s+architect", re.I),
    re.compile(r"aws\s+devops\s+engineer", re.I),
    re.compile(r"aws\s+developer\s+associate", re.I),
    re.compile(r"aws\s+sysops", re.I),
    re.compile(r"aws\s+security\s+specialty", re.I),
    re.compile(r"aws\s+machine\s+learning\s+specialty", re.I),
    # Azure
    re.compile(r"azure\s+(?:fundamentals|administrator|developer|architect|security|data|ai)\s*(?:associate|expert)?", re.I),
    re.compile(r"az-\d{3}", re.I),
    re.compile(r"microsoft\s+certified\s*:?\s*[\w\s\-]+", re.I),
    # GCP
    re.compile(r"google\s+cloud\s+(?:certified\s+)?(?:professional|associate)\s+[\w\s\-]+", re.I),
    re.compile(r"gcp\s+(?:professional|associate)\s+[\w\s\-]+", re.I),
    # Security certs
    re.compile(r"\bCISSP\b"),
    re.compile(r"\bCISM\b"),
    re.compile(r"\bCISA\b"),
    re.compile(r"\bCEH\b"),
    re.compile(r"\bOSCP\b"),
    re.compile(r"\bSecurity\+", re.I),
    re.compile(r"\bCompTIA\s+Security\+", re.I),
    re.compile(r"\bCompTIA\s+Network\+", re.I),
    re.compile(r"\bCompTIA\s+A\+", re.I),
    re.compile(r"\bCCSP\b"),
    re.compile(r"\bGSEC\b"),
    re.compile(r"\bGCIH\b"),
    # Kubernetes / cloud-native
    re.compile(r"\bCKA\b"),
    re.compile(r"\bCKAD\b"),
    re.compile(r"\bCKS\b"),
    re.compile(r"certified\s+kubernetes", re.I),
    # Terraform
    re.compile(r"hashicorp\s+certified\s*:?\s*[\w\s\-]+", re.I),
    re.compile(r"terraform\s+(?:associate|professional)", re.I),
    # Data / AI
    re.compile(r"\bCDP\b"),
    re.compile(r"\bCDE\b"),
    re.compile(r"databricks\s+certified", re.I),
    re.compile(r"snowflake\s+[\w\s]*cert", re.I),
    # PMP / ITIL
    re.compile(r"\bPMP\b"),
    re.compile(r"\bITIL\b"),
    re.compile(r"\bPrince2\b", re.I),
    re.compile(r"\bCSM\b"),  # Certified Scrum Master
    re.compile(r"\bSAFe\s+\d*\s*(?:agilist|practitioner|scrum master)?", re.I),
]

# ---------------------------------------------------------------------------
# Education patterns
# ---------------------------------------------------------------------------
_DEGREE_PATTERN = re.compile(
    r"(?:bachelor|master|ph\.?d|doctor|associate|mba|m\.?s\.?|b\.?s\.?|b\.?a\.?|m\.?a\.?|b\.?eng|m\.?eng)"
    r"(?:'?s?)?"
    r"(?:\s+(?:of|in)\s+[\w\s,&]+)?",
    re.I,
)

# ---------------------------------------------------------------------------
# Experience date range pattern
# ---------------------------------------------------------------------------
_DATE_RANGE_PATTERN = re.compile(
    r"(?:(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\w*[\s,]*)?(\d{4})"
    r"\s*[-\u2013\u2014to]+\s*"
    r"(?:(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\w*[\s,]*)?(\d{4}|present|current|now)",
    re.I,
)

_SECTION_HEADERS = re.compile(
    r"^[\s#*]*("
    r"experience|employment|work\s+history|professional\s+experience"
    r"|education|academic"
    r"|skills|technical\s+skills|core\s+competencies|technologies"
    r"|certifications?|licenses?\s*(?:&|and)?\s*certifications?"
    r"|projects|achievements|awards|publications|summary|objective|profile"
    r")[\s:]*$",
    re.I,
)


class ResumeParser:
    """Parse resumes from PDF, DOCX, or plain-text files."""

    SUPPORTED_EXTENSIONS: set[str] = {".pdf", ".docx", ".doc", ".txt", ".md"}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def parse(self, file_path: str) -> dict:
        """Parse a resume file and return structured data.

        Returns a dict with keys:
            name, email, phone, current_role, experience_years,
            companies, skills, certifications, education, raw_text
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Resume file not found: {file_path}")

        ext = path.suffix.lower()
        if ext not in self.SUPPORTED_EXTENSIONS:
            raise ValueError(
                f"Unsupported file type '{ext}'. "
                f"Supported: {', '.join(sorted(self.SUPPORTED_EXTENSIONS))}"
            )

        if ext == ".pdf":
            raw_text = self._parse_pdf(str(path))
        elif ext in {".docx", ".doc"}:
            raw_text = self._parse_docx(str(path))
        else:
            raw_text = self._parse_text(str(path))

        if not raw_text or not raw_text.strip():
            return {
                "name": None,
                "email": None,
                "phone": None,
                "current_role": None,
                "experience_years": 0,
                "companies": [],
                "skills": [],
                "certifications": [],
                "education": [],
                "raw_text": "",
            }

        return self._extract_structure(raw_text)

    # ------------------------------------------------------------------
    # File-type parsers
    # ------------------------------------------------------------------

    def _parse_pdf(self, path: str) -> str:
        """Extract text from a PDF file.

        Tries pdfplumber first, falls back to PyPDF2.
        """
        # Attempt 1: pdfplumber (best quality)
        try:
            import pdfplumber  # type: ignore[import-untyped]

            text_parts: list[str] = []
            with pdfplumber.open(path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
            if text_parts:
                return "\n".join(text_parts)
        except ImportError:
            pass
        except Exception:
            pass  # fall through to next method

        # Attempt 2: PyPDF2
        try:
            from PyPDF2 import PdfReader  # type: ignore[import-untyped]

            reader = PdfReader(path)
            text_parts = []
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
            if text_parts:
                return "\n".join(text_parts)
        except ImportError:
            pass
        except Exception:
            pass

        raise RuntimeError(
            "Could not extract text from PDF. "
            "Install a PDF library:\n"
            "  pip install pdfplumber   # recommended\n"
            "  pip install PyPDF2       # alternative"
        )

    def _parse_docx(self, path: str) -> str:
        """Extract text from a DOCX file using python-docx."""
        try:
            import docx  # type: ignore[import-untyped]

            doc = docx.Document(path)
            return "\n".join(para.text for para in doc.paragraphs if para.text.strip())
        except ImportError:
            raise RuntimeError(
                "Could not read DOCX file. Install python-docx:\n"
                "  pip install python-docx"
            )

    def _parse_text(self, path: str) -> str:
        """Read a plain-text or Markdown file."""
        p = Path(path)
        try:
            return p.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return p.read_text(encoding="latin-1")

    # ------------------------------------------------------------------
    # Structure extraction
    # ------------------------------------------------------------------

    def _extract_structure(self, raw_text: str) -> dict:
        """Extract structured resume fields from raw text."""
        lines = [ln.strip() for ln in raw_text.splitlines() if ln.strip()]

        name = self._extract_name(lines)
        email = self._extract_email(raw_text)
        phone = self._extract_phone(raw_text)
        skills = self._extract_skills(raw_text)
        certs = self._extract_certifications(raw_text)
        education = self._extract_education(raw_text)
        experience_years = self._estimate_experience_years(raw_text)
        companies, current_role = self._extract_companies_and_role(raw_text)

        return {
            "name": name,
            "email": email,
            "phone": phone,
            "current_role": current_role,
            "experience_years": experience_years,
            "companies": companies,
            "skills": skills,
            "certifications": certs,
            "education": education,
            "raw_text": raw_text,
        }

    # ------------------------------------------------------------------
    # Field extractors
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_name(lines: list[str]) -> str | None:
        """Guess the candidate name from the first non-trivial line."""
        for line in lines[:5]:
            # Skip lines that look like section headers, emails, URLs
            if _SECTION_HEADERS.match(line):
                continue
            if "@" in line or "http" in line.lower():
                continue
            if re.match(r"^[\d()+\-\s]+$", line):
                continue
            # A name line is typically short and mostly alphabetic
            cleaned = re.sub(r"[#*_\-|]", "", line).strip()
            if cleaned and len(cleaned) < 60 and re.search(r"[a-zA-Z]", cleaned):
                return cleaned
        return None

    @staticmethod
    def _extract_email(text: str) -> str | None:
        match = re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", text)
        return match.group(0) if match else None

    @staticmethod
    def _extract_phone(text: str) -> str | None:
        match = re.search(
            r"(?:\+?\d{1,3}[\s.-]?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}", text
        )
        return match.group(0) if match else None

    @staticmethod
    def _extract_skills(text: str) -> list[str]:
        """Extract technical skills via keyword matching against KNOWN_SKILLS."""
        text_lower = text.lower()
        found: list[str] = []
        for skill in sorted(KNOWN_SKILLS):
            # Word-boundary check to avoid false positives (e.g., "r" inside words)
            if len(skill) <= 2:
                pattern = rf"(?<![a-zA-Z]){re.escape(skill)}(?![a-zA-Z])"
            else:
                pattern = rf"\b{re.escape(skill)}\b"
            if re.search(pattern, text_lower):
                found.append(skill)
        return found

    @staticmethod
    def _extract_certifications(text: str) -> list[str]:
        """Extract certifications using predefined patterns."""
        certs: list[str] = []
        seen_lower: set[str] = set()
        for pat in CERT_PATTERNS:
            for match in pat.finditer(text):
                cert = match.group(0).strip()
                if cert.lower() not in seen_lower:
                    seen_lower.add(cert.lower())
                    certs.append(cert)
        return certs

    @staticmethod
    def _extract_education(text: str) -> list[str]:
        """Extract education entries."""
        results: list[str] = []
        seen: set[str] = set()
        for match in _DEGREE_PATTERN.finditer(text):
            deg = match.group(0).strip()
            if deg.lower() not in seen and len(deg) > 3:
                seen.add(deg.lower())
                results.append(deg)
        return results

    @staticmethod
    def _estimate_experience_years(text: str) -> int:
        """Estimate total years of professional experience from date ranges."""
        from datetime import datetime

        current_year = datetime.now().year
        total_years = 0

        for match in _DATE_RANGE_PATTERN.finditer(text):
            start_year = int(match.group(1))
            end_str = match.group(2).lower()
            end_year = current_year if end_str in {"present", "current", "now"} else int(end_str)

            # Basic sanity checks
            if 1970 <= start_year <= current_year and start_year <= end_year <= current_year + 1:
                total_years += end_year - start_year

        # Also try explicit "X years of experience" statements
        explicit = re.findall(r"(\d{1,2})\+?\s*years?\s+of\s+experience", text, re.I)
        if explicit:
            max_explicit = max(int(y) for y in explicit)
            total_years = max(total_years, max_explicit)

        return total_years

    @staticmethod
    def _extract_companies_and_role(text: str) -> tuple[list[str], str | None]:
        """Extract company names and the most recent role.

        This is heuristic-based: looks for lines that contain typical role
        keywords followed by company-like text, or lines between Experience
        section header and the next section.
        """
        companies: list[str] = []
        current_role: str | None = None

        role_keywords = re.compile(
            r"\b(engineer|developer|architect|manager|director|lead|analyst|consultant"
            r"|administrator|specialist|scientist|designer|coordinator|vp|cto|cio|ceo"
            r"|devops|sre|principal|staff|senior|junior|intern)\b",
            re.I,
        )

        lines = text.splitlines()
        in_experience = False

        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue

            # Detect experience section
            if re.match(
                r"^[\s#*]*(experience|employment|work\s+history|professional\s+experience)[\s:]*$",
                stripped,
                re.I,
            ):
                in_experience = True
                continue

            # Detect next section (exit experience)
            if in_experience and _SECTION_HEADERS.match(stripped):
                in_experience = False
                continue

            if in_experience and role_keywords.search(stripped):
                if current_role is None:
                    current_role = re.sub(r"[#*_]", "", stripped).strip()

            # Try to find "at Company" or "Company |" patterns
            at_match = re.search(r"\bat\s+([A-Z][\w\s&.,]+)", stripped)
            if at_match:
                company = at_match.group(1).strip().rstrip(",.")
                if company and company not in companies:
                    companies.append(company)

            pipe_match = re.search(r"[|,]\s*([A-Z][\w\s&.]+?)(?:\s*[|,]|\s*$)", stripped)
            if pipe_match and in_experience:
                company = pipe_match.group(1).strip().rstrip(",.")
                if company and len(company) > 2 and company not in companies:
                    companies.append(company)

        return companies, current_role
