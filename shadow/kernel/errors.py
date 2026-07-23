"""Kernel-level exceptions.

The DI Container's LLD (`docs/architecture/lld/kernel/container.md`) lists
Exceptions as a dependency, but the Exception Framework itself is a later
milestone item (Phase 0, Issue 12). These are minimal, local stand-ins,
following the same pattern as `shadow.config.errors` and
`shadow.infrastructure.logging.errors`.

Shared across `shadow.kernel` rather than scoped to `container.py` alone,
since later kernel issues (Event Bus, Plugin Framework, Kernel Bootstrap)
are also expected to need kernel-level exceptions.

When Issue 12 lands, these should be re-parented under
``shadow.exceptions.kernel`` and inherit from the shared ``ShadowError``
base without changing this module's public names.
"""

from __future__ import annotations


class KernelError(Exception):
    """Base class for all Kernel errors."""


class ContainerError(KernelError):
    """Base class for all DI Container errors."""


class DuplicateServiceError(ContainerError):
    """Raised when registering a service key that is already registered
    without passing ``override=True``. Fatal, per the LLD's Error Handling
    section ("duplicate required service")."""


class ServiceNotFoundError(ContainerError):
    """Raised by `resolve()` when a service key was never registered.
    Fatal ("missing required dependency"). `try_resolve()` returns `None`
    instead of raising this, covering the "optional service unavailable"
    recoverable case."""


class CircularDependencyError(ContainerError):
    """Raised when resolving a service would require resolving itself,
    directly or transitively. Fatal."""


class MissingDependencyError(ContainerError):
    """Raised during `freeze()` when a registered service declares a
    dependency on a key that was never registered. Fatal."""


class ContainerFrozenError(ContainerError):
    """Raised when attempting to register or remove a service after the
    container has been frozen. Fatal ("frozen container modification")."""


class ContainerDisposedError(ContainerError):
    """Raised when attempting to resolve or register a service after the
    container has been disposed. Fatal ("resolution after disposal")."""


class ServiceConstructionError(ContainerError):
    """Raised when a service factory raises while being constructed. Wraps
    the original exception so a failure deep in the dependency graph is
    still traceable to the service that failed. Fatal ("constructor
    failure")."""
