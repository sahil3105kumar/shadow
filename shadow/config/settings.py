"""Configuration Registry, Export Manager, and the public ConfigurationManager.

`ConfigurationManager` is the only class other subsystems should import from
this package (see `shadow/config/__init__.py`). Everything else here is an
internal collaborator per the LLD's Class Design.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Literal

import yaml

from shadow.config.errors import ConfigError
from shadow.config.loader import ConfigurationLoader
from shadow.config.models import ApplicationSettings, ConfigurationSection
from shadow.config.validators import ConfigurationValidator

_REDACTED = "***REDACTED***"
_SENSITIVE_KEY_MARKERS = ("key", "secret", "password", "token", "credential")


class ConfigurationRegistry:
    """Holds the validated, immutable configuration tree and answers lookups."""

    def __init__(self, settings: ApplicationSettings) -> None:
        self._settings = settings

    @property
    def settings(self) -> ApplicationSettings:
        return self._settings

    def section(self, name: str) -> ConfigurationSection:
        """Return a named top-level section (e.g. "logging") as a `ConfigurationSection`."""
        if not hasattr(self._settings, name):
            raise KeyError(f"Unknown configuration section: {name!r}")
        value = getattr(self._settings, name)
        if hasattr(value, "model_dump"):
            values = value.model_dump()
        else:
            values = {name: value}
        return ConfigurationSection(name=name, values=values)

    def exists(self, dotted_key: str) -> bool:
        """Return whether a dotted key path (e.g. "logging.level") resolves to a value."""
        try:
            self._resolve(dotted_key)
            return True
        except (KeyError, AttributeError):
            return False

    def get(self, dotted_key: str, default: Any = None) -> Any:
        """Return the value at a dotted key path, or `default` if it doesn't exist."""
        try:
            return self._resolve(dotted_key)
        except (KeyError, AttributeError):
            return default

    def _resolve(self, dotted_key: str) -> Any:
        cursor: Any = self._settings
        for part in dotted_key.split("."):
            if hasattr(cursor, part):
                cursor = getattr(cursor, part)
            elif isinstance(cursor, dict) and part in cursor:
                cursor = cursor[part]
            else:
                raise KeyError(dotted_key)
        return cursor


class ExportManager:
    """Serializes configuration for export, redacting sensitive values."""

    def export(self, settings: ApplicationSettings, fmt: Literal["json", "yaml"] = "json") -> str:
        redacted = self._redact(settings.model_dump(mode="json"))
        if fmt == "json":
            return json.dumps(redacted, indent=2, sort_keys=True)
        if fmt == "yaml":
            return str(yaml.safe_dump(redacted, sort_keys=True))
        raise ValueError(f"Unsupported export format: {fmt!r}")

    def _redact(self, value: Any) -> Any:
        if isinstance(value, dict):
            return {
                key: (_REDACTED if self._is_sensitive_key(key) else self._redact(v))
                for key, v in value.items()
            }
        if isinstance(value, list):
            return [self._redact(item) for item in value]
        return value

    @staticmethod
    def _is_sensitive_key(key: str) -> bool:
        lowered = key.lower()
        return any(marker in lowered for marker in _SENSITIVE_KEY_MARKERS)


class ConfigurationManager:
    """The single public entry point for all configuration access.

    Every other subsystem retrieves configuration exclusively through an
    instance of this class (or the module-level singleton exposed via
    `shadow.config.get_settings()` / `get_manager()`), never by reading
    environment variables or config files directly.
    """

    def __init__(self, config_path: Path | str | None = None) -> None:
        self._config_path = config_path
        self._registry: ConfigurationRegistry | None = None
        self._frozen = False
        self._export_manager = ExportManager()

    def load(self) -> ApplicationSettings:
        """Load, validate, and freeze configuration. Idempotent-safe to call once at startup.

        Raises `ConfigError` (or a subclass) on any fatal error, which per
        the LLD must prevent the application from starting.
        """
        if self._frozen:
            return self._registry.settings  # type: ignore[union-attr]

        merged = ConfigurationLoader(self._config_path).load()
        settings = ConfigurationValidator().validate(merged)
        self._registry = ConfigurationRegistry(settings)
        self._frozen = True
        return settings

    def reload(self) -> ApplicationSettings:
        """Not supported in the current architecture.

        Live reload is a documented Future Extension. Configuration is
        frozen after startup by design (see LLD Concurrency Model), so this
        always raises rather than silently returning stale or re-loaded data.
        """
        raise NotImplementedError(
            "Live configuration reload is not supported. Configuration is frozen "
            "after startup by design; restart the process to pick up changes."
        )

    def get(self, dotted_key: str, default: Any = None) -> Any:
        return self._require_registry().get(dotted_key, default)

    def section(self, name: str) -> ConfigurationSection:
        return self._require_registry().section(name)

    def exists(self, dotted_key: str) -> bool:
        return self._require_registry().exists(dotted_key)

    def validate(self) -> bool:
        """Return True if configuration has been successfully loaded and validated."""
        return self._frozen

    def freeze(self) -> None:
        """No-op if already loaded; configuration is always frozen immediately after `load()`."""
        if not self._frozen:
            raise ConfigError("Cannot freeze configuration before it has been loaded.")

    def export(self, fmt: Literal["json", "yaml"] = "json") -> str:
        settings = self._require_registry().settings
        return self._export_manager.export(settings, fmt=fmt)

    @property
    def settings(self) -> ApplicationSettings:
        return self._require_registry().settings

    def _require_registry(self) -> ConfigurationRegistry:
        if self._registry is None:
            raise ConfigError("Configuration has not been loaded yet. Call load() first.")
        return self._registry
