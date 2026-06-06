# Testing guide

Reviewer + end-user smoke-test walkthrough for platform-prep-kit. Three levels of "fresh" — pick whichever matches how isolated your test needs to be.

| Level | What's fresh | Time | Use when |
|---|---|---|---|
| 1 | New terminal window, existing venv | ~2 min | Quick regression check after a change |
| 2 | Empty user workspace (`~/.prep`) | ~5 min | Simulate a first-time local install |
| 3 | Fresh Docker container | ~10 min | Clean-room review; security audit; launch-readiness check |

All three exercise the same surfaces. Level 3 is the most trustworthy because it has zero carry-over from your dev environment.

---

## Level 1 — Fresh terminal, local venv

```bash
cd /path/to/platform-prep-kit
source .venv/bin/activate
prep --version
prep --help          # `pack` should appear in the command list
```

### New surfaces to exercise

**Pack browsing** (the 12-week curriculum, readable through the CLI):

```bash
prep pack list                                   # available packs
prep pack show sre-to-platform-engineer          # pack README
prep pack weeks sre-to-platform-engineer         # 12-week index
prep pack week sre-to-platform-engineer 3        # read week 3
prep pack stories sre-to-platform-engineer       # STAR prompt categories
prep pack mocks sre-to-platform-engineer         # mock exercises
prep pack mock sre-to-platform-engineer 1        # mock 1 (by number)
```

**Pack → quiz bridge** (extracts the exact quiz command from any week):

```bash
prep pack week sre-to-platform-engineer 5 --quiz
# → prep quiz --topic iac-gitops --tag gitops

prep pack week sre-to-platform-engineer 9 --quiz
# → prep quiz --topic platform-engineer --tag multi-tenancy
```

**Tagged quiz** (178 questions across 4 banks, filterable by topic tag):

```bash
prep quiz --list                                 # all banks with counts
prep quiz --topic iac-gitops --list-tags         # tags in a bank
prep quiz --topic iac-gitops --tag gitops --num 3
# → interactive quiz, 3 random gitops questions from 22 tagged
#   Answer A/B/C/D for multiple choice;
#   type open answer + self-rate 1–5 for open questions
```

**Web UI** (FastAPI + HTMX dashboard):

```bash
prep serve --no-open
# → http://127.0.0.1:8080
# Ctrl+C to stop
```

---

## Level 2 — Fresh workspace (first-time-user simulation)

This tests the onboarding flow without polluting your existing `~/.prep`.

```bash
# Save existing state
mv ~/.prep ~/.prep.bak.$(date +%s) 2>/dev/null

# Onboarding paths — pick one
prep init --template cloud-security-lead         # pre-built role template
prep init --interactive                          # guided wizard
prep init --job-url "https://..." --resume ~/resume.pdf   # gap analysis

# Core commands on the fresh workspace
prep today
prep pack list
prep pack week sre-to-platform-engineer 1 --quiz
prep status

# Restore your previous state
rm -rf ~/.prep                                   # or archive as ~/.prep.testrun
mv ~/.prep.bak.* ~/.prep
```

---

## Level 3 — Fresh Docker container (clean-room)

The strongest signal for a security / launch-readiness review. Requires Docker daemon running (`open -a Docker` on macOS, wait for the whale icon to settle).

```bash
cd /path/to/platform-prep-kit
docker build -t platform-prep-kit:test .
# First build: 3–5 minutes. Subsequent builds: seconds (layer cache).
```

### Web UI in a detached container

```bash
docker run -d --name ppk-test -p 8080:8080 \
  -v ppk-test-data:/home/prep/.prep \
  platform-prep-kit:test

open http://localhost:8080                       # exercise the UI

# Logs
docker logs ppk-test

# Clean up
docker stop ppk-test && docker rm ppk-test
docker volume rm ppk-test-data
```

### One-shot CLI (no web UI)

```bash
docker run --rm platform-prep-kit:test pack list
docker run --rm platform-prep-kit:test pack week sre-to-platform-engineer 7
docker run --rm platform-prep-kit:test quiz --topic platform-engineer --list-tags
docker run --rm platform-prep-kit:test --help
```

### Verify security posture of the container

```bash
# Runs as non-root (uid 1000)?
docker exec ppk-test id
# Expected: uid=1000(prep) gid=1000(prep) groups=1000(prep)

# No unexpected outbound connections?
docker exec ppk-test sh -c \
  'ss -tan 2>/dev/null || netstat -tan 2>/dev/null' | grep -E "ESTAB|LISTEN"
# Expected: only the :8080 listener — no ESTABLISHED outbound connections
```

---

## Functionality review checklist

Run through Levels 1 or 2 and watch for:

- `prep pack list` shows at least one pack → path resolution works
- `prep pack week <pack> <n> --quiz` returns a non-empty `prep quiz ...` line → pack ↔ quiz wiring intact
- `prep quiz --topic <bank> --list-tags` lists tags with counts → quiz-bank schema honoured
- `prep quiz --topic <bank> --tag <tag> --num 3` returns 3 questions → tag filter works
- `prep serve --no-open` binds to :8080 without errors → web UI starts cleanly
- Web UI onboarding wizard completes to a generated plan → end-to-end flow green
- `prep --help` lists `pack` among the command groups → CLI registration works

### Red flags

- `prep pack list` shows no packs → `packs/` path resolution broken
- `--quiz` extractor returns empty → a week file's quiz command line got mangled
- `--tag <x>` returns 0 for a tag `--list-tags` advertised → tagging mismatch
- Web UI 500s on onboarding → regression in the web flow
- CLI errors with `ModuleNotFoundError` that aren't `mcp` → missing dep in install

The `mcp` module-not-found error in `tests/test_mcp_server.py` is pre-existing; install `pip install -e ".[mcp]"` to clear it or ignore it for functionality testing.

---

## Security review checklist

The project claims: *"Self-hosted interview prep — your resume and job history never leave your machine."* These checks verify the claim holds today.

| Check | How | Expected |
|---|---|---|
| No telemetry at startup | Fresh container, watch with `tcpdump` / Little Snitch / Lulu | Zero outbound traffic on `prep serve` startup |
| User-initiated network calls only | `grep -rn "requests\\|httpx\\|urllib\\|socket" prep_agent/ --include='*.py'` | Only 4 sites: `ai_bridge._ollama_session` (localhost:11434), `job_fetcher.fetch` (user URL), `update_cmd` (api.github.com, user-initiated), `quiz_cmd._handle_generate` (localhost Ollama) |
| Resume / job data stays local | Upload a resume via the web UI; check `~/.prep/` for its contents | File written to local workspace only |
| Container runs non-root | `docker exec <container> id` | `uid=1000(prep)` |
| Docker image lists only FOSS licenses | `docker inspect <image> \| grep -i license` | `MIT` |
| Secrets scan clean | `grep -rE "sk-[a-zA-Z0-9]{20,}\|AKIA[A-Z0-9]{16}" prep_agent/` | No hits |

### On external calls that do exist

These are all user-initiated, none are background phone-home:

- **`prep update`** — explicitly invoked. Fetches content updates from `api.github.com/repos/aiforge-labs/platform-prep-kit`. No user data sent.
- **`prep init --job-url <url>`** — fetches a job posting URL the user provided. User data is the URL they chose.
- **AI backends** — optional, user-configured:
  - Ollama: calls `http://localhost:11434` (local; doesn't leave the machine).
  - Claude Code / ChatGPT-paste / OpenAI / Cursor — each requires explicit user configuration via `prep` settings; no default calls.

If you add a new call site, document it here.

---

## Reporting issues

If a check fails:

1. Note the level (1 / 2 / 3), the command run, and the exact output.
2. Capture `prep --version` and platform details (`uname -a`).
3. Open an issue at the repo's issue tracker with the above.

For security findings specifically, see [`SECURITY.md`](../SECURITY.md) for the disclosure process.
