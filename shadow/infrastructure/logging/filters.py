"""Log filters.

Per the LLD, filters execute before formatting and handler dispatch, and
are responsible for level filtering, component filtering, sensitive-data
masking, and duplicate suppression. Filters never format or route
records — they only decide whether a record passes through, or redact
values within it.

All filters implement the standard library's `logging.Filter` interface
(a `filter(record) -> bool` method returning whether the record should be
emitted) so they compose with `logging.Handler.addFilter` and
`logging.Logger.addFilter` unmodified.
"""

from __future__ import annotations

import logging
import time
from typing import Any

_SENSITIVE_KEY_MARKERS = ("key", "secret", "password", "token", "credential")
_REDACTED = "***REDACTED***"


class LogFilter(logging.Filter):
    """Base class for all Shadow log filters. Exists to give every filter in this
    package a common, discoverable import path and base type."""


class LevelFilter(LogFilter):
    """Drops records below a minimum level, independent of the logger/handler's own level.

    Useful for per-component overrides where a handler's level should stay
    untouched but one noisy component needs to be quieted (or made more
    verbose than the rest of the system).
    """

    def __init__(self, min_level: int) -> None:
        super().__init__()
        self._min_level = min_level

    def filter(self, record: logging.LogRecord) -> bool:
        return record.levelno >= self._min_level


class ComponentFilter(LogFilter):
    """Only allows records from a specific component (logger name) or its children."""

    def __init__(self, component: str) -> None:
        super().__init__()
        self._component = component

    def filter(self, record: logging.LogRecord) -> bool:
        return record.name == self._component or record.name.startswith(f"{self._component}.")


class SensitiveDataFilter(LogFilter):
    """Redacts values of sensitive-looking keys in a record's metadata.

    Matches the same marker-based heuristic as the Configuration System's
    export redaction (`shadow.config.settings.ExportManager`) for
    consistency across the codebase: any key containing "key", "secret",
    "password", "token", or "credential" (case-insensitive) has its value
    replaced, at any nesting depth.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        metadata = getattr(record, "metadata", None)
        if isinstance(metadata, dict):
            record.metadata = self._redact(metadata)
        return True

    @classmethod
    def _redact(cls, value: Any) -> Any:
        if isinstance(value, dict):
            return {
                key: (_REDACTED if cls._is_sensitive_key(key) else cls._redact(v))
                for key, v in value.items()
            }
        if isinstance(value, list):
            return [cls._redact(item) for item in value]
        return value

    @staticmethod
    def _is_sensitive_key(key: str) -> bool:
        lowered = key.lower()
        return any(marker in lowered for marker in _SENSITIVE_KEY_MARKERS)


class DuplicateSuppressionFilter(LogFilter):
    """Suppresses exact-duplicate (logger, level, message) records within a time window.

    Guards against a noisy loop flooding a destination with the identical
    line thousands of times. This is duplicate collapsing, not a
    general-purpose rate limiter — distinct messages are never affected.
    """

    def __init__(self, window_seconds: float = 1.0) -> None:
        super().__init__()
        self._window_seconds = window_seconds
        self._last_seen: dict[tuple[str, int, str], float] = {}

    def filter(self, record: logging.LogRecord) -> bool:
        key = (record.name, record.levelno, record.getMessage())
        now = time.monotonic()
        last = self._last_seen.get(key)
        self._last_seen[key] = now
        if last is not None and (now - last) < self._window_seconds:
            return False
        return True
