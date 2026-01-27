"""Minimal structured logging configuration."""

from __future__ import annotations

import logging
import structlog


def configure_logging(level: int = logging.INFO) -> None:
    """Configure structlog with a simple format for CLI and tests."""

    logging.basicConfig(
        level=level,
        format="%(message)s",
    )
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.TimeStamper(fmt="ISO"),
            structlog.processors.add_log_level,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(level),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    """Return a ready-to-use structlog logger."""

    return structlog.get_logger(name)
