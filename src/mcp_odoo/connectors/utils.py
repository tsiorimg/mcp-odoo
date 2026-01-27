"""Utilitaires communs aux connecteurs."""

from __future__ import annotations

from typing import Any


def parse_version(version_str: str) -> float:
    """Convert an Odoo version string to float.

    Examples: "17.0" -> 17.0, "19.1+e" -> 19.1, "19.0-20260118" -> 19.0
    """

    clean = version_str.strip().split("+")[0].split("-")[0]
    parts = clean.split(".")
    try:
        major = int(parts[0])
        minor = int(parts[1]) if len(parts) > 1 else 0
        return float(f"{major}.{minor}")
    except (ValueError, IndexError):
        raise ValueError(f"Version Odoo invalide: {version_str}") from None


def is_json2(version: float) -> bool:
    return version >= 19.0


def build_headers(database: str, api_key: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {api_key}",
        "X-Odoo-Database": database,
        "Content-Type": "application/json",
    }


def ensure_ids(ids: list[int]) -> list[int]:
    if not all(isinstance(i, int) for i in ids):
        raise ValueError("IDs must be integers")
    return ids


def to_kwargs(payload: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in payload.items() if v is not None}


def map_status_to_error(status_code: int, message: str) -> Exception:
    """Map HTTP status to the appropriate API exception."""
    from mcp_odoo.core.exceptions import (
        APIError,
        AuthenticationError,
        NotFoundError,
        RateLimitError,
        ServerError,
        ValidationError,
    )

    if status_code in (401, 403):
        return AuthenticationError(message)
    if status_code == 404:
        return NotFoundError(message, status_code=status_code)
    if status_code == 400:
        return ValidationError(message, status_code=status_code)
    if status_code == 429:
        return RateLimitError(message, status_code=status_code)
    if status_code >= 500:
        return ServerError(message, status_code=status_code)
    return APIError(message, status_code=status_code)
