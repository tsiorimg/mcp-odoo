"""Custom exceptions for MCP Odoo."""

from __future__ import annotations


class MCPError(Exception):
    """Generic MCP Odoo connector error."""


class VersionDetectionError(MCPError):
    """Unable to detect remote Odoo version."""


class AuthenticationError(MCPError):
    """Authentication error when connecting to Odoo."""


class APIError(MCPError):
    """Error returned by Odoo API (XML-RPC or JSON-2)."""

    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


class NotFoundError(APIError):
    """Resource not found (HTTP 404 or equivalent)."""


class ValidationError(APIError):
    """Invalid data or malformed request (HTTP 400)."""


class RateLimitError(APIError):
    """Rate limit / quota exceeded (HTTP 429)."""


class ServerError(APIError):
    """Server-side error from Odoo (>=500)."""
