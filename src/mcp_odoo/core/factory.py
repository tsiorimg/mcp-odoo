"""Connector factory with Odoo version auto-detection."""

from __future__ import annotations

import httpx
import os

from mcp_odoo.connectors.utils import is_json2, parse_version
from mcp_odoo.core.exceptions import VersionDetectionError
from mcp_odoo.utils.logging import get_logger

logger = get_logger(__name__)


def _env_ssl_verify() -> bool | str:
    val = os.getenv("MCP_SSL_VERIFY")
    if val is None:
        return True
    val = val.strip().lower()
    if val in {"0", "false", "no", "off"}:
        return False
    return val


def detect_odoo_version(url: str, timeout: float = 5.0) -> float:
    """Fetch Odoo version via `/web/version` (or fallback).

    Returns float like 17.0, raises VersionDetectionError on failure.
    """

    endpoints = ["/web/version", "/web/webclient/version_info"]
    last_error: Exception | None = None
    for suffix in endpoints:
        version_endpoint = url.rstrip("/") + suffix
        try:
            resp = httpx.get(version_endpoint, timeout=timeout, verify=_env_ssl_verify())
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
        api_key: str | None,
        password: str | None = None,
        user: str | None = None,
        version: float | None = None,
        timeout: float = 10.0,
        retry_attempts: int = 3,
        retry_backoff: float = 0.3,
        verify: bool | str | None = None,
    ):
        # Deferred import to avoid circular dependencies
        from mcp_odoo.connectors.json2 import JSON2Connector
        from mcp_odoo.connectors.xmlrpc import XMLRPCConnector

        resolved_version = version or detect_odoo_version(url, timeout=timeout)
        verify_flag = _env_ssl_verify() if verify is None else verify
        if is_json2(resolved_version):
            if not api_key:
                raise VersionDetectionError(
                    "Odoo >=19 detected: ODOO_API_KEY (api_key) is required for JSON-2 authentication"
                )
            return JSON2Connector(
                url=url,
                database=database,
                api_key=api_key,
                user=user or "",
                timeout=timeout,
                retry_attempts=retry_attempts,
                retry_backoff=retry_backoff,
                verify=verify_flag,
            )
        # XML-RPC (14-18): accept password or api_key fallback
        secret = password or api_key
        if not secret:
            raise VersionDetectionError("Odoo 14-18 detected: provide ODOO_PASSWORD or ODOO_API_KEY")
        if not user:
            raise VersionDetectionError("Odoo 14-18 detected: provide ODOO_USER")
        return XMLRPCConnector(
            url=url,
            database=database,
            api_key=secret,
            user=user,
            timeout=timeout,
            retry_attempts=retry_attempts,
            retry_backoff=retry_backoff,
            verify=verify_flag,
        )


class MCPOdoo:
    """Simple facade for direct usage."""

    def __init__(
        self,
        url: str,
        database: str,
        api_key: str | None = None,
        password: str | None = None,
        user: str | None = None,
        version: float | None = None,
        timeout: float = 10.0,
        retry_attempts: int = 3,
        retry_backoff: float = 0.3,
        verify: bool | str | None = None,
    ):
        self.connector = ConnectorFactory.create(
            url=url,
            database=database,
            api_key=api_key,
            password=password,
            user=user,
            version=version,
            timeout=timeout,
            retry_attempts=retry_attempts,
            retry_backoff=retry_backoff,
            verify=verify,
        )

    def __getattr__(self, item):
        return getattr(self.connector, item)
