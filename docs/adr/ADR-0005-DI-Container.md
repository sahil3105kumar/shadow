# ADR-0005: DI Container — Explicit Dependencies, No Auto-Injection

**Status:** Accepted
**Date:** 2026-07-23
**Related:** `docs/architecture/lld/kernel/container.md`, Issue #4 (Dependency Injection Container)

---

## Context

Issue #4 asks for a lightweight DI container supporting service
registration, singleton management, factory registration, dependency
resolution, and lazy initialization. The LLD's Future Extensions list
explicitly defers "automatic constructor injection" and "assembly/module
scanning" to later work, which leaves open how services are meant to
declare their dependencies *right now*.

## Problem Statement

Without reflection-based auto-injection, how does a service factory
obtain its own dependencies, and how does the container know a
dependency graph exists at all — for validation, and for correct
disposal order — if it never inspects factory signatures?

## Decision

Every factory receives a `ResolutionContext` and pulls its own
dependencies explicitly:

```python
container.register_singleton(
    Database,
    lambda ctx: Database(ctx.resolve(LoggingSettings)),
    dependencies=(LoggingSettings,),
)
```

The `dependencies=` tuple is a second, independent declaration used only
by `freeze()`'s static graph validation (missing-dependency and
declared-cycle detection). It does not drive resolution — the factory
body does that itself via `ctx.resolve(...)`. The two can, in principle,
drift apart (a factory could resolve something it didn't declare); a
thread-local resolution stack catches any resulting cycle at actual
resolution time regardless of whether it was declared, so an incomplete
`dependencies=` tuple weakens validation coverage but never produces an
undetected runtime cycle.

Singleton disposal order is derived from actual construction order
(tracked as each singleton is first built) rather than from a formal
topological sort of the declared graph, and disposed in reverse. Since a
factory can only obtain an already-constructed dependency, construction
order is guaranteed to already respect the dependency graph.

## Alternatives Considered

- **Reflect on factory/constructor signatures for automatic injection.**
  More convenient, but the LLD defers this to a Future Extension, and it
  would require every service to be a class (not an arbitrary factory
  callable) with type-hinted constructor parameters — a bigger
  commitment than Phase 0 needs.
- **Full topological sort for disposal order.** More formally correct,
  but adds a second graph representation to keep in sync with the
  construction-order list, for a phase where singleton graphs are small
  and shallow.

## Consequences

- Registrations are slightly more verbose (`dependencies=` alongside the
  factory body's own `ctx.resolve()` calls) than a fully automatic
  container would be.
- If a future issue adds constructor reflection, it can be introduced as
  an alternative registration path (e.g. `register_type(Database)`) that
  still populates the same `ServiceDescriptor.dependencies` field,
  without changing `resolve()`, `freeze()`, or `dispose()`.

## Superseded By

Not superseded.