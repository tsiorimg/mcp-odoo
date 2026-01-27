"""Simple retry decorator with exponential backoff."""

from __future__ import annotations

import time
from typing import Callable, Iterable, Type


def retry(
    attempts: int = 3,
    backoff: float = 0.3,
    exceptions: Iterable[Type[BaseException]] = (Exception,),
):
    """Decorator to retry a function on error.

    - attempts: total attempts
    - backoff: initial delay (exponential: backoff * 2**(n-1))
    - exceptions: exceptions that trigger a retry
    """

    def decorator(func: Callable):
        def wrapper(*args, **kwargs):
            last_exc: BaseException | None = None
            for attempt in range(1, attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as exc:  # type: ignore
                    last_exc = exc
                    if attempt == attempts:
                        raise
                    time.sleep(backoff * (2 ** (attempt - 1)))
            # Should not be reachable
            if last_exc:
                raise last_exc

        return wrapper

    return decorator
