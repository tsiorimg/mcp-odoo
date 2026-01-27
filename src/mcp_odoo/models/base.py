"""Types utilitaires pour domaines et champs."""

from __future__ import annotations

from typing import Any, Literal, TypedDict

DomainOperator = Literal["=", "!=", ">", "<", ">=", "<=", "in", "not in", "like", "ilike"]
Domain = list[tuple[str, DomainOperator, Any]]


class FieldInfo(TypedDict, total=False):
    string: str
    type: str
    help: str
    readonly: bool
    required: bool
    selection: list[tuple[str, str]]
