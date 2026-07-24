"""Logger Factory and Logging Manager.

`LoggingManager` is the only class other subsystems should import from
this package (see `shadow/infrastructure/logging/__init__.py`).
`LoggerFactory` is an internal collaborator responsible for creating and
caching per-component logger instances, per the LLD's Class Design:

    LoggingManager
    │
    ├── LoggerFactory
    ├── StructuredFormatter
    ├── LogHandler
    ├── ContextManager
    └── LogFilter
"""

from __future__ import annotations

import logging
import threading
from enum import Enum, auto

from shadow.config.models import LoggingSettings, LogLevel
from shadow.infrastructure.logging.errors import LoggingError, LoggingInitializationError
from shadow.infrastructure.logging.filters import SensitiveDataFilter
from shadow.infrastructure.logging.formatter import StructuredFormatter
from shadow.infrastructure.logging.handlers import LogHandler

_ROOT_LOGGER_NAME = "shadow"


class LoggingState(Enum):
    """The Logging System's lifecycle states, per the LLD's State Management section."""

    CREATED = auto()
    INITIALIZING = auto()
    RUNNING = auto()
    STOPPING = auto()
    STOPPED = auto()


class LoggerFactory:
    """Creates and caches per-component loggers, uniquely identified by component name."""

    def __init__(self, root_logger: logging.Logger) -> None:
        self._root_logger = root_logger
        self._lock = threading.Lock()
        self._loggers: dict[str, logging.Logger] = {}

    def get_logger(self, name: str | None = None) -> logging.Logger:
        """Return the logger for `name` (e.g. "kernel.bootstrap"), creating it on first use.

        A `None` or empty name returns the Shadow root logger itself.
        Logger creation is synchronized, per the LLD's Concurrency Model.
        """
        qualified = f"{_ROOT_LOGGER_NAME}.{name}" if name else _ROOT_LOGGER_NAME
        with self._lock:
            cached = self._loggers.get(qualified)
            if cached is not None:
                return cached
            logger = logging.getLogger(qualified)
            self._loggers[qualified] = logger
            return logger


class LoggingManager:
    """Coordinates initialization, logger creation, and shutdown of the Logging System.

    The single public entry point for the Logging System — every other
    subsystem obtains loggers through an instance of this class (or the
    module-level singleton exposed via
    `shadow.infrastructure.logging.get_logger()` / `initialize()`), never
    by calling Python's `logging` module directly (see the LLD's Scope).
    """

    def __init__(self) -> None:
        self._state = LoggingState.CREATED
        self._lock = threading.Lock()
        self._factory: LoggerFactory | None = None
        self._handlers: list[logging.Handler] = []
        self._root_logger = logging.getLogger(_ROOT_LOGGER_NAME)

    @property
    def state(self) -> LoggingState:
        return self._state

    def initialize(self, settings: LoggingSettings) -> None:
        """Build the formatter, handlers, and filters, then start the Logging System.

        Calling this more than once is a no-op after the first successful
        call — configuration is applied exactly once per process, the same
        way `ConfigurationManager.load()` is idempotent-safe.
        """
        with self._lock:
            if self._state in (LoggingState.RUNNING, LoggingState.INITIALIZING):
                return
            self._state = LoggingState.INITIALIZING
            try:
                self._configure(settings)
            except LoggingError:
                self._state = LoggingState.CREATED
                raise
            except Exception as exc:  # pragma: no cover - defensive
                self._state = LoggingState.CREATED
                raise LoggingInitializationError(str(exc)) from exc
            self._state = LoggingState.RUNNING

    def _configure(self, settings: LoggingSettings) -> None:
        formatter = StructuredFormatter(
            fmt=settings.format, timestamp_format=settings.timestamp_format
        )
        console_handler = LogHandler.build_console_handler(formatter)

        handlers: list[logging.Handler] = []
        if settings.console_enabled:
            handlers.append(console_handler)
        if settings.file_enabled:
            file_handler = LogHandler.build_file_handler(
                settings, formatter, fallback=console_handler
            )
            handlers.append(file_handler)
        if not handlers:
            # Never run fully silent. This configuration is technically valid
            # (both destinations disabled) but leaves the system unobservable,
            # so console output is kept as an unconditional last resort.
            handlers.append(console_handler)

        if settings.mask_sensitive_fields:
            sensitive_filter = SensitiveDataFilter()
            for handler in handlers:
                handler.addFilter(sensitive_filter)

        for existing in list(self._root_logger.handlers):
            self._root_logger.removeHandler(existing)
        for handler in handlers:
            self._root_logger.addHandler(handler)

        self._root_logger.setLevel(self._level_to_int(settings.level))
        self._root_logger.propagate = False

        self._handlers = handlers
        self._factory = LoggerFactory(self._root_logger)

    def get_logger(self, name: str | None = None) -> logging.Logger:
        """Return a logger for `name`.

        Initializes with default settings first if `initialize()` hasn't
        been called yet, mirroring `shadow.config.get_settings()`'s
        zero-config-startup behavior.
        """
        if self._factory is None:
            self.initialize(LoggingSettings())
        assert self._factory is not None  # narrows type after initialize()
        return self._factory.get_logger(name)

    def set_level(self, level: LogLevel | str, *, component: str | None = None) -> None:
        """Change the minimum emitted level at runtime, for the root logger or one component."""
        target = self.get_logger(component) if component else self._root_logger
        target.setLevel(self._level_to_int(level))

    def flush(self) -> None:
        """Flush all handlers. Handler flushing is serialized, per the Concurrency Model."""
        with self._lock:
            for handler in self._handlers:
                handler.flush()

    def shutdown(self) -> None:
        """Flush and close all handlers, then move to the Stopped state.

        Per the LLD, logging requests received after shutdown are ignored
        rather than raising — a shutting-down application logging one last
        line is normal, not an error.
        """
        with self._lock:
            if self._state in (LoggingState.STOPPED, LoggingState.STOPPING):
                return
            self._state = LoggingState.STOPPING
            for handler in self._handlers:
                try:
                    handler.flush()
                    handler.close()
                except Exception:  # noqa: BLE001 - shutdown must never raise
                    pass
                self._root_logger.removeHandler(handler)
            self._handlers = []
            self._factory = None
            self._state = LoggingState.STOPPED

    @staticmethod
    def _level_to_int(level: LogLevel | str) -> int:
        name = level.value if isinstance(level, LogLevel) else str(level)
        return int(getattr(logging, name.upper()))
