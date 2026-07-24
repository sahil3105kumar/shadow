"""Dependency Injection Container.

The DI Container is the central service registry of the Shadow runtime
(see `docs/architecture/lld/kernel/container.md`). It manages the
creation, registration, resolution, and lifetime of application services,
so components depend on abstractions resolved through the container
rather than on concrete implementations constructed directly.

`Container` is the only public entry point. The Service Registry,
Resolver, Lifetime Manager, Factory Manager, Dependency Validator, and
Disposal Manager described in the LLD are internal collaborators folded
into private methods on `Container` rather than separate classes, since
the LLD's Package Structure calls for a single `container.py` module.

Typical usage, once at bootstrap:

    container = Container()
    container.register_instance(LoggingSettings, settings.logging)
    container.register_singleton(Database, lambda ctx: Database(ctx.resolve(LoggingSettings)))
    container.freeze()

    db = container.resolve(Database)
    ...
    container.dispose()
"""

from __future__ import annotations

import threading
from collections.abc import Callable, Hashable
from dataclasses import dataclass
from enum import Enum, auto
from typing import Any

from shadow.kernel.errors import (
    CircularDependencyError,
    ContainerDisposedError,
    ContainerFrozenError,
    DuplicateServiceError,
    MissingDependencyError,
    ServiceConstructionError,
    ServiceNotFoundError,
)

ServiceKey = Hashable
"""A service is identified by a type (typically an abstract base class or a
concrete class) or a plain string. Either works as a dict key, which is all
the container actually requires of it."""

ServiceFactory = Callable[["ResolutionContext"], Any]


def _key_name(key: ServiceKey) -> str:
    """Render a service key for error messages and diagnostics."""
    return key.__name__ if isinstance(key, type) else str(key)


class ServiceLifetime(Enum):
    """How long a resolved service instance is kept alive, per the LLD's
    Lifetime Manager component."""

    SINGLETON = auto()
    """Constructed once, on first resolution; every later `resolve()` call
    for the same key returns the same instance."""

    TRANSIENT = auto()
    """Constructed fresh on every `resolve()` call."""

    SCOPED = auto()
    """Reserved for future use (see the LLD's Future Extensions). Shadow
    has no notion of a request/session scope yet, so registering a
    service with this lifetime raises `NotImplementedError` rather than
    silently behaving like `SINGLETON` or `TRANSIENT`."""


class ContainerState(Enum):
    """The container's lifecycle states, per the LLD's State Management section."""

    CREATED = auto()
    REGISTERING = auto()
    FROZEN = auto()
    DISPOSED = auto()


@dataclass
class ServiceDescriptor:
    """Registration metadata for one service, per the LLD's Data Models section."""

    key: ServiceKey
    factory: ServiceFactory
    lifetime: ServiceLifetime
    dependencies: tuple[ServiceKey, ...] = ()
    instance: Any = None
    initialized: bool = False


class ResolutionContext:
    """Passed into every factory so it can pull its own dependencies out of
    the same container, e.g. `lambda ctx: Service(ctx.resolve(Other))`.

    Automatic constructor injection (reflecting a factory's signature) is
    a documented Future Extension, not implemented here — factories
    declare what they need explicitly, both to `ResolutionContext.resolve`
    and (for graph validation) via `dependencies=` at registration time.
    """

    def __init__(self, container: Container) -> None:
        self._container = container

    def resolve(self, key: ServiceKey) -> Any:
        return self._container.resolve(key)

    def try_resolve(self, key: ServiceKey) -> Any | None:
        return self._container.try_resolve(key)


class RegistrationBuilder:
    """A fluent handle returned by `register()` (and its `register_*` sugar)
    for declaring additional dependency metadata after the initial call:

        container.register(Foo, factory=make_foo).with_dependencies(Bar, Baz)

    The descriptor is already stored in the registry the moment `register()`
    returns; this builder mutates that same descriptor in place rather than
    deferring registration to a `.build()` call.
    """

    def __init__(self, descriptor: ServiceDescriptor) -> None:
        self._descriptor = descriptor

    @property
    def key(self) -> ServiceKey:
        return self._descriptor.key

    @property
    def lifetime(self) -> ServiceLifetime:
        return self._descriptor.lifetime

    @property
    def dependencies(self) -> tuple[ServiceKey, ...]:
        return self._descriptor.dependencies

    def with_dependencies(self, *dependencies: ServiceKey) -> RegistrationBuilder:
        """Declare additional services this registration depends on, so
        `freeze()`'s dependency validation can catch a missing or circular
        dependency before anything is ever resolved."""
        self._descriptor.dependencies = (*self._descriptor.dependencies, *dependencies)
        return self


class Container:
    """The Dependency Injection Container. See the module docstring for
    typical usage; see `docs/architecture/lld/kernel/container.md` for the
    full design."""

    def __init__(self, *, logger: Any | None = None) -> None:
        self._state = ContainerState.CREATED
        self._lock = threading.RLock()
        self._descriptors: dict[ServiceKey, ServiceDescriptor] = {}
        self._construction_order: list[ServiceKey] = []
        self._resolution_stack = threading.local()
        self._logger = logger if logger is not None else self._default_logger()

    @staticmethod
    def _default_logger() -> Any | None:
        """Logging is optional for the container, per the LLD's Dependencies
        section — diagnostics should never be a hard requirement to use it."""
        try:
            from shadow.infrastructure.logging import get_logger

            return get_logger("kernel.container")
        except Exception:  # noqa: BLE001 - logging must never block the container
            return None

    @property
    def state(self) -> ContainerState:
        return self._state

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register(
        self,
        key: ServiceKey,
        factory: ServiceFactory,
        *,
        lifetime: ServiceLifetime = ServiceLifetime.SINGLETON,
        dependencies: tuple[ServiceKey, ...] = (),
        override: bool = False,
    ) -> RegistrationBuilder:
        """Register `key` to be constructed by `factory` when first resolved.

        Raises `DuplicateServiceError` if `key` is already registered,
        unless `override=True` — the LLD's "duplicate optional
        registration" recoverable case is modeled as an explicit opt-in
        rather than a silent default, so an accidental duplicate
        registration is still caught by default.
        """
        if lifetime is ServiceLifetime.SCOPED:
            raise NotImplementedError(
                "ServiceLifetime.SCOPED is reserved for future use and not yet supported"
            )

        with self._lock:
            self._ensure_can_register()
            if key in self._descriptors and not override:
                raise DuplicateServiceError(f"Service {_key_name(key)!r} is already registered")
            descriptor = ServiceDescriptor(
                key=key, factory=factory, lifetime=lifetime, dependencies=tuple(dependencies)
            )
            self._descriptors[key] = descriptor
            if self._state is ContainerState.CREATED:
                self._state = ContainerState.REGISTERING
            self._log("debug", "service registered", key)
            return RegistrationBuilder(descriptor)

    def register_singleton(
        self,
        key: ServiceKey,
        factory: ServiceFactory,
        *,
        dependencies: tuple[ServiceKey, ...] = (),
        override: bool = False,
    ) -> RegistrationBuilder:
        """Sugar for `register(..., lifetime=ServiceLifetime.SINGLETON)`."""
        return self.register(
            key,
            factory,
            lifetime=ServiceLifetime.SINGLETON,
            dependencies=dependencies,
            override=override,
        )

    def register_factory(
        self,
        key: ServiceKey,
        factory: ServiceFactory,
        *,
        dependencies: tuple[ServiceKey, ...] = (),
        override: bool = False,
    ) -> RegistrationBuilder:
        """Sugar for `register(..., lifetime=ServiceLifetime.TRANSIENT)`: a
        fresh instance is constructed on every `resolve()` call."""
        return self.register(
            key,
            factory,
            lifetime=ServiceLifetime.TRANSIENT,
            dependencies=dependencies,
            override=override,
        )

    def register_instance(
        self, key: ServiceKey, instance: Any, *, override: bool = False
    ) -> RegistrationBuilder:
        """Register an already-constructed object as a singleton.

        Useful for values that don't need (or can't have) a factory, such
        as a `Settings` object loaded before the container exists.
        """
        with self._lock:
            self._ensure_can_register()
            if key in self._descriptors and not override:
                raise DuplicateServiceError(f"Service {_key_name(key)!r} is already registered")
            descriptor = ServiceDescriptor(
                key=key,
                factory=lambda _ctx: instance,
                lifetime=ServiceLifetime.SINGLETON,
                dependencies=(),
                instance=instance,
                initialized=True,
            )
            self._descriptors[key] = descriptor
            if self._state is ContainerState.CREATED:
                self._state = ContainerState.REGISTERING
            self._log("debug", "instance registered", key)
            return RegistrationBuilder(descriptor)

    def remove(self, key: ServiceKey) -> None:
        """Unregister `key`. Only permitted before the container is frozen."""
        with self._lock:
            self._ensure_can_register()
            self._descriptors.pop(key, None)

    def contains(self, key: ServiceKey) -> bool:
        """Return whether `key` is currently registered. Safe to call in any state."""
        return key in self._descriptors

    # ------------------------------------------------------------------
    # Resolution
    # ------------------------------------------------------------------

    def resolve(self, key: ServiceKey) -> Any:
        """Resolve `key` to an instance, constructing it (and any
        dependencies it pulls via `ResolutionContext.resolve`) if needed.

        Raises `ServiceNotFoundError` if `key` was never registered, and
        `CircularDependencyError` if resolving it requires resolving
        itself, directly or transitively.
        """
        if self._state is ContainerState.DISPOSED:
            raise ContainerDisposedError("Cannot resolve services from a disposed container")

        descriptor = self._descriptors.get(key)
        if descriptor is None:
            raise ServiceNotFoundError(f"No service registered for {_key_name(key)!r}")

        if descriptor.lifetime is ServiceLifetime.SINGLETON and descriptor.initialized:
            return descriptor.instance

        stack: list[ServiceKey] = getattr(self._resolution_stack, "keys", None) or []
        if key in stack:
            cycle = " -> ".join(_key_name(k) for k in (*stack, key))
            raise CircularDependencyError(f"Circular dependency detected: {cycle}")

        if descriptor.lifetime is ServiceLifetime.SINGLETON:
            with self._lock:
                # Re-check inside the lock: another thread may have finished
                # constructing this singleton while we were waiting for it.
                if descriptor.initialized:
                    return descriptor.instance
                instance = self._construct(descriptor, stack)
                descriptor.instance = instance
                descriptor.initialized = True
                self._construction_order.append(key)
                return instance

        # Transient: no locking, no caching — a fresh instance every time.
        return self._construct(descriptor, stack)

    def try_resolve(self, key: ServiceKey) -> Any | None:
        """Like `resolve()`, but returns `None` instead of raising
        `ServiceNotFoundError` for an unregistered key. Other failures
        (circular dependency, constructor failure, disposed container)
        still raise — those are programming errors, not "the service is
        optional" situations."""
        if not self.contains(key):
            return None
        return self.resolve(key)

    def _construct(self, descriptor: ServiceDescriptor, stack: list[ServiceKey]) -> Any:
        self._resolution_stack.keys = [*stack, descriptor.key]
        try:
            context = ResolutionContext(self)
            try:
                instance = descriptor.factory(context)
            except (ContainerDisposedError, ServiceNotFoundError, CircularDependencyError):
                raise
            except Exception as exc:
                raise ServiceConstructionError(
                    f"Factory for {_key_name(descriptor.key)!r} raised: {exc}"
                ) from exc
            self._log("debug", "service constructed", descriptor.key)
            return instance
        finally:
            self._resolution_stack.keys = stack

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def freeze(self) -> None:
        """Validate the declared dependency graph, then stop accepting new
        registrations. Idempotent once frozen.

        Per the LLD, dependency validation happens once here rather than
        on every `resolve()` call, so a missing or circular dependency is
        caught during bootstrap instead of on first use in production.
        """
        with self._lock:
            if self._state is ContainerState.DISPOSED:
                raise ContainerDisposedError("Cannot freeze a disposed container")
            if self._state is ContainerState.FROZEN:
                return
            self._validate_dependency_graph()
            self._state = ContainerState.FROZEN
            self._log("info", "container frozen", None)

    def dispose(self) -> None:
        """Dispose constructed singleton instances (in reverse construction
        order, per the LLD) and clear the registry. Idempotent.

        Each instance's `close()` or `dispose()` method (if it has one) is
        called on a best-effort basis: one failing disposal is logged and
        does not prevent the rest from running, the same way
        `LoggingManager.shutdown()` never raises.
        """
        with self._lock:
            if self._state is ContainerState.DISPOSED:
                return
            for key in reversed(self._construction_order):
                descriptor = self._descriptors.get(key)
                if descriptor is None:
                    continue
                self._dispose_instance(key, descriptor.instance)
            self._descriptors.clear()
            self._construction_order.clear()
            self._state = ContainerState.DISPOSED
            self._log("info", "container disposed", None)

    def _dispose_instance(self, key: ServiceKey, instance: Any) -> None:
        disposer = getattr(instance, "dispose", None) or getattr(instance, "close", None)
        if disposer is None:
            return
        try:
            disposer()
        except Exception:  # noqa: BLE001 - disposal must never raise during shutdown
            self._log("warning", "service disposal failed", key)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _ensure_can_register(self) -> None:
        if self._state is ContainerState.FROZEN:
            raise ContainerFrozenError("Cannot modify a frozen container")
        if self._state is ContainerState.DISPOSED:
            raise ContainerDisposedError("Cannot modify a disposed container")

    def _validate_dependency_graph(self) -> None:
        for descriptor in self._descriptors.values():
            for dependency in descriptor.dependencies:
                if dependency not in self._descriptors:
                    raise MissingDependencyError(
                        f"Service {_key_name(descriptor.key)!r} depends on "
                        f"{_key_name(dependency)!r}, which is not registered"
                    )

        visiting: set[ServiceKey] = set()
        visited: set[ServiceKey] = set()

        def visit(key: ServiceKey, path: list[ServiceKey]) -> None:
            if key in visiting:
                cycle = " -> ".join(_key_name(k) for k in (*path, key))
                raise CircularDependencyError(f"Circular dependency detected: {cycle}")
            if key in visited:
                return
            visiting.add(key)
            for dependency in self._descriptors[key].dependencies:
                visit(dependency, [*path, key])
            visiting.discard(key)
            visited.add(key)

        for key in self._descriptors:
            visit(key, [])

    def _log(self, level: str, message: str, key: ServiceKey | None) -> None:
        if self._logger is None:
            return
        suffix = f": {_key_name(key)}" if key is not None else ""
        getattr(self._logger, level)(f"{message}{suffix}")
