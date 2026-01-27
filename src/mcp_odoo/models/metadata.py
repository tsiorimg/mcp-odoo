"""Typed models for ir.model and ir.model.fields."""

from __future__ import annotations

from typing import TypedDict


class IRModel(TypedDict):
    id: int
    name: str
    model: str
    state: str


class IRModelField(TypedDict):
    id: int
    name: str
    field_description: str
    ttype: str
    model_id: int
