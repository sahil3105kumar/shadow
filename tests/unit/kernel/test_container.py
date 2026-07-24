from __future__ import annotations

import threading
import time

import pytest

from shadow.kernel.container import (
    Container,
    ContainerState,
    ResolutionContext,
    ServiceLifetime,
)
from shadow.kernel.errors import (
    CircularDependencyError,
    ContainerDisposedError,
    ContainerFrozenError,
    DuplicateServiceError,
    MissingDependencyError,
    ServiceConstructionError,
    ServiceNotFoundError,
)


class Alpha:
    def __init__(self) -> None:
        self.disposed = False

    def dispose(self) -> None:
        self.disposed = True


class Beta:
    def __init__(self, alpha: Alpha) -> None:
        self.alpha = alpha


@pytest.fixture
def container() -> Container:
    # No logger passed; the default lookup falls back to `shadow.infrastructure.logging`
    # if importable, so tests exercise the real (soft-optional) logging integration too.
    return Container()


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------


def test_initial_state_is_created(container: Container) -> None:
    assert container.state == ContainerState.CREATED


def test_register_moves_state_to_registering(container: Container) -> None:
    container.register_singleton(Alpha, lambda ctx: Alpha())
    assert container.state == ContainerState.REGISTERING


def test_contains_reflects_registration(container: Container) -> None:
    assert container.contains(Alpha) is False
    container.register_singleton(Alpha, lambda ctx: Alpha())
    assert container.contains(Alpha) is True


def test_duplicate_registration_raises_by_default(container: Container) -> None:
    container.register_singleton(Alpha, lambda ctx: Alpha())
    with pytest.raises(DuplicateServiceError):
        container.register_singleton(Alpha, lambda ctx: Alpha())


def test_duplicate_registration_with_override_replaces_descriptor(container: Container) -> None:
    container.register_singleton(Alpha, lambda ctx: Alpha())
    first = container.resolve(Alpha)

    container.register_singleton(Alpha, lambda ctx: Alpha(), override=True)
    second = container.resolve(Alpha)

    assert first is not second


def test_register_instance_returns_the_same_object(container: Container) -> None:
    alpha = Alpha()
    container.register_instance(Alpha, alpha)
    assert container.resolve(Alpha) is alpha


def test_register_scoped_lifetime_raises_not_implemented(container: Container) -> None:
    with pytest.raises(NotImplementedError):
        container.register(Alpha, lambda ctx: Alpha(), lifetime=ServiceLifetime.SCOPED)


def test_remove_before_freeze_unregisters_the_service(container: Container) -> None:
    container.register_singleton(Alpha, lambda ctx: Alpha())
    container.remove(Alpha)
    assert container.contains(Alpha) is False


def test_registration_builder_with_dependencies_is_reflected_in_validation(
    container: Container,
) -> None:
    builder = container.register_singleton(Beta, lambda ctx: Beta(ctx.resolve(Alpha)))
    builder.with_dependencies(Alpha)

    with pytest.raises(MissingDependencyError):
        container.freeze()  # Alpha was declared as a dependency but never registered


# ---------------------------------------------------------------------------
# Resolution
# ---------------------------------------------------------------------------


def test_resolve_unregistered_service_raises() -> None:
    container = Container()
    with pytest.raises(ServiceNotFoundError):
        container.resolve(Alpha)


def test_try_resolve_unregistered_service_returns_none() -> None:
    container = Container()
    assert container.try_resolve(Alpha) is None


def test_try_resolve_registered_service_returns_instance(container: Container) -> None:
    container.register_singleton(Alpha, lambda ctx: Alpha())
    assert isinstance(container.try_resolve(Alpha), Alpha)


def test_singleton_resolves_to_the_same_instance_every_time(container: Container) -> None:
    container.register_singleton(Alpha, lambda ctx: Alpha())
    assert container.resolve(Alpha) is container.resolve(Alpha)


def test_transient_resolves_to_a_new_instance_every_time(container: Container) -> None:
    container.register_factory(Alpha, lambda ctx: Alpha())
    assert container.resolve(Alpha) is not container.resolve(Alpha)


def test_resolution_context_resolves_declared_dependencies(container: Container) -> None:
    container.register_singleton(Alpha, lambda ctx: Alpha())
    container.register_singleton(Beta, lambda ctx: Beta(ctx.resolve(Alpha)), dependencies=(Alpha,))

    beta = container.resolve(Beta)

    assert isinstance(beta.alpha, Alpha)
    assert beta.alpha is container.resolve(Alpha)


def test_factory_exception_is_wrapped_in_service_construction_error(container: Container) -> None:
    def broken_factory(ctx: ResolutionContext) -> Alpha:
        raise ValueError("boom")

    container.register_singleton(Alpha, broken_factory)

    with pytest.raises(ServiceConstructionError):
        container.resolve(Alpha)


def test_direct_self_dependency_raises_circular_dependency_error(container: Container) -> None:
    container.register_singleton("self_referencing", lambda ctx: ctx.resolve("self_referencing"))

    with pytest.raises(CircularDependencyError):
        container.resolve("self_referencing")


def test_indirect_cycle_is_caught_at_runtime_resolution(container: Container) -> None:
    container.register_singleton("a", lambda ctx: ctx.resolve("b"))
    container.register_singleton("b", lambda ctx: ctx.resolve("a"))

    with pytest.raises(CircularDependencyError):
        container.resolve("a")


def test_declared_cycle_is_caught_at_freeze_time(container: Container) -> None:
    container.register_singleton("a", lambda ctx: ctx.resolve("b"), dependencies=("b",))
    container.register_singleton("b", lambda ctx: ctx.resolve("a"), dependencies=("a",))

    with pytest.raises(CircularDependencyError):
        container.freeze()


def test_missing_declared_dependency_is_caught_at_freeze_time(container: Container) -> None:
    container.register_singleton(Beta, lambda ctx: Beta(ctx.resolve(Alpha)), dependencies=(Alpha,))

    with pytest.raises(MissingDependencyError):
        container.freeze()


# ---------------------------------------------------------------------------
# Lifecycle: freeze
# ---------------------------------------------------------------------------


def test_freeze_moves_state_to_frozen(container: Container) -> None:
    container.freeze()
    assert container.state == ContainerState.FROZEN


def test_freeze_is_idempotent(container: Container) -> None:
    container.freeze()
    container.freeze()  # must not raise
    assert container.state == ContainerState.FROZEN


def test_registration_after_freeze_raises(container: Container) -> None:
    container.freeze()
    with pytest.raises(ContainerFrozenError):
        container.register_singleton(Alpha, lambda ctx: Alpha())


def test_remove_after_freeze_raises(container: Container) -> None:
    container.register_singleton(Alpha, lambda ctx: Alpha())
    container.freeze()
    with pytest.raises(ContainerFrozenError):
        container.remove(Alpha)


def test_resolution_still_works_after_freeze(container: Container) -> None:
    container.register_singleton(Alpha, lambda ctx: Alpha())
    container.freeze()
    assert isinstance(container.resolve(Alpha), Alpha)


# ---------------------------------------------------------------------------
# Lifecycle: dispose
# ---------------------------------------------------------------------------


def test_dispose_moves_state_to_disposed(container: Container) -> None:
    container.dispose()
    assert container.state == ContainerState.DISPOSED


def test_dispose_is_idempotent(container: Container) -> None:
    container.dispose()
    container.dispose()  # must not raise
    assert container.state == ContainerState.DISPOSED


def test_dispose_calls_dispose_on_constructed_singletons(container: Container) -> None:
    container.register_singleton(Alpha, lambda ctx: Alpha())
    alpha = container.resolve(Alpha)

    container.dispose()

    assert alpha.disposed is True


def test_dispose_ignores_services_without_a_dispose_or_close_method(container: Container) -> None:
    container.register_instance("plain_value", object())
    container.resolve("plain_value")
    container.dispose()  # must not raise


def test_dispose_continues_past_a_failing_disposal(container: Container) -> None:
    class Broken:
        def dispose(self) -> None:
            raise RuntimeError("cleanup failed")

    container.register_singleton(Broken, lambda ctx: Broken())
    container.register_singleton(Alpha, lambda ctx: Alpha())
    container.resolve(Broken)
    alpha = container.resolve(Alpha)

    container.dispose()  # must not raise despite Broken.dispose() failing

    assert alpha.disposed is True


def test_dispose_runs_in_reverse_construction_order(container: Container) -> None:
    order: list[str] = []

    class Recorder:
        def __init__(self, name: str) -> None:
            self.name = name

        def dispose(self) -> None:
            order.append(self.name)

    container.register_singleton("a", lambda ctx: Recorder("a"))
    container.register_singleton("b", lambda ctx: Recorder("b"))
    container.resolve("a")
    container.resolve("b")

    container.dispose()

    assert order == ["b", "a"]


def test_resolve_after_dispose_raises(container: Container) -> None:
    container.register_singleton(Alpha, lambda ctx: Alpha())
    container.dispose()
    with pytest.raises(ContainerDisposedError):
        container.resolve(Alpha)


def test_register_after_dispose_raises(container: Container) -> None:
    container.dispose()
    with pytest.raises(ContainerDisposedError):
        container.register_singleton(Alpha, lambda ctx: Alpha())


def test_freeze_after_dispose_raises(container: Container) -> None:
    container.dispose()
    with pytest.raises(ContainerDisposedError):
        container.freeze()


def test_contains_returns_false_after_dispose_clears_registry(container: Container) -> None:
    container.register_singleton(Alpha, lambda ctx: Alpha())
    container.dispose()
    assert container.contains(Alpha) is False


# ---------------------------------------------------------------------------
# Concurrency
# ---------------------------------------------------------------------------


def test_singleton_is_constructed_exactly_once_under_concurrent_resolution(
    container: Container,
) -> None:
    construction_count = 0
    lock = threading.Lock()

    def slow_factory(ctx: ResolutionContext) -> Alpha:
        nonlocal construction_count
        with lock:
            construction_count += 1
        time.sleep(0.02)
        return Alpha()

    container.register_singleton(Alpha, slow_factory)

    results: list[Alpha] = []

    def worker() -> None:
        results.append(container.resolve(Alpha))

    threads = [threading.Thread(target=worker) for _ in range(8)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert construction_count == 1
    assert len({id(instance) for instance in results}) == 1
