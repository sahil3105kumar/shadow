from __future__ import annotations

from collections.abc import Iterator

import pytest

import shadow.infrastructure.logging as shadow_logging


@pytest.fixture(autouse=True)
def _reset_logging_singleton() -> Iterator[None]:
    """Ensure the process-wide LoggingManager singleton doesn't leak across tests."""
    shadow_logging._reset_for_testing()
    yield
    shadow_logging._reset_for_testing()
