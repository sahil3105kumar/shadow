"""Logging-System-specific exceptions.

The Logging System's LLD (`docs/architecture/lld/infrastructure/logging.md`)
lists Exceptions as a dependency, but the Exception Framework itself is a
later milestone item (Phase 0, Issue 12). These are minimal, local
stand-ins scoped to this package only, following the same pattern as
`shadow.config.errors`.

When Issue 12 lands, these should be re-parented under
``shadow.exceptions.logging`` and inherit from the shared ``ShadowError``
base without changing this module's public names, so nothing importing
from ``shadow.infrastructure.logging.errors`` has to change.
"""

from __future__ import annotations


class LoggingError(Exception):
    """Base class for all Logging System errors."""


class LoggingInitializationError(LoggingError):
    """Raised when the Logging System fails to initialize.

    Covers unreachable/uncreatable log directories, unwritable log files,
    and other problems discovered while building handlers. Per the LLD's
    Error Handling section this is fatal — it must prevent the application
    from starting rather than silently falling back to a degraded state.
    """


class LoggingConfigurationError(LoggingError):
    """Raised when logging settings are structurally invalid in a way that
    `LoggingSettings` validation alone can't catch (e.g. a `log_dir` that
    points at an existing path which is not a directory).
    """
