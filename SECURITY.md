# Security Policy

## Reporting a Vulnerability

**Do NOT open a public GitHub issue for security vulnerabilities.**

Please report security issues responsibly by emailing:

**gitaiforgelabs@gmail.com**

Include:
- Description of the vulnerability
- Steps to reproduce
- Impact assessment (what an attacker could do)
- Affected version(s)

We will acknowledge your report within **48 hours** and aim to provide a fix or mitigation plan within **7 days** for critical issues.

## Supported Versions

| Version | Supported |
|---------|-----------|
| 0.1.x   | Yes       |

## Security Design

Platform Prep Kit is designed as a **local-only, single-user tool**. Security decisions reflect this scope:

### Data Storage

- All user data is stored in `~/.prep/` on your local machine
- Data is **not encrypted at rest** — it is plain YAML, Markdown, JSON, and SQLite
- This is intentional: the tool is for personal use on your own machine
- **Never deploy this tool on a shared or multi-tenant server**

### Web UI (`prep serve`)

- Binds to `127.0.0.1` (localhost) by default — **not accessible from the network**
- If you use `--host 0.0.0.0`, a warning is displayed; this is **not recommended**
- CSRF protection is enabled on all mutating requests (signed tokens)
- Security headers are set: CSP, X-Frame-Options DENY, X-Content-Type-Options nosniff
- File uploads (resume parsing) are restricted to allowed extensions, 10MB max, and deleted after processing

### AI Integration

- AI provider calls are **explicit and user-initiated only**
- No telemetry, no analytics, no phone-home behavior
- If you configure an API key (e.g., OpenAI), it is stored in `~/.prep/config.yml` **unencrypted**
- For production API keys, consider using environment variables instead:
  ```bash
  export OPENAI_API_KEY="sk-..."
  ```

### Supply Chain

- Core dependencies: `click`, `pyyaml`, `rich`, `pydantic` (all widely audited)
- Web UI dependencies: `fastapi`, `uvicorn`, `jinja2`, `itsdangerous`, `markdown`
- All dependencies are MIT/BSD/Apache-2.0 licensed
- HTMX is vendored (not loaded from CDN) to prevent supply chain attacks
- No post-install scripts or build hooks

## What We Consider In-Scope

- Remote code execution via crafted quiz banks, templates, or knowledge packs
- Path traversal in file upload or knowledge pack rendering
- XSS in rendered markdown or template output
- CSRF bypass in the web UI
- Injection in SQLite queries
- Secrets leaked in logs or error messages

## What We Consider Out-of-Scope

- Attacks requiring local machine access (the tool stores data locally by design)
- Social engineering
- Denial of service against the local web server
- Issues in dependencies (report those upstream)

## Security Best Practices for Contributors

1. **Never use `eval()`, `exec()`, or `os.system()` with user input**
2. **Always use parameterized queries** for SQLite (never string formatting)
3. **Sanitize file paths** — use `pathlib` and reject path traversal (`..`)
4. **Escape HTML output** — Jinja2 autoescaping is enabled; never use `|safe` on user content
5. **Validate all form inputs** server-side, not just client-side
6. **Never commit secrets** — `.env`, API keys, credentials
