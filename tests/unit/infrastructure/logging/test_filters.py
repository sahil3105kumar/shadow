from __future__ import annotations

import logging

import pytest

from shadow.infrastructure.logging.filters import (
    ComponentFilter,
    DuplicateSuppressionFilter,
    LevelFilter,
    SensitiveDataFilter,
)


def _make_record(
    name: str = "shadow.kernel",
    level: int = logging.INFO,
    msg: str = "hello",
    metadata: dict[str, object] | None = None,
) -> logging.LogRecord:
    record = logging.LogRecord(name, level, __file__, 0, msg, (), None)
    if metadata is not None:
        record.metadata = metadata
    return record


# ---------------------------------------------------------------------------
# LevelFilter
# ---------------------------------------------------------------------------


def test_level_filter_drops_records_below_minimum() -> None:
    filt = LevelFilter(logging.WARNING)
    assert filt.filter(_make_record(level=logging.INFO)) is False
    assert filt.filter(_make_record(level=logging.WARNING)) is True
    assert filt.filter(_make_record(level=logging.ERROR)) is True


# ---------------------------------------------------------------------------
# ComponentFilter
# ---------------------------------------------------------------------------


def test_component_filter_matches_exact_and_child_loggers() -> None:
    filt = ComponentFilter("shadow.kernel")
    assert filt.filter(_make_record(name="shadow.kernel")) is True
    assert filt.filter(_make_record(name="shadow.kernel.bootstrap")) is True
    assert filt.filter(_make_record(name="shadow.plugins")) is False
    # A component sharing a prefix but not a dotted child must not match.
    assert filt.filter(_make_record(name="shadow.kernel_extra")) is False


# ---------------------------------------------------------------------------
# SensitiveDataFilter
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "sensitive_key",
    ["api_key", "password", "secret", "access_token", "credential", "API_KEY"],
)
def test_sensitive_data_filter_redacts_matching_keys(sensitive_key: str) -> None:
    filt = SensitiveDataFilter()
    record = _make_record(metadata={sensitive_key: "super-secret-value", "user_id": "u-1"})

    assert filt.filter(record) is True

    metadata = record.metadata  # type: ignore[attr-defined]
    assert metadata[sensitive_key] == "***REDACTED***"
    assert metadata["user_id"] == "u-1"


def test_sensitive_data_filter_redacts_nested_dicts_and_lists() -> None:
    filt = SensitiveDataFilter()
    record = _make_record(
        metadata={"auth": {"password": "hunter2"}, "sessions": [{"token": "abc"}]}
    )

    filt.filter(record)

    metadata = record.metadata  # type: ignore[attr-defined]
    assert metadata["auth"]["password"] == "***REDACTED***"
    assert metadata["sessions"][0]["token"] == "***REDACTED***"


def test_sensitive_data_filter_redacts_whole_value_when_key_itself_is_sensitive() -> None:
    """A key matching a marker (e.g. "tokens") is redacted wholesale, without
    recursing into it — the marker match takes priority."""
    filt = SensitiveDataFilter()
    record = _make_record(metadata={"tokens": [{"id": "t-1"}]})

    filt.filter(record)

    assert record.metadata["tokens"] == "***REDACTED***"  # type: ignore[attr-defined]


def test_sensitive_data_filter_ignores_records_without_metadata() -> None:
    filt = SensitiveDataFilter()
    record = _make_record()
    assert filt.filter(record) is True


# ---------------------------------------------------------------------------
# DuplicateSuppressionFilter
# ---------------------------------------------------------------------------


def test_duplicate_suppression_filter_drops_repeats_within_window() -> None:
    filt = DuplicateSuppressionFilter(window_seconds=60.0)
    first = _make_record(msg="disk almost full")
    second = _make_record(msg="disk almost full")

    assert filt.filter(first) is True
    assert filt.filter(second) is False


def test_duplicate_suppression_filter_allows_distinct_messages() -> None:
    filt = DuplicateSuppressionFilter(window_seconds=60.0)
    assert filt.filter(_make_record(msg="one")) is True
    assert filt.filter(_make_record(msg="two")) is True


def test_duplicate_suppression_filter_allows_repeats_after_window_expires() -> None:
    filt = DuplicateSuppressionFilter(window_seconds=0.01)
    assert filt.filter(_make_record(msg="repeat me")) is True

    import time

    time.sleep(0.02)
    assert filt.filter(_make_record(msg="repeat me")) is True
