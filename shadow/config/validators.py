"""Configuration validator.

Turns the merged, untyped configuration dict into a validated
`ApplicationSettings` instance, or raises `ConfigValidationError`. Per the
LLD, validation is fatal-only: there is no partial/degraded config state
that lets the application continue starting.
"""

from __future__ import annotations

from typing import Any

from pydantic import ValidationError

from shadow.config.errors import ConfigValidationError
from shadow.config.models import ApplicationSettings


class ConfigurationValidator:
    """Validates a merged configuration dict into a typed `ApplicationSettings`."""

    def validate(self, merged_config: dict[str, Any]) -> ApplicationSettings:
        try:
            return ApplicationSettings.model_validate(merged_config)
        except ValidationError as exc:
            raise ConfigValidationError(self._format_errors(exc)) from exc

    @staticmethod
    def _format_errors(exc: ValidationError) -> str:
        lines = [f"Configuration validation failed with {exc.error_count()} error(s):"]
        for error in exc.errors():
            location = ".".join(str(part) for part in error["loc"])
            lines.append(f"  - {location}: {error['msg']}")
        return "\n".join(lines)
