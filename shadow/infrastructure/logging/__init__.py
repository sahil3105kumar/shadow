"""Logging System.

The Logging System is the single source of truth for all diagnostic
output produced by the Shadow runtime. No other subsystem configures its
own handlers or formatters, or calls Python's `logging` module directly
(see `docs/architecture/lld/infrastructure/logging.md`, Scope).

Typical usage, once at startup:

    from shadow.config import get_settings
    from shadow.infrastructure.logging import initialize, get_logger

    initialize(get_settings().logging)
    logger = get_logger("kernel.bootstrap")
    logger.info("Kernel starting")

Contextual metadata (request IDs, job IDs, ...) is attached to every log
record automatically once bound via `bind_context` — see
`shadow.infrastructure.logging.context`.
"""

from __future__ import annotations

import logging

from shadow.config.models import LoggingSettings, LogLevel
from shadow.infrastructure.logging.context import LogContext, bind_context, current_context
from shadow.infrastructure.logging.errors import (
    LoggingConfigurationError,
    LoggingError,
    LoggingInitializationError,
)
from shadow.infrastructure.logging.factory import LoggerFactory, LoggingManager, LoggingState
from shadow.infrastructure.logging.filters import (
    ComponentFilter,
    DuplicateSuppressionFilter,
    LevelFilter,
    LogFilter,
    SensitiveDataFilter,
)
from shadow.infrastructure.logging.formatter import StructuredFormatter
from shadow.infrastructure.logging.handlers import LogHandler

__all__ = [
    "ComponentFilter",
    "DuplicateSuppressionFilter",
    "LevelFilter",
    "LogContext",
    "LogFilter",
    "LogHandler",
    "LoggerFactory",
    "LoggingConfigurationError",
    "LoggingError",
    "LoggingInitializationError",
    "LoggingManager",
    "LoggingState",
    "SensitiveDataFilter",
    "StructuredFormatter",
    "bind_context",
    "current_context",
    "flush",
    "get_logger",
    "initialize",
    "set_level",
    "shutdown",
]

_manager = LoggingManager()


def initialize(settings: LoggingSettings | None = None) -> None:
    """Initialize the process-wide Logging System.

    A no-op after the first successful call. Pass `settings` explicitly at
    the real startup call site (typically `initialize(get_settings().logging)`
    right after the Configuration System loads); later calls elsewhere in
    the codebase can omit it entirely.
    """
    _manager.initialize(settings if settings is not None else LoggingSettings())


def get_logger(name: str | None = None) -> logging.Logger:
    """Return the logger for `name` (e.g. "kernel.bootstrap").

    Initializes the Logging System with default settings first if
    `initialize()` hasn't been called yet, so importing this and calling
    `get_logger(__name__)` always works even before startup wiring runs.
    """
    return _manager.get_logger(name)


def set_level(level: LogLevel | str, *, component: str | None = None) -> None:
    """Change the minimum emitted level at runtime, for the root logger or one component."""
    _manager.set_level(level, component=component)


def flush() -> None:
    """Flush all log handlers."""
    _manager.flush()


def shutdown() -> None:
    """Flush and close all log handlers. Requests after this call are silently ignored."""
    _manager.shutdown()


def _reset_for_testing() -> None:
    """Reset the process-wide singleton. For test suites only — not part of the public API."""
    global _manager
    _manager.shutdown()
    _manager = LoggingManager()
