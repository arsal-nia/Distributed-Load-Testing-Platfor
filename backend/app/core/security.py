from fastapi import Header, HTTPException, status
from urllib.parse import urlparse

from app.core.config import settings


async def verify_token(authorization: str = Header(default="")) -> None:
    """
    FastAPI dependency that validates Bearer token if auth is enabled.

    If API_TOKEN is empty, auth is disabled and this is a no-op.
    """
    if not settings.auth_enabled:
        return

    expected = f"Bearer {settings.api_token.strip()}"

    if not authorization or authorization != expected:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )


def validate_target_url(url: str) -> str:
    """
    Enforce that the URL uses http/https and hostname is in the allowlist.
    Raises ValueError if invalid (FastAPI will convert to 422).
    """
    parsed = urlparse(url)

    if parsed.scheme not in ("http", "https"):
        raise ValueError(f"Only http/https URLs allowed, got scheme '{parsed.scheme}'")

    if not parsed.hostname:
        raise ValueError("URL must include a hostname")

    hostname = parsed.hostname.lower()
    allowed = settings.allowed_hosts_list

    if hostname not in allowed:
        raise ValueError(
            f"Hostname '{hostname}' not in allowlist. "
            f"Allowed: {', '.join(allowed)}. "
            f"Set ALLOWED_TARGET_HOSTS env var to override."
        )

    return url
