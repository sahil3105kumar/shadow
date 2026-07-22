"""Strongly typed settings models for each configuration section.

Per the LLD's Data Models section, the primary runtime models are:
ApplicationSettings, KernelSettings, LoggingSettings, PluginSettings,
SchedulerSettings, SecuritySettings, plus the metadata/value models used by
the Configuration Registry.

Only the sections needed by Phase 0 (Foundation) are fully modeled here.
Later-phase sections (Perception, Cognition, Action, LLM, Storage, API, CLI,
Filesystem, Health Monitor) are intentionally out of scope for this issue and
should be added by whichever milestone introduces them, following the same
pattern.
"""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field, field_validator


class LogLevel(StrEnum):
    """Supported structured-logging levels."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogFormat(StrEnum):
    """Supported log output formats."""

    JSON = "json"
    CONSOLE = "console"


class KernelSettings(BaseModel):
    """Kernel bootstrap and lifecycle settings."""

    model_config = {"frozen": True}

    startup_timeout_seconds: float = Field(
        default=30.0,
        gt=0,
        description="Maximum time allowed for Kernel bootstrap before failing startup.",
    )
    shutdown_timeout_seconds: float = Field(
        default=15.0,
        gt=0,
        description="Maximum time allowed for graceful shutdown before forcing exit.",
    )


class LoggingSettings(BaseModel):
    """Structured logging settings."""

    model_config = {"frozen": True}

    level: LogLevel = Field(default=LogLevel.INFO, description="Minimum log level emitted.")
    format: LogFormat = Field(
        default=LogFormat.JSON,
        description="Log output format (json for machine-readable, console for humans).",
    )


class PluginSettings(BaseModel):
    """Plugin Framework settings."""

    model_config = {"frozen": True}

    enabled: bool = Field(default=True, description="Whether plugin loading is enabled at all.")
    plugin_dirs: list[str] = Field(
        default_factory=lambda: ["plugins"],
        description="Directories scanned for installable plugins, relative to the app root.",
    )


class SchedulerSettings(BaseModel):
    """Kernel Scheduler settings."""

    model_config = {"frozen": True}

    max_concurrent_jobs: int = Field(
        default=10,
        gt=0,
        description="Maximum number of system jobs the Kernel Scheduler runs concurrently.",
    )


class SecuritySettings(BaseModel):
    """Baseline security settings.

    Full Security System configuration (`docs/architecture/lld/infrastructure/security.md`)
    is a later milestone item; this only covers what Phase 0 needs to exist.
    """

    model_config = {"frozen": True}

    require_approval_for_actions: bool = Field(
        default=True,
        description="Whether consequential actions require human approval before execution.",
    )


class ApplicationSettings(BaseModel):
    """Root configuration model. The single object returned by the Configuration Manager."""

    model_config = {"frozen": True}

    environment: str = Field(default="development", description="Deployment environment name.")
    debug: bool = Field(
        default=False, description="Enables verbose/debug behavior across subsystems."
    )

    kernel: KernelSettings = Field(default_factory=KernelSettings)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)
    plugins: PluginSettings = Field(default_factory=PluginSettings)
    scheduler: SchedulerSettings = Field(default_factory=SchedulerSettings)
    security: SecuritySettings = Field(default_factory=SecuritySettings)

    @field_validator("environment")
    @classmethod
    def _environment_must_be_known(cls, value: str) -> str:
        allowed = {"development", "staging", "production", "test"}
        if value not in allowed:
            raise ValueError(f"environment must be one of {sorted(allowed)}, got {value!r}")
        return value


class ConfigurationMetadata(BaseModel):
    """Metadata describing a single configuration key, for introspection/export."""

    model_config = {"frozen": True}

    key: str
    source: str
    type_name: str
    default_value: Any = None
    current_value: Any = None
    description: str | None = None


class ConfigurationSection(BaseModel):
    """A named, immutable slice of the configuration tree, returned by `section()`."""

    model_config = {"frozen": True}

    name: str
    values: dict[str, Any]


class ConfigurationValue(BaseModel):
    """A single resolved configuration value with provenance, used internally by the Registry."""

    model_config = {"frozen": True}

    key: str
    value: Any
    source: str
    resolved_at: datetime = Field(default_factory=datetime.utcnow)
