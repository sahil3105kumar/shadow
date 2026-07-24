# ADR-0004: Structured Logging Built on the Standard Library

**Status:** Accepted
**Date:** 2026-07-23
**Related:** `docs/architecture/lld/infrastructure/logging.md`, Issue #3 (Structured Logging)

---

## Context

Issue #3 requires a centralized, structured logging framework: every
subsystem obtains a logger through it, output is JSON or console
formatted, context is attached automatically, and sensitive fields are
redacted.

`pyproject.toml`'s `dev` dependency group already lists `structlog` and
`rich`, which could plausibly have been intended as the implementation
mechanism for this issue.

## Problem Statement

Should the Logging System be built on `structlog` (already present as a
dev dependency) or on Python's standard library `logging` module, wrapped
by Shadow's own formatter/handler/filter layer?

## Decision

Build on the standard library `logging` module. `shadow.infrastructure.logging`
wraps it with a custom `StructuredFormatter` (JSON/console), `LogHandler`
factory (console + rotating file), a small set of `logging.Filter`
subclasses (level, component, sensitive-data redaction, duplicate
suppression), and `contextvars`-based automatic context propagation.

`get_logger()` returns a plain `logging.Logger`, so any third-party
library that already logs via the standard `logging` module (which is
most of the Python ecosystem) is automatically compatible without an
adapter.

`structlog` and `rich` remain unused for now. They are left in the `dev`
group rather than removed, since a future issue may still want
`structlog`'s processor pipeline or `rich`'s console rendering for
developer-facing output — that is a separable decision from this one.

## Alternatives Considered

- **Use `structlog` as the core.** Gives a richer processor pipeline
  out of the box, but adds a second logging abstraction on top of
  whatever the underlying libraries already use, and moves `structlog`
  from a dev-only dependency to a runtime one — a larger footprint change
  than this issue's scope needs the trade-off to justify.
- **Let every subsystem configure `logging` independently.** Rejected in
  the issue itself ("Alternatives Considered"): produces inconsistent
  formatting and duplicated configuration.

## Consequences

- No new runtime dependency is introduced by this issue.
- Third-party libraries using stdlib `logging` integrate for free.
- If a future issue adopts `structlog`, it can sit on top of this layer
  (e.g. as an alternative `StructuredFormatter` implementation) without
  changing the public API (`initialize`, `get_logger`, `set_level`,
  `flush`, `shutdown`).

## Superseded By

Not superseded.