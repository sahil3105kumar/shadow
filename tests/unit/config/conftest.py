from __future__ import annotations

import os
from collections.abc import Iterator

import pytest

import shadow.config as shadow_config


@pytest.fixture(autouse=True)
def _clean_shadow_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Remove any SHADOW_* env vars leaking in from the host environment."""
    for key in list(os.environ):
        if key.startswith("SHADOW_"):
            monkeypatch.delenv(key, raising=False)


@pytest.fixture(autouse=True)
def _reset_config_singleton() -> Iterator[None]:
    """Ensure the process-wide ConfigurationManager singleton doesn't leak across tests."""
    shadow_config._reset_for_testing()
    yield
    shadow_config._reset_for_testing()
