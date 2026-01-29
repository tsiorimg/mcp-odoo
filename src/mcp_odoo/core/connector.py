"""Unified interface for Odoo connectors."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Iterable


class OdooConnector(ABC):
    """Defines common operations supported by the different APIs."""

    def __init__(self, url: str, database: str, api_key: str, user: str, timeout: float = 10.0):
        self.url = url.rstrip("/")
        self.database = database
        self.api_key = api_key
        self.user = user
        self.timeout = timeout

    @abstractmethod
    def version(self) -> float:
        """Return server version as float (e.g., 17.0)."""

    # Basic CRUD
    @abstractmethod
    def search(self, model: str, domain: list[list] | list[tuple]) -> list[int]:
        ...

    @abstractmethod
    def read(self, model: str, ids: Iterable[int], fields: list[str] | None = None) -> list[dict]:
        ...

    @abstractmethod
    def search_read(
        self, model: str, domain: list[list] | list[tuple], fields: list[str] | None = None
    ) -> list[dict]:
        ...

    @abstractmethod
    def create(self, model: str, values: dict[str, Any]) -> int:
        ...

    @abstractmethod
    def write(self, model: str, ids: Iterable[int], values: dict[str, Any]) -> bool:
        ...

    @abstractmethod
    def unlink(self, model: str, ids: Iterable[int]) -> bool:
        ...

    # Introspection
    @abstractmethod
    def fields_get(self, model: str, attributes: list[str] | None = None) -> dict:
        ...

    # Custom method invocation
    @abstractmethod
    def call_method(
        self, model: str, method: str, *args: Any, **kwargs: Any
    ) -> Any:
        ...
