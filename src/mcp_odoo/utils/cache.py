"""Simple cache utilities for metadata (placeholder)."""

from __future__ import annotations

from functools import lru_cache
from typing import Callable


def cached_fields_get(func: Callable):
    """Decorator to cache fields_get per model."""

    return lru_cache(maxsize=128)(func)
