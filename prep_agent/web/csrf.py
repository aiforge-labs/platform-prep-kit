"""CSRF protection middleware for the web UI.

Uses the Synchronizer Token Pattern adapted for HTMX:
- Every response sets a signed ``csrf_token`` cookie.
- ``app.js`` configures HTMX to send it as an ``X-CSRF-Token`` header.
- This middleware validates the header on every mutating request.
"""

from __future__ import annotations

import os
import secrets

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from itsdangerous import URLSafeTimedSerializer, BadSignature

# Signing key — generated once per process lifetime.
_SECRET = os.environ.get("PREP_CSRF_SECRET", secrets.token_hex(32))
_SERIALIZER = URLSafeTimedSerializer(_SECRET)
_COOKIE_NAME = "csrf_token"
_HEADER_NAME = "x-csrf-token"
_TOKEN_MAX_AGE = 3600 * 4  # 4 hours

_SAFE_METHODS = frozenset({"GET", "HEAD", "OPTIONS"})


def _generate_token() -> str:
    """Create a new signed CSRF token."""
    raw = secrets.token_hex(16)
    return _SERIALIZER.dumps(raw)


def _validate_token(token: str) -> bool:
    """Return True if *token* is a valid, non-expired signed token."""
    try:
        _SERIALIZER.loads(token, max_age=_TOKEN_MAX_AGE)
        return True
    except (BadSignature, Exception):
        return False


class CSRFMiddleware(BaseHTTPMiddleware):
    """Starlette middleware that enforces CSRF tokens on mutating requests."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # --- Validate on mutating methods ---
        if request.method not in _SAFE_METHODS:
            header_token = request.headers.get(_HEADER_NAME, "")
            cookie_token = request.cookies.get(_COOKIE_NAME, "")

            if not header_token or not cookie_token:
                return Response("CSRF token missing", status_code=403)

            if header_token != cookie_token:
                return Response("CSRF token mismatch", status_code=403)

            if not _validate_token(cookie_token):
                return Response("CSRF token expired", status_code=403)

        response = await call_next(request)

        # --- Set / refresh token cookie on every response ---
        if _COOKIE_NAME not in request.cookies or request.method in _SAFE_METHODS:
            token = _generate_token()
            response.set_cookie(
                key=_COOKIE_NAME,
                value=token,
                httponly=False,   # JS needs to read it for HTMX
                samesite="strict",
                secure=False,    # localhost only
                max_age=_TOKEN_MAX_AGE,
                path="/",
            )

        return response
