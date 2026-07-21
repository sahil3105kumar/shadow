"""Configuration providers.

Each provider loads configuration from exactly one source and returns a
plain nested dict. Providers never validate — that is the Configuration
Validator's job (see `validators.py`) — and never merge each other's output
— that is the Configuration Loader's job (see `loader.py`).

Per the LLD: Default Provider, YAML Provider, and Environment Provider are
in scope now. Remote/Vault/Database providers are documented Future
Extensions and are not implemented here.
"""

from __future__ import annotations

import os
import re
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

import yaml

from shadow.config.defaults import default_config
from shadow.config.errors import ConfigLoadError

_ENV_PREFIX = "SHADOW_"
_ENV_NESTED_DELIMITER = "__"


class ConfigurationProvider(ABC):
    """Base class for all configuration sources."""

    @abstractmethod
    def load(self) -> dict[str, Any]:
        """Return this provider's configuration as a nested dict.

        Must never raise for "no configuration found" — an empty dict is the
        correct return value in that case. Providers only raise for actual
        read/parse failures (see `ConfigLoadError`).
        """


class DefaultProvider(ConfigurationProvider):
    """Lowest-precedence provider: the built-in defaults."""

    def load(self) -> dict[str, Any]:
        return default_config()


class YamlProvider(ConfigurationProvider):
    """Loads configuration from a YAML file.

    A missing file is not an error — Shadow must start with zero config
    present, using defaults and environment variables only. A file that
    exists but fails to parse *is* an error, since that's very likely a
    typo the person would want to know about immediately rather than have
    silently ignored.
    """

    def __init__(self, path: Path | str | None) -> None:
        self._path = Path(path) if path is not None else None

    def load(self) -> dict[str, Any]:
        if self._path is None or not self._path.exists():
            return {}

        try:
            raw = self._path.read_text(encoding="utf-8")
        except OSError as exc:
            raise ConfigLoadError(f"Could not read configuration file {self._path}: {exc}") from exc

        try:
            parsed = yaml.safe_load(raw)
        except yaml.YAMLError as exc:
            raise ConfigLoadError(
                f"Malformed YAML in configuration file {self._path}: {exc}"
            ) from exc

        if parsed is None:
            return {}
        if not isinstance(parsed, dict):
            raise ConfigLoadError(
                f"Configuration file {self._path} must contain a mapping at the top level, "
                f"got {type(parsed).__name__}"
            )
        return parsed


class EnvironmentProvider(ConfigurationProvider):
    """Highest-precedence provider: environment variables.

    Convention: ``SHADOW_<SECTION>__<KEY>``, e.g. ``SHADOW_LOGGING__LEVEL=DEBUG``
    or ``SHADOW_KERNEL__STARTUP_TIMEOUT_SECONDS=45``. Top-level keys with no
    section (e.g. ``SHADOW_DEBUG=true``) are also supported.

    Values are parsed leniently: ``true``/``false`` (case-insensitive) become
    booleans, values that parse as ints or floats become numbers, everything
    else stays a string. Real type coercion/validation happens later via the
    Pydantic settings models — this provider only avoids handing every value
    to the validator as a string when it obviously isn't one.
    """

    def __init__(self, environ: dict[str, str] | None = None) -> None:
        self._environ = environ if environ is not None else dict(os.environ)

    def load(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for raw_key, raw_value in self._environ.items():
            if not raw_key.startswith(_ENV_PREFIX):
                continue

            key_path = raw_key[len(_ENV_PREFIX) :].lower().split(_ENV_NESTED_DELIMITER)
            value = self._coerce(raw_value)

            cursor = result
            for part in key_path[:-1]:
                cursor = cursor.setdefault(part, {})
                if not isinstance(cursor, dict):
                    raise ConfigLoadError(
                        f"Environment variable {raw_key} conflicts with a non-section value "
                        f"already set at the same path"
                    )
            cursor[key_path[-1]] = value

        return result

    @staticmethod
    def _coerce(value: str) -> Any:
        if re.fullmatch(r"(?i)true", value):
            return True
        if re.fullmatch(r"(?i)false", value):
            return False
        try:
            return int(value)
        except ValueError:
            pass
        try:
            return float(value)
        except ValueError:
            pass
        return value
