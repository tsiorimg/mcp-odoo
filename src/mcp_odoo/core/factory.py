"""Connector factory with Odoo version auto-detection."""

from __future__ import annotations

import httpx

from mcp_odoo.connectors.utils import is_json2, parse_version
from mcp_odoo.core.exceptions import VersionDetectionError
from mcp_odoo.utils.logging import get_logger

logger = get_logger(__name__)


def detect_odoo_version(url: str, timeout: float = 5.0) -> float:
    """Fetch Odoo version via `/web/version` (or fallback).

    Returns float like 17.0, raises VersionDetectionError on failure.
    """

    endpoints = ["/web/version", "/web/webclient/version_info"]
    last_error: Exception | None = None
    for suffix in endpoints:
        version_endpoint = url.rstrip("/") + suffix
        try:
            resp = httpx.get(version_endpoint, timeout=timeout)
            resp.raise_for_status()
            data = resp.json()
            version_str = data.get("server_version") or data.get("version")
            if not version_str and "server_version" not in data and "version" not in data:
                continue
            version = parse_version(str(version_str or data))
            logger.debug("detected_version", url=url, version=version, endpoint=suffix)
            return version
        except Exception as exc:  # httpx.HTTPError ou json.JSONDecodeError
            last_error = exc
            continue
    raise VersionDetectionError(f"Unable to detect Odoo version on {url}: {last_error}")


class ConnectorFactory:
    """Create the appropriate connector based on detected Odoo version."""

    @staticmethod
    def create(
        url: str,
        database: str,
        api_key: str,
        user: str = "admin",
        version: float | None = None,
        timeout: float = 10.0,
        retry_attempts: int = 3,
        retry_backoff: float = 0.3,
    ):
        # Deferred import to avoid circular dependencies
        from mcp_odoo.connectors.json2 import JSON2Connector
        from mcp_odoo.connectors.xmlrpc import XMLRPCConnector

        resolved_version = version or detect_odoo_version(url, timeout=timeout)
        if is_json2(resolved_version):
            return JSON2Connector(
                url=url,
                database=database,
                api_key=api_key,
                user=user,
                timeout=timeout,
                retry_attempts=retry_attempts,
                retry_backoff=retry_backoff,
            )
        return XMLRPCConnector(
            url=url,
            database=database,
            api_key=api_key,
            user=user,
            timeout=timeout,
            retry_attempts=retry_attempts,
            retry_backoff=retry_backoff,
        )


class MCPOdoo:
    """Simple facade for direct usage."""

    def __init__(
        self,
        url: str,
        database: str,
        api_key: str,
        user: str = "admin",
        version: float | None = None,
        timeout: float = 10.0,
        retry_attempts: int = 3,
        retry_backoff: float = 0.3,
    ):
        self.connector = ConnectorFactory.create(
            url=url,
            database=database,
            api_key=api_key,
            user=user,
            version=version,
            timeout=timeout,
            retry_attempts=retry_attempts,
            retry_backoff=retry_backoff,
        )

    def __getattr__(self, item):
        return getattr(self.connector, item)
