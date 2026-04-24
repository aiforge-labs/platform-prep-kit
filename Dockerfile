# syntax=docker/dockerfile:1.7

# ------------------------------------------------------------
# platform-prep-kit — self-hosted interview prep, Docker build
# ------------------------------------------------------------
#
# Build:   docker build -t platform-prep-kit .
# Run UI:  docker run -p 8080:8080 -v prep-data:/home/prep/.prep platform-prep-kit
# Run CLI: docker run --rm -v $(pwd):/workspace platform-prep-kit prep --help
#
# Data persistence: the user's workspace lives at /home/prep/.prep inside
# the container. Mount a named volume (or a host path) to keep study
# history, quiz results, and plans across runs.

FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# System deps: curl for the healthcheck, tini for proper signal handling.
# Everything else comes from pip wheels on Python 3.12-slim.
RUN apt-get update && apt-get install -y --no-install-recommends \
        curl \
        tini \
    && rm -rf /var/lib/apt/lists/*

# ------------------------------------------------------------
# Dependency layer — cached when pyproject.toml is unchanged
# ------------------------------------------------------------
WORKDIR /app

# Copy only the build metadata first so changes to source code don't bust
# the dependency cache.
COPY pyproject.toml README.md LICENSE ./

# Install the project with the UI extras. The web dashboard is the default
# mode for Docker; ".[all]" is available if you rebuild with --build-arg.
ARG EXTRAS=ui
RUN pip install --upgrade pip \
    && pip install ".[${EXTRAS}]"

# ------------------------------------------------------------
# Application layer
# ------------------------------------------------------------
# Copy the source last so editing application code doesn't reinstall deps.
COPY prep_agent/ ./prep_agent/
COPY knowledge_packs/ ./knowledge_packs/
COPY quiz_banks/ ./quiz_banks/
COPY project_templates/ ./project_templates/
COPY templates/ ./templates/
COPY packs/ ./packs/

# Re-install editable-style so the copied package directory is picked up.
# This is cheap because deps are already installed above.
RUN pip install --no-deps -e .

# ------------------------------------------------------------
# Non-root user
# ------------------------------------------------------------
RUN groupadd --system --gid 1000 prep \
    && useradd  --system --uid 1000 --gid prep --home /home/prep --shell /bin/bash prep \
    && mkdir -p /home/prep/.prep \
    && chown -R prep:prep /home/prep

USER prep
WORKDIR /home/prep
ENV HOME=/home/prep

# Expose the default web UI port.
EXPOSE 8080

# Health check targets the web UI's root. If a user runs the CLI only
# (with an override command), Docker will still probe but the worst
# effect is "unhealthy" status — the container still runs.
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD curl -fsS http://localhost:8080/ > /dev/null || exit 1

# tini handles PID 1 correctly (forwards signals, reaps zombies).
ENTRYPOINT ["/usr/bin/tini", "--", "prep"]

# Default: serve the web UI bound to all interfaces. --no-open prevents
# the CLI from trying to launch a (non-existent) browser inside the container.
# Override with e.g.  docker run ... platform-prep-kit quiz --list
CMD ["serve", "--host", "0.0.0.0", "--port", "8080", "--no-open"]
