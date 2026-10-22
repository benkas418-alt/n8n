"""Bearer-token check for write endpoints."""

import secrets

from fastapi import Header, HTTPException

from footintel.config import get_settings


def require_admin(authorization: str = Header(default="")) -> None:
    expected = get_settings().admin_token
    if expected is None or not expected.get_secret_value():
        raise HTTPException(503, "ADMIN_TOKEN is not configured: write endpoints are disabled")
    given = authorization.removeprefix("Bearer ").strip()
    if not secrets.compare_digest(given, expected.get_secret_value()):
        raise HTTPException(401, "invalid token")
