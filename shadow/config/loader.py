"""Configuration loader.

Discovers sources and merges them in precedence order: Defaults -> YAML file
-> Environment variables. Performs no validation — see `validators.py`.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from shadow.config.providers import DefaultProvider, EnvironmentProvider, YamlProvider

_CONFIG_PATH_ENV_VAR = "SHADOW_CONFIG_PATH"
_DEFAULT_CONFIG_FILENAMES = ("shadow.yaml", "shadow.yml")


def discover_config_path(search_dir: Path | None = None) -> Path | None:
    """Find the config file to load, if any.

    Precedence: ``SHADOW_CONFIG_PATH`` env var, then ``shadow.yaml``/``shadow.yml``
    in the current working directory (or ``search_dir`` if given). Returns
    ``None`` if nothing is found — this is not an error; Shadow must be able
    to start with zero config files present.
    """
    override = os.environ.get(_CONFIG_PATH_ENV_VAR)
    if override:
        return Path(override)

    base = search_dir if search_dir is not None else Path.cwd()
    for filename in _DEFAULT_CONFIG_FILENAMES:
        candidate = base / filename
        if candidate.exists():
            return candidate

    return None


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """Recursively merge `override` into `base`, returning a new dict.

    Nested dicts are merged key-by-key; any other type in `override`
    (including lists) replaces the corresponding value in `base` entirely
    rather than attempting a partial merge.
    """
    merged = dict(base)
    for key, override_value in override.items():
        base_value = merged.get(key)
        if isinstance(base_value, dict) and isinstance(override_value, dict):
            merged[key] = _deep_merge(base_value, override_value)
        else:
            merged[key] = override_value
    return merged


class ConfigurationLoader:
    """Loads and merges configuration from all providers, in precedence order."""

    def __init__(self, config_path: Path | str | None = None) -> None:
        self._config_path = Path(config_path) if config_path is not None else discover_config_path()

    def load(self) -> dict[str, Any]:
        """Return the fully merged configuration tree as a plain dict."""
        providers = (
            DefaultProvider(),
            YamlProvider(self._config_path),
            EnvironmentProvider(),
        )

        merged: dict[str, Any] = {}
        for provider in providers:
            merged = _deep_merge(merged, provider.load())
        return merged
