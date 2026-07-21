from __future__ import annotations

import json
from pathlib import Path

import pytest

from shadow.config import get_manager, get_settings
from shadow.config.errors import ConfigError, ConfigLoadError, ConfigValidationError
from shadow.config.loader import ConfigurationLoader, discover_config_path
from shadow.config.models import ApplicationSettings
from shadow.config.settings import ConfigurationManager

# ---------------------------------------------------------------------------
# Default loading
# ---------------------------------------------------------------------------


def test_loads_defaults_with_no_file_and_no_env(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)  # no shadow.yaml here
    manager = ConfigurationManager()
    settings = manager.load()

    assert isinstance(settings, ApplicationSettings)
    assert settings.environment == "development"
    assert settings.debug is False
    assert settings.logging.level == "INFO"
    assert settings.kernel.startup_timeout_seconds == 30.0


def test_zero_config_startup_works_via_singleton(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    settings = get_settings()
    assert settings.scheduler.max_concurrent_jobs == 10


# ---------------------------------------------------------------------------
# YAML parsing
# ---------------------------------------------------------------------------


def test_yaml_file_overrides_defaults(tmp_path: Path) -> None:
    config_file = tmp_path / "shadow.yaml"
    config_file.write_text(
        "logging:\n  level: DEBUG\nkernel:\n  startup_timeout_seconds: 60\n",
        encoding="utf-8",
    )

    manager = ConfigurationManager(config_path=config_file)
    settings = manager.load()

    assert settings.logging.level == "DEBUG"
    assert settings.kernel.startup_timeout_seconds == 60.0
    # Untouched defaults remain intact (partial-section override)
    assert settings.logging.format == "json"


def test_missing_yaml_file_is_not_an_error(tmp_path: Path) -> None:
    manager = ConfigurationManager(config_path=tmp_path / "does-not-exist.yaml")
    settings = manager.load()
    assert settings.environment == "development"


def test_empty_yaml_file_is_not_an_error(tmp_path: Path) -> None:
    config_file = tmp_path / "shadow.yaml"
    config_file.write_text("", encoding="utf-8")
    manager = ConfigurationManager(config_path=config_file)
    settings = manager.load()
    assert settings.environment == "development"


def test_config_path_discovery_prefers_env_var(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    explicit = tmp_path / "custom.yaml"
    explicit.write_text("debug: true\n", encoding="utf-8")
    (tmp_path / "shadow.yaml").write_text("debug: false\n", encoding="utf-8")

    monkeypatch.setenv("SHADOW_CONFIG_PATH", str(explicit))
    monkeypatch.chdir(tmp_path)

    discovered = discover_config_path()
    assert discovered == explicit


# ---------------------------------------------------------------------------
# Environment overrides
# ---------------------------------------------------------------------------


def test_env_var_overrides_yaml_and_defaults(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    config_file = tmp_path / "shadow.yaml"
    config_file.write_text("logging:\n  level: DEBUG\n", encoding="utf-8")

    monkeypatch.setenv("SHADOW_LOGGING__LEVEL", "ERROR")

    manager = ConfigurationManager(config_path=config_file)
    settings = manager.load()

    assert settings.logging.level == "ERROR"


def test_env_var_boolean_and_number_coercion(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("SHADOW_DEBUG", "true")
    monkeypatch.setenv("SHADOW_SCHEDULER__MAX_CONCURRENT_JOBS", "25")

    manager = ConfigurationManager(config_path=tmp_path / "missing.yaml")
    settings = manager.load()

    assert settings.debug is True
    assert settings.scheduler.max_concurrent_jobs == 25


def test_top_level_env_var_with_no_section(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SHADOW_ENVIRONMENT", "production")
    manager = ConfigurationManager(config_path=tmp_path / "missing.yaml")
    settings = manager.load()
    assert settings.environment == "production"


# ---------------------------------------------------------------------------
# Validation (recoverable is implicit above; these are the fatal paths)
# ---------------------------------------------------------------------------


def test_invalid_environment_value_is_fatal(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("SHADOW_ENVIRONMENT", "not-a-real-environment")
    manager = ConfigurationManager(config_path=tmp_path / "missing.yaml")

    with pytest.raises(ConfigValidationError):
        manager.load()


def test_invalid_type_is_fatal(tmp_path: Path) -> None:
    config_file = tmp_path / "shadow.yaml"
    config_file.write_text("kernel:\n  startup_timeout_seconds: not-a-number\n", encoding="utf-8")

    manager = ConfigurationManager(config_path=config_file)
    with pytest.raises(ConfigValidationError):
        manager.load()


def test_malformed_yaml_is_fatal(tmp_path: Path) -> None:
    config_file = tmp_path / "shadow.yaml"
    config_file.write_text("kernel: [this is not valid: yaml\n", encoding="utf-8")

    manager = ConfigurationManager(config_path=config_file)
    with pytest.raises(ConfigLoadError):
        manager.load()


def test_non_mapping_yaml_top_level_is_fatal(tmp_path: Path) -> None:
    config_file = tmp_path / "shadow.yaml"
    config_file.write_text("- just\n- a\n- list\n", encoding="utf-8")

    manager = ConfigurationManager(config_path=config_file)
    with pytest.raises(ConfigLoadError):
        manager.load()


def test_unreadable_config_path_raises_before_settings_exist(tmp_path: Path) -> None:
    # A directory, not a file, at the configured path should fail cleanly.
    bad_path = tmp_path / "a-directory"
    bad_path.mkdir()

    manager = ConfigurationManager(config_path=bad_path)
    with pytest.raises(ConfigLoadError):
        manager.load()


# ---------------------------------------------------------------------------
# Section lookup
# ---------------------------------------------------------------------------


def test_section_lookup(tmp_path: Path) -> None:
    manager = ConfigurationManager(config_path=tmp_path / "missing.yaml")
    manager.load()

    section = manager.section("logging")
    assert section.name == "logging"
    assert section.values["level"] == "INFO"


def test_unknown_section_raises_key_error(tmp_path: Path) -> None:
    manager = ConfigurationManager(config_path=tmp_path / "missing.yaml")
    manager.load()
    with pytest.raises(KeyError):
        manager.section("not-a-real-section")


def test_get_with_dotted_key(tmp_path: Path) -> None:
    manager = ConfigurationManager(config_path=tmp_path / "missing.yaml")
    manager.load()
    assert manager.get("logging.level") == "INFO"
    assert manager.get("does.not.exist", default="fallback") == "fallback"


def test_exists(tmp_path: Path) -> None:
    manager = ConfigurationManager(config_path=tmp_path / "missing.yaml")
    manager.load()
    assert manager.exists("logging.level") is True
    assert manager.exists("logging.nonexistent") is False


# ---------------------------------------------------------------------------
# Export (with secret redaction)
# ---------------------------------------------------------------------------


def test_export_json_redacts_sensitive_looking_keys(tmp_path: Path) -> None:
    config_file = tmp_path / "shadow.yaml"
    config_file.write_text(
        "security:\n  require_approval_for_actions: false\n",
        encoding="utf-8",
    )
    manager = ConfigurationManager(config_path=config_file)
    manager.load()

    exported = json.loads(manager.export(fmt="json"))
    assert exported["security"]["require_approval_for_actions"] is False


def test_export_redacts_key_named_field(tmp_path: Path) -> None:
    from shadow.config.settings import ExportManager

    exporter = ExportManager()
    redacted = exporter._redact({"api_key": "sk-super-secret", "level": "INFO"})
    assert redacted["api_key"] == "***REDACTED***"
    assert redacted["level"] == "INFO"


def test_export_yaml_format(tmp_path: Path) -> None:
    manager = ConfigurationManager(config_path=tmp_path / "missing.yaml")
    manager.load()
    exported = manager.export(fmt="yaml")
    assert "environment: development" in exported


def test_export_unsupported_format_raises(tmp_path: Path) -> None:
    manager = ConfigurationManager(config_path=tmp_path / "missing.yaml")
    manager.load()
    with pytest.raises(ValueError):
        manager.export(fmt="toml")  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# Freezing / immutability
# ---------------------------------------------------------------------------


def test_settings_are_frozen_and_reject_mutation(tmp_path: Path) -> None:
    manager = ConfigurationManager(config_path=tmp_path / "missing.yaml")
    settings = manager.load()

    from pydantic import ValidationError as PydanticValidationError

    with pytest.raises(PydanticValidationError):  # frozen model rejects attribute assignment
        settings.debug = True  # type: ignore[misc]


def test_reload_is_not_supported(tmp_path: Path) -> None:
    manager = ConfigurationManager(config_path=tmp_path / "missing.yaml")
    manager.load()
    with pytest.raises(NotImplementedError):
        manager.reload()


def test_second_load_call_is_idempotent(tmp_path: Path) -> None:
    manager = ConfigurationManager(config_path=tmp_path / "missing.yaml")
    first = manager.load()
    second = manager.load()
    assert first is second


def test_accessing_settings_before_load_raises(tmp_path: Path) -> None:
    manager = ConfigurationManager(config_path=tmp_path / "missing.yaml")
    with pytest.raises(ConfigError):
        _ = manager.settings


def test_singleton_returns_same_instance_across_calls(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    first = get_manager()
    second = get_manager()
    assert first is second


# ---------------------------------------------------------------------------
# Loader-level merge behavior
# ---------------------------------------------------------------------------


def test_loader_deep_merges_nested_sections(tmp_path: Path) -> None:
    config_file = tmp_path / "shadow.yaml"
    config_file.write_text("plugins:\n  enabled: false\n", encoding="utf-8")

    merged = ConfigurationLoader(config_path=config_file).load()

    assert merged["plugins"]["enabled"] is False
    # plugin_dirs default should survive since only `enabled` was overridden
    assert merged["plugins"]["plugin_dirs"] == ["plugins"]
