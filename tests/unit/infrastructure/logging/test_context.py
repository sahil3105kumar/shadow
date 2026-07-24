from __future__ import annotations

import threading

from shadow.infrastructure.logging.context import LogContext, bind_context, current_context


def test_current_context_always_includes_thread_id() -> None:
    context = current_context()
    assert context["thread_id"] == threading.get_ident()


def test_bind_context_adds_fields_for_the_block_only() -> None:
    assert "request_id" not in current_context()

    with bind_context(request_id="r-1"):
        assert current_context()["request_id"] == "r-1"

    assert "request_id" not in current_context()


def test_nested_bind_context_layers_fields() -> None:
    with bind_context(request_id="r-1"):
        with bind_context(job_id="j-1"):
            context = current_context()
            assert context["request_id"] == "r-1"
            assert context["job_id"] == "j-1"

        # Outer context is restored, not wiped, after the inner block exits.
        context = current_context()
        assert context["request_id"] == "r-1"
        assert "job_id" not in context


def test_inner_bind_context_can_override_a_parent_field() -> None:
    with bind_context(correlation_id="outer"):
        with bind_context(correlation_id="inner"):
            assert current_context()["correlation_id"] == "inner"
        assert current_context()["correlation_id"] == "outer"


def test_log_context_facade_matches_module_functions() -> None:
    with LogContext.bind(plugin_id="p-1"):
        assert LogContext.current()["plugin_id"] == "p-1"
    LogContext.clear()
    assert "plugin_id" not in LogContext.current()


def test_context_is_isolated_per_thread() -> None:
    seen: dict[str, object] = {}

    def worker() -> None:
        with bind_context(request_id="thread-local"):
            seen["thread_context"] = current_context().get("request_id")

    with bind_context(request_id="main-thread"):
        thread = threading.Thread(target=worker)
        thread.start()
        thread.join()
        assert current_context()["request_id"] == "main-thread"

    assert seen["thread_context"] == "thread-local"
