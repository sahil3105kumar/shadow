from __future__ import annotations

import logging

from shadow.config.models import LoggingSettings, LogLevel
from shadow.infrastructure.logging import get_logger, initialize, set_level, shutdown


def test_get_logger_without_initialize_still_works() -> None:
    logger = get_logger("kernel.bootstrap")
    assert isinstance(logger, logging.Logger)
    assert logger.name == "shadow.kernel.bootstrap"


def test_initialize_accepts_explicit_settings() -> None:
    initialize(LoggingSettings(level=LogLevel.DEBUG))
    logger = get_logger("plugins")
    assert logger.getEffectiveLevel() == logging.DEBUG


def test_set_level_is_reflected_on_new_loggers() -> None:
    initialize(LoggingSettings())
    set_level(LogLevel.ERROR)
    assert get_logger().getEffectiveLevel() == logging.ERROR


def test_shutdown_then_get_logger_does_not_raise() -> None:
    initialize(LoggingSettings())
    shutdown()
    logger = get_logger("kernel")  # should silently re-initialize, not raise
    assert isinstance(logger, logging.Logger)
