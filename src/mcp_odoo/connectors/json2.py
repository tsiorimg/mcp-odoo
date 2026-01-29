"""Connecteur JSON-2 pour Odoo 19+."""

from __future__ import annotations

import httpx
from functools import lru_cache
from typing import Any, Iterable

from mcp_odoo.connectors.utils import build_headers, ensure_ids, map_status_to_error
from mcp_odoo.core.connector import OdooConnector
from mcp_odoo.core.exceptions import APIError
from mcp_odoo.utils.logging import get_logger

logger = get_logger(__name__)


class JSON2Connector(OdooConnector):
    def __init__(
        self,
        *args,
        retry_attempts: int = 3,
        retry_backoff: float = 0.3,
        verify: bool | str = True,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self._client = httpx.Client(base_url=self.url, timeout=self.timeout, verify=verify)
        self._headers = build_headers(self.database, self.api_key)
        self.retry_attempts = retry_attempts
        self.retry_backoff = retry_backoff
        self._version = self._fetch_version()

    def _fetch_version(self) -> float:
        resp = self._client.get("/web/version")
        resp.raise_for_status()
        data = resp.json()
        version_str = data.get("server_version") or data.get("version") or "19.0"
        major_minor = version_str.split("+")[0]
        try:
            return float(".".join(major_minor.split(".")[:2]))
        except ValueError:
            return 19.0

    def version(self) -> float:
        return self._version

    def _request(self, model: str, method: str, payload: dict[str, Any] | None = None):
        payload = payload or {}
        url = f"/json/2/{model}/{method}"
        last_exc: Exception | None = None
        for attempt in range(1, self.retry_attempts + 1):
            try:
                resp = self._client.post(url, headers=self._headers, json=payload)
                if resp.status_code >= 400:
                    raise map_status_to_error(resp.status_code, resp.text)
                return resp.json()
            except httpx.HTTPError as exc:
                last_exc = exc
                logger.warning("json2_http_error", url=url, attempt=attempt, error=str(exc))
            except APIError as exc:
                # do not retry functional errors
                raise exc
            if attempt < self.retry_attempts:
                import time

                time.sleep(self.retry_backoff * (2 ** (attempt - 1)))
        if last_exc:
            raise last_exc
        raise APIError(f"Request failed {url}")

    def search(self, model: str, domain: list[list] | list[tuple]) -> list[int]:
        return list(self._request(model, "search", {"domain": domain}))

    def read(self, model: str, ids: Iterable[int], fields: list[str] | None = None) -> list[dict]:
        ids_list = ensure_ids(list(ids))
        payload = {"ids": ids_list}
        if fields:
            payload["fields"] = fields
        return list(self._request(model, "read", payload))

    def search_read(
        self, model: str, domain: list[list] | list[tuple], fields: list[str] | None = None
    ) -> list[dict]:
        payload = {"domain": domain}
        if fields:
            payload["fields"] = fields
        return list(self._request(model, "search_read", payload))

    def create(self, model: str, values: dict[str, Any]) -> int:
        # JSON-2 expects `vals_list` (list of dictionaries)
        result = self._request(model, "create", {"vals_list": [values]})
        # API often returns a list of IDs
        if isinstance(result, list):
            return int(result[0])
        return int(result)

    def write(self, model: str, ids: Iterable[int], values: dict[str, Any]) -> bool:
        ids_list = ensure_ids(list(ids))
        result = self._request(model, "write", {"ids": ids_list, "vals": values})
        return bool(result)

    def unlink(self, model: str, ids: Iterable[int]) -> bool:
        ids_list = ensure_ids(list(ids))
        result = self._request(model, "unlink", {"ids": ids_list})
        return bool(result)

    def fields_get(self, model: str, attributes: list[str] | None = None) -> dict:
        attrs_key = tuple(attributes) if attributes else None
        return self._fields_get_cached(model, attrs_key)

    @lru_cache(maxsize=128)
    def _fields_get_cached(self, model: str, attrs_key: tuple[str, ...] | None) -> dict:
        payload = {}
        if attrs_key:
            payload["attributes"] = list(attrs_key)
        return dict(self._request(model, "fields_get", payload))

    def call_method(
        self, model: str, method: str, *args: Any, **kwargs: Any
    ) -> Any:
        payload = {"args": args, "kwargs": kwargs}
        return self._request(model, method, payload)
