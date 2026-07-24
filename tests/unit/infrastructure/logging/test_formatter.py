from __future__ import annotations

import json
import logging

from shadow.config.models import LogFormat
from shadow.infrastructure.logging.context import bind_context
from shadow.infrastructure.logging.formatter import StructuredFormatter


def _make_record(**overrides: object) -> logging.LogRecord:
    defaults: dict[str, object] = {
        "name": "shadow.kernel.bootstrap",
        "level": logging.INFO,
        "pathname": __file__,
        "lineno": 1,
        "msg": "kernel starting",
        "args": (),
        "exc_info": None,
    }
    defaults.update(overrides)
    return logging.LogRecord(**defaults)  # type: ignore[arg-type]


def test_json_output_contains_expected_fields() -> None:
    formatter = StructuredFormatter(fmt=LogFormat.JSON)
    record = _make_record()

    payload = json.loads(formatter.format(record))

    assert payload["level"] == "INFO"
    assert payload["logger"] == "shadow.kernel.bootstrap"
    assert payload["message"] == "kernel starting"
    assert payload["component"] == "shadow.kernel.bootstrap"
    assert "timestamp" in payload
    assert "context" in payload


def test_json_output_is_valid_json_and_single_line() -> None:
    formatter = StructuredFormatter(fmt=LogFormat.JSON)
    output = formatter.format(_make_record())

    assert "\n" not in output
    json.loads(output)  # must not raise


def test_console_output_is_human_readable() -> None:
    formatter = StructuredFormatter(fmt=LogFormat.CONSOLE)
    output = formatter.format(_make_record())

    assert "INFO" in output
    assert "shadow.kernel.bootstrap" in output
    assert "kernel starting" in output


def test_bound_context_is_attached_to_the_record() -> None:
    formatter = StructuredFormatter(fmt=LogFormat.JSON)
    with bind_context(request_id="r-42"):
        payload = json.loads(formatter.format(_make_record()))

    assert payload["context"]["request_id"] == "r-42"


def test_extra_fields_become_metadata() -> None:
    formatter = StructuredFormatter(fmt=LogFormat.JSON)
    record = _make_record()
    record.user_id = "u-1"  # simulates logger.info(..., extra={"user_id": "u-1"})

    payload = json.loads(formatter.format(record))

    assert payload["metadata"]["user_id"] == "u-1"


def test_exception_info_is_included() -> None:
    formatter = StructuredFormatter(fmt=LogFormat.JSON)
    try:
        raise ValueError("boom")
    except ValueError:
        import sys

        record = _make_record(exc_info=sys.exc_info())

    payload = json.loads(formatter.format(record))

    assert "ValueError: boom" in payload["exception"]


def test_console_output_appends_exception_traceback() -> None:
    formatter = StructuredFormatter(fmt=LogFormat.CONSOLE)
    try:
        raise ValueError("boom")
    except ValueError:
        import sys

        record = _make_record(exc_info=sys.exc_info())

    output = formatter.format(record)

    assert "ValueError: boom" in output
