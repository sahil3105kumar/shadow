"""Log context propagation.

Maintains contextual metadata that is automatically attached to every log
record, per the LLD's Context Manager component and its "Context is
automatic" design decision: application code binds context once (e.g. at
the start of a request or job) rather than passing it to every individual
log call.

Built on `contextvars` rather than thread-locals so context is isolated
per execution context (thread *or* async task) per the LLD's Concurrency
Model.
"""

from __future__ import annotations

import threading
from collections.abc import Iterator
from contextlib import contextmanager
from contextvars import ContextVar
from typing import Any

_context_var: ContextVar[dict[str, Any] | None] = ContextVar("shadow_log_context", default=None)


def _snapshot() -> dict[str, Any]:
    """Return a copy of the currently bound fields, or an empty dict if none are bound."""
    bound = _context_var.get()
    return dict(bound) if bound is not None else {}


def current_context() -> dict[str, Any]:
    """Return a snapshot of the contextual metadata for the current execution context.

    Always includes `thread_id`; other keys (`request_id`, `job_id`,
    `conversation_id`, `plugin_id`, `correlation_id`, ...) are present only
    if previously bound via `bind_context`.
    """
    context = _snapshot()
    context["thread_id"] = threading.get_ident()
    return context


@contextmanager
def bind_context(**fields: Any) -> Iterator[None]:
    """Bind contextual fields for the duration of the `with` block.

    Nested calls layer on top of (and restore) any previously bound
    fields rather than replacing them outright, so a request-scoped
    `bind_context` can wrap a narrower job-scoped one without losing the
    request's fields:

        with bind_context(request_id="r-1"):
            with bind_context(job_id="j-1"):
                logger.info("working")  # context: {request_id: r-1, job_id: j-1}
            logger.info("done")  # context: {request_id: r-1}
    """
    parent = _snapshot()
    merged = {**parent, **fields}
    token = _context_var.set(merged)
    try:
        yield
    finally:
        _context_var.reset(token)


def clear_context() -> None:
    """Reset the current execution context's bound fields.

    For test suites and shutdown paths only — application code should
    prefer letting a `bind_context` block exit naturally.
    """
    _context_var.set(None)


class LogContext:
    """Object-oriented facade over the module-level context functions.

    The LLD's expected-classes list names `LogContext` explicitly; this
    class exists to satisfy that public surface while keeping the
    underlying primitives (`bind_context`, `current_context`,
    `clear_context`) independently testable and importable.
    """

    bind = staticmethod(bind_context)
    current = staticmethod(current_context)
    clear = staticmethod(clear_context)
