"""Configuration System.

The Configuration System is the single source of truth for every
configurable aspect of the Shadow runtime. No other subsystem reads
environment variables or configuration files directly (see
`docs/architecture/lld/infrastructure/configuration.md`, Scope).

Typical usage, once at startup:

    from shadow.config import get_settings

    settings = get_settings()
    settings.logging.level

Testing or advanced use may construct a `ConfigurationManager` directly
instead of using the process-wide singleton.
"""

from __future__ import annotations

from pathlib import Path

from shadow.config.errors import ConfigError, ConfigLoadError, ConfigValidationError
from shadow.config.models import (
    ApplicationSettings,
    ConfigurationMetadata,
    ConfigurationSection,
    ConfigurationValue,
    KernelSettings,
    LoggingSettings,
    PluginSettings,
    SchedulerSettings,
    SecuritySettings,
)
from shadow.config.settings import ConfigurationManager

__all__ = [
    "ApplicationSettings",
    "ConfigError",
    "ConfigLoadError",
    "ConfigValidationError",
    "ConfigurationManager",
    "ConfigurationMetadata",
    "ConfigurationSection",
    "ConfigurationValue",
    "KernelSettings",
    "LoggingSettings",
    "PluginSettings",
    "SchedulerSettings",
    "SecuritySettings",
    "get_manager",
    "get_settings",
]

_manager: ConfigurationManager | None = None


def get_manager(config_path: Path | str | None = None) -> ConfigurationManager:
    """Return the process-wide `ConfigurationManager`, loading it on first call.

    Subsequent calls return the same frozen instance regardless of arguments
    passed — configuration is loaded exactly once per process. Pass
    `config_path` explicitly only on the very first call (e.g. from the CLI
    entry point); later calls elsewhere in the codebase should use
    `get_manager()` with no arguments.
    """
    global _manager
    if _manager is None:
        _manager = ConfigurationManager(config_path)
        _manager.load()
    return _manager


def get_settings() -> ApplicationSettings:
    """Return the process-wide, validated `ApplicationSettings`."""
    return get_manager().settings


def _reset_for_testing() -> None:
    """Reset the process-wide singleton. For test suites only — not part of the public API."""
    global _manager
    _manager = None
