from __future__ import annotations

import logging
from pathlib import Path

import pytest

from shadow.config.models import LogFormat, LoggingSettings, LogLevel
from shadow.infrastructure.logging.errors import LoggingInitializationError
from shadow.infrastructure.logging.factory import LoggingManager, LoggingState


def test_initial_state_is_created() -> None:
    manager = LoggingManager()
    assert manager.state == LoggingState.CREATED


def test_initialize_moves_to_running() -> None:
    manager = LoggingManager()
    manager.initialize(LoggingSettings())
    assert manager.state == LoggingState.RUNNING


def test_initialize_is_idempotent() -> None:
    manager = LoggingManager()
    manager.initialize(LoggingSettings())
    first_handlers = list(manager._handlers)

    manager.initialize(LoggingSettings(level=LogLevel.DEBUG))  # should be ignored

    assert manager._handlers == first_handlers


def test_get_logger_auto_initializes_with_defaults() -> None:
    manager = LoggingManager()
    logger = manager.get_logger("kernel.bootstrap")
    assert manager.state == LoggingState.RUNNING
    assert logger.name == "shadow.kernel.bootstrap"


def test_get_logger_caches_the_same_instance() -> None:
    manager = LoggingManager()
    first = manager.get_logger("kernel.bootstrap")
    second = manager.get_logger("kernel.bootstrap")
    assert first is second


def test_set_level_changes_root_logger_level() -> None:
    manager = LoggingManager()
    manager.initialize(LoggingSettings())
    manager.set_level(LogLevel.DEBUG)
    assert manager._root_logger.level == logging.DEBUG


def test_set_level_can_target_a_single_component() -> None:
    manager = LoggingManager()
    manager.initialize(LoggingSettings())
    manager.set_level(LogLevel.DEBUG, component="kernel.bootstrap")

    component_logger = manager.get_logger("kernel.bootstrap")
    assert component_logger.level == logging.DEBUG
    assert manager._root_logger.level != logging.DEBUG


def test_shutdown_moves_to_stopped_and_removes_handlers() -> None:
    manager = LoggingManager()
    manager.initialize(LoggingSettings())

    manager.shutdown()

    assert manager.state == LoggingState.STOPPED
    assert manager._root_logger.handlers == []


def test_shutdown_is_idempotent() -> None:
    manager = LoggingManager()
    manager.initialize(LoggingSettings())
    manager.shutdown()
    manager.shutdown()  # must not raise
    assert manager.state == LoggingState.STOPPED


def test_flush_does_not_raise_when_not_initialized() -> None:
    manager = LoggingManager()
    manager.flush()  # no handlers yet, must be a no-op


def test_initialize_raises_and_reverts_state_on_bad_log_dir(tmp_path: Path) -> None:
    blocked_path = tmp_path / "occupied"
    blocked_path.write_text("not a directory")

    manager = LoggingManager()
    settings = LoggingSettings(file_enabled=True, log_dir=str(blocked_path))

    with pytest.raises(LoggingInitializationError):
        manager.initialize(settings)

    assert manager.state == LoggingState.CREATED


def test_file_enabled_writes_json_lines_to_disk(tmp_path: Path) -> None:
    manager = LoggingManager()
    settings = LoggingSettings(
        file_enabled=True,
        console_enabled=False,
        log_dir=str(tmp_path),
        log_filename="shadow.log",
        format=LogFormat.JSON,
    )
    manager.initialize(settings)

    logger = manager.get_logger("kernel")
    logger.info("hello from the kernel")
    manager.flush()

    log_file = tmp_path / "shadow.log"
    assert log_file.exists()
    contents = log_file.read_text(encoding="utf-8")
    assert "hello from the kernel" in contents

    manager.shutdown()


def test_sensitive_fields_are_masked_end_to_end(tmp_path: Path) -> None:
    manager = LoggingManager()
    settings = LoggingSettings(
        file_enabled=True,
        console_enabled=False,
        log_dir=str(tmp_path),
        log_filename="shadow.log",
        mask_sensitive_fields=True,
    )
    manager.initialize(settings)

    logger = manager.get_logger("auth")
    logger.info("login attempt", extra={"metadata": {"password": "hunter2"}})
    manager.flush()
    manager.shutdown()

    contents = (tmp_path / "shadow.log").read_text(encoding="utf-8")
    assert "hunter2" not in contents
    assert "REDACTED" in contents
