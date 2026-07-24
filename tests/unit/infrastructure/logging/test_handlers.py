from __future__ import annotations

import logging
from pathlib import Path

import pytest

from shadow.config.models import LoggingSettings
from shadow.infrastructure.logging.errors import LoggingInitializationError
from shadow.infrastructure.logging.formatter import StructuredFormatter
from shadow.infrastructure.logging.handlers import LogHandler


def test_build_console_handler_returns_stream_handler() -> None:
    formatter = StructuredFormatter()
    handler = LogHandler.build_console_handler(formatter)
    assert isinstance(handler, logging.StreamHandler)
    assert handler.formatter is formatter


def test_build_file_handler_creates_log_directory(tmp_path: Path) -> None:
    log_dir = tmp_path / "nested" / "logs"
    settings = LoggingSettings(log_dir=str(log_dir), log_filename="shadow.log")
    formatter = StructuredFormatter()
    fallback = LogHandler.build_console_handler(formatter)

    handler = LogHandler.build_file_handler(settings, formatter, fallback=fallback)

    try:
        assert log_dir.is_dir()
        assert (log_dir / "shadow.log").exists() or handler is not None
    finally:
        handler.close()


def test_build_file_handler_raises_when_log_dir_is_a_file(tmp_path: Path) -> None:
    blocked_path = tmp_path / "not_a_dir"
    blocked_path.write_text("occupied")

    settings = LoggingSettings(log_dir=str(blocked_path))
    formatter = StructuredFormatter()
    fallback = LogHandler.build_console_handler(formatter)

    with pytest.raises(LoggingInitializationError):
        LogHandler.build_file_handler(settings, formatter, fallback=fallback)


def test_fallback_handler_receives_records_on_write_failure(tmp_path: Path) -> None:
    settings = LoggingSettings(log_dir=str(tmp_path), log_filename="shadow.log")
    formatter = StructuredFormatter()
    fallback = LogHandler.build_console_handler(formatter)
    handler = LogHandler.build_file_handler(settings, formatter, fallback=fallback)

    received: list[logging.LogRecord] = []
    fallback.emit = received.append  # type: ignore[assignment]

    record = logging.LogRecord("shadow", logging.INFO, __file__, 0, "msg", (), None)
    handler.handleError(record)  # simulate a runtime write failure

    try:
        assert received == [record]
    finally:
        handler.close()
