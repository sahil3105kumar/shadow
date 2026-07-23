"""Default configuration values.

Defaults are the lowest-precedence source (Defaults -> YAML -> Environment).
They are expressed as a plain nested dict so the Loader can merge them the
same way it merges every other provider's output, rather than relying on
Pydantic's own field defaults for merging semantics.

Keeping this as an explicit, reviewable dict (instead of "defaults are just
whatever's in the model") also makes it possible for a config file or env var
to override *some* nested keys of a section without needing to restate the
whole section.
"""

from __future__ import annotations

from typing import Any


def default_config() -> dict[str, Any]:
    """Return a fresh copy of the built-in default configuration tree.

    Returns a new dict each call so callers can safely mutate it while
    merging without affecting the defaults for future calls.
    """
    return {
        "environment": "development",
        "debug": False,
        "kernel": {
            "startup_timeout_seconds": 30.0,
            "shutdown_timeout_seconds": 15.0,
        },
        "logging": {
            "level": "INFO",
            "format": "json",
            "console_enabled": True,
            "file_enabled": False,
            "log_dir": "logs",
            "log_filename": "shadow.log",
            "max_bytes": 10_485_760,
            "backup_count": 5,
            "timestamp_format": "%Y-%m-%dT%H:%M:%S%z",
            "mask_sensitive_fields": True,
        },
        "plugins": {
            "enabled": True,
            "plugin_dirs": ["plugins"],
        },
        "scheduler": {
            "max_concurrent_jobs": 10,
        },
        "security": {
            "require_approval_for_actions": True,
        },
    }
