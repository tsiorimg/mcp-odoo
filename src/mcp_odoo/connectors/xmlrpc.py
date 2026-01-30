"""XML-RPC connector for Odoo 14-18."""

from __future__ import annotations

import xmlrpc.client
import ssl
from functools import lru_cache
from typing import Any, Iterable

from mcp_odoo.connectors.utils import ensure_ids, parse_version
from mcp_odoo.core.connector import OdooConnector
from mcp_odoo.core.exceptions import APIError, AuthenticationError
from mcp_odoo.utils.logging import get_logger

logger = get_logger(__name__)


class XMLRPCConnector(OdooConnector):
    def __init__(
        self,
        *args,
        retry_attempts: int = 3,
        retry_backoff: float = 0.3,
        version: float | None = None,
        **kwargs,
    ):
        verify = kwargs.pop("verify", True)
        super().__init__(*args, version=version, **kwargs)
        transport = None
        if self.url.startswith("https://"):
            if verify is False:
                context = ssl._create_unverified_context()
                transport = xmlrpc.client.SafeTransport(context=context)
            elif isinstance(verify, str):
                context = ssl.create_default_context(cafile=verify)
                transport = xmlrpc.client.SafeTransport(context=context)
        self.common = xmlrpc.client.ServerProxy(
            f"{self.url}/xmlrpc/2/common", allow_none=True, transport=transport
        )
        self.object = xmlrpc.client.ServerProxy(
            f"{self.url}/xmlrpc/2/object", allow_none=True, transport=transport
        )
        self.retry_attempts = retry_attempts
        self.retry_backoff = retry_backoff
        self._uid = self.common.authenticate(self.database, self.user, self.api_key, {})
        if not self._uid:
            raise AuthenticationError("XML-RPC authentication failed")
        self._version = self._provided_version if self._provided_version is not None else self._fetch_version()

    def _fetch_version(self) -> float:
        info = self.common.version()
        version_str = info.get("server_version") or info.get("version")
        return parse_version(version_str) if version_str else 0.0

    def version(self) -> float:
        return self._version

    def _execute_kw(self, model: str, method: str, args: list[Any], kwargs: dict | None = None):
        kwargs = kwargs or {}
        last_exc: Exception | None = None
        for attempt in range(1, self.retry_attempts + 1):
            try:
                return self.object.execute_kw(
                    self.database,
                    self._uid,
                    self.api_key,
                    model,
                    method,
                    args,
                    kwargs,
                )
            except xmlrpc.client.Fault as exc:
                last_exc = exc
                if attempt == self.retry_attempts:
                    raise APIError(exc.faultString) from exc
            if attempt < self.retry_attempts:
                import time

                time.sleep(self.retry_backoff * (2 ** (attempt - 1)))
        if last_exc:
            raise last_exc
        raise APIError("XML-RPC call failed")

    def search(self, model: str, domain: list[list] | list[tuple]) -> list[int]:
        return self._execute_kw(model, "search", [domain])

    def read(self, model: str, ids: Iterable[int], fields: list[str] | None = None) -> list[dict]:
        ids_list = ensure_ids(list(ids))
        kwargs = {"fields": fields} if fields else {}
        return self._execute_kw(model, "read", [ids_list], kwargs)

    def search_read(
        self, model: str, domain: list[list] | list[tuple], fields: list[str] | None = None
    ) -> list[dict]:
        kwargs = {"fields": fields} if fields else {}
        return self._execute_kw(model, "search_read", [domain], kwargs)

    def create(self, model: str, values: dict[str, Any]) -> int:
        return int(self._execute_kw(model, "create", [values]))

    def write(self, model: str, ids: Iterable[int], values: dict[str, Any]) -> bool:
        ids_list = ensure_ids(list(ids))
        return bool(self._execute_kw(model, "write", [ids_list, values]))

    def unlink(self, model: str, ids: Iterable[int]) -> bool:
        ids_list = ensure_ids(list(ids))
        return bool(self._execute_kw(model, "unlink", [ids_list]))

    def fields_get(self, model: str, attributes: list[str] | None = None) -> dict:
        attrs_key = tuple(attributes) if attributes else None
        return self._fields_get_cached(model, attrs_key)

    @lru_cache(maxsize=128)
    def _fields_get_cached(self, model: str, attrs_key: tuple[str, ...] | None) -> dict:
        kwargs = {"attributes": list(attrs_key)} if attrs_key else {}
        return self._execute_kw(model, "fields_get", [[], kwargs])

    def call_method(
        self, model: str, method: str, *args: Any, **kwargs: Any
    ) -> Any:
        return self._execute_kw(model, method, list(args), kwargs)
