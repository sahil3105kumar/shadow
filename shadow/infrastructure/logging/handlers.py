"""Log handlers: route formatted records to their destinations.

Per the LLD, Console and File handlers are in scope now; Syslog, HTTP,
OpenTelemetry, and Cloud Logging handlers are documented Future
Extensions and are not implemented here.
"""

from __future__ import annotations

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Any

from shadow.config.models import LoggingSettings
from shadow.infrastructure.logging.errors import LoggingInitializationError
from shadow.infrastructure.logging.formatter import StructuredFormatter


class _FallbackRotatingFileHandler(logging.handlers.RotatingFileHandler):
    """A `RotatingFileHandler` that routes runtime write failures to a fallback
    handler instead of printing a traceback to stderr.

    Per the LLD's Error Handling section, handler failures at runtime
    (e.g. the disk filling up mid-run) are recoverable and "failures fall
    back to console logging". Only the write itself is fallback-protected;
    failures at construction time remain fatal — see `build_file_handler`.
    """

    def __init__(self, *args: Any, fallback: logging.Handler, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._fallback = fallback

    def handleError(self, record: logging.LogRecord) -> None:
        try:
            self._fallback.emit(record)
        except Exception:  # noqa: BLE001 - a failing fallback must never raise further
            pass


class LogHandler:
    """Namespace of handler-construction helpers. Not instantiated directly —
    every method here is a `staticmethod` factory, per the LLD's Log Handlers
    component."""

    @staticmethod
    def build_console_handler(formatter: StructuredFormatter) -> logging.Handler:
        """Build the console (stderr) handler.

        Also used as the fallback destination when the file handler fails
        at runtime, per `_FallbackRotatingFileHandler`.
        """
        handler = logging.StreamHandler(stream=sys.stderr)
        handler.setFormatter(formatter)
        return handler

    @staticmethod
    def build_file_handler(
        settings: LoggingSettings,
        formatter: StructuredFormatter,
        fallback: logging.Handler,
    ) -> logging.Handler:
        """Build a rotating file handler for `settings.log_dir`/`settings.log_filename`.

        Directory-creation and file-open failures are treated as fatal at
        initialization time — per the LLD, "invalid logging configuration"
        is a fatal error, so a broken log path stops startup the same way
        a broken configuration file does (see `ConfigurationValidator`).
        Failures *after* initialization instead fall back to `fallback`
        via `_FallbackRotatingFileHandler`.
        """
        log_dir = Path(settings.log_dir)
        try:
            log_dir.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            raise LoggingInitializationError(
                f"Could not create log directory {log_dir}: {exc}"
            ) from exc

        if log_dir.exists() and not log_dir.is_dir():
            raise LoggingInitializationError(f"Log path {log_dir} exists and is not a directory")

        path = log_dir / settings.log_filename
        try:
            handler = _FallbackRotatingFileHandler(
                path,
                maxBytes=settings.max_bytes,
                backupCount=settings.backup_count,
                encoding="utf-8",
                fallback=fallback,
            )
        except OSError as exc:
            raise LoggingInitializationError(f"Could not open log file {path}: {exc}") from exc

        handler.setFormatter(formatter)
        return handler
