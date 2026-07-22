"""Configuration-specific exceptions.

The Configuration System's LLD (`docs/architecture/lld/infrastructure/configuration.md`)
lists Exceptions as a dependency, but the Exception Framework itself is a later
milestone item (Phase 0, Issue 12). These are minimal, local stand-ins scoped to
this package only.

When Issue 12 lands, these should be re-parented under ``shadow.exceptions.configuration``
and inherit from the shared ``ShadowError`` base without changing this module's
public names, so nothing importing from ``shadow.config.errors`` has to change.
"""

from __future__ import annotations


class ConfigError(Exception):
    """Base class for all Configuration System errors."""


class ConfigLoadError(ConfigError):
    """Raised when a configuration source cannot be loaded or parsed.

    Covers missing/unreadable YAML files, malformed YAML, and provider-level
    read failures. Does not cover validation failures — see
    :class:`ConfigValidationError`.
    """


class ConfigValidationError(ConfigError):
    """Raised when merged configuration fails validation.

    This is the fatal path described in the LLD's Error Handling section:
    missing required values, invalid types, schema validation failure, or
    conflicting providers. Raising this must prevent the application from
    starting.
    """
