"""Structured log formatting.

Converts `logging.LogRecord`s into JSON or console output. Every record
produced by the Logging System carries the same set of fields regardless
of output format (see the LLD's Data Models / example LogRecord), so JSON
and console output are two renderings of one underlying structure rather
than two independent formats — per the LLD's "structured logging by
default" design decision, logs are meant for both humans and machines.
"""

from __future__ import annotations

import json
import logging
import traceback
from typing import Any

from shadow.config.models import LogFormat
from shadow.infrastructure.logging.context import current_context

# Attributes every stdlib LogRecord carries. Anything else set on a record
# (via `logger.info(..., extra={...})`) is treated as caller-supplied metadata.
_RESERVED_RECORD_ATTRS = frozenset(
    logging.LogRecord(
        name="", level=0, pathname="", lineno=0, msg="", args=(), exc_info=None
    ).__dict__
) | {"message", "asctime", "metadata"}


class StructuredFormatter(logging.Formatter):
    """Renders `logging.LogRecord`s as structured JSON or human-readable console lines."""

    def __init__(
        self,
        fmt: LogFormat = LogFormat.JSON,
        timestamp_format: str | None = None,
    ) -> None:
        super().__init__(datefmt=timestamp_format)
        self._output_format = fmt

    def format(self, record: logging.LogRecord) -> str:
        payload = self._build_payload(record)
        if self._output_format == LogFormat.JSON:
            return json.dumps(payload, default=str, sort_keys=True)
        return self._render_console(payload)

    def _build_payload(self, record: logging.LogRecord) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "component": getattr(record, "component", record.name),
            "module": record.module,
            "thread": record.threadName,
            "context": current_context(),
        }
        metadata = self._extract_metadata(record)
        if metadata:
            payload["metadata"] = metadata
        if record.exc_info:
            payload["exception"] = "".join(traceback.format_exception(*record.exc_info))
        return payload

    @staticmethod
    def _extract_metadata(record: logging.LogRecord) -> dict[str, Any]:
        explicit = getattr(record, "metadata", None)
        extra = {
            key: value
            for key, value in record.__dict__.items()
            if key not in _RESERVED_RECORD_ATTRS
        }
        if isinstance(explicit, dict):
            extra.update(explicit)
        return extra

    @staticmethod
    def _render_console(payload: dict[str, Any]) -> str:
        line = (
            f"{payload['timestamp']} [{payload['level']:<8}] "
            f"{payload['logger']}: {payload['message']}"
        )

        bound_context = {k: v for k, v in payload.get("context", {}).items() if k != "thread_id"}
        if bound_context:
            fields = ", ".join(f"{k}={v}" for k, v in sorted(bound_context.items()))
            line += f" ({fields})"

        if payload.get("metadata"):
            line += f" | metadata={payload['metadata']}"

        if payload.get("exception"):
            line += f"\n{payload['exception']}"

        return line
