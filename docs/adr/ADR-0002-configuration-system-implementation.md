# ADR-0002: Configuration System Implementation

**Status:** Accepted
**Date:** 2026-07-21
**Related Documents:** `architecture/lld/infrastructure/configuration.md`, `ADR-0001.md`

---

# Context

Milestone 1 ("Phase 0: Foundation"), Issue 1: implement the Configuration System per `architecture/lld/infrastructure/configuration.md`. This is the first line of code written for Shadow — every other Phase 0 issue (Logging, DI Container, Event Bus, Plugin Framework, Kernel Bootstrap, ...) depends on it.

Two implementation questions were not fully pinned down by the LLD alone and needed a decision before writing code:

1. The LLD says Configuration depends on Exceptions, but the Exception Framework is a later issue in this same milestone (Issue 12).
2. The LLD lists broad future configuration sections (LLM, Perception, Cognition, Action, API, CLI, Storage, Filesystem, Health Monitor) alongside the Phase 0 sections (Application, Kernel, Logging, Plugins, Scheduler, Security).

---

# Decision

## Sequencing around the Exceptions dependency

Implemented `shadow/config/errors.py` with three minimal local exceptions (`ConfigError`, `ConfigLoadError`, `ConfigValidationError`) scoped to this package only, rather than building the full Exception Framework early or reordering the milestone.

The module docstring states explicitly that these are stand-ins to be re-parented under `shadow.exceptions.configuration` once Issue 12 lands, without changing their public names — so nothing importing `shadow.config.errors` today has to change when that happens.

## Scope: only Phase 0 sections are modeled

`shadow/config/models.py` implements exactly the sections in the LLD's Data Models list: `ApplicationSettings` (root), `KernelSettings`, `LoggingSettings`, `PluginSettings`, `SchedulerSettings`, `SecuritySettings`. The broader "Configuration" section list (LLM, Perception, Cognition, Action, API, CLI, Storage, Filesystem, Health Monitor) is deferred to whichever milestone introduces that subsystem, following the same pattern established here. Building those now would mean guessing at fields no issue has specified yet.

## Precedence and format

YAML confirmed as the only file format for now (per earlier direction — no TOML). Precedence is Defaults → YAML file → Environment variables, implemented as three `ConfigurationProvider` subclasses (`DefaultProvider`, `YamlProvider`, `EnvironmentProvider`) merged in that order by `ConfigurationLoader`. A missing YAML file is not an error — zero-config startup is required by the "local-first" principle; a malformed one is fatal.

Environment variable convention: `SHADOW_<SECTION>__<KEY>` (double underscore as the nesting delimiter), e.g. `SHADOW_LOGGING__LEVEL=DEBUG`. Chosen over a single underscore to avoid ambiguity with section/key names that themselves contain underscores (e.g. `startup_timeout_seconds`).

## Immutability

`ApplicationSettings` and all section models are frozen Pydantic models (`model_config = {"frozen": True}`). `ConfigurationManager.reload()` raises `NotImplementedError` rather than silently no-op-ing or attempting a partial reload — live reload remains a documented Future Extension, not current scope, and a loud failure is safer than a method that looks like it works but doesn't.

## Access pattern

`shadow.config.get_settings()` / `get_manager()` provide a process-wide singleton for normal use; `ConfigurationManager` can also be instantiated directly (used throughout the test suite) for isolated construction without touching global state.

---

# Alternatives Considered

- **Build the real Exception Framework now, out of milestone order, since Configuration formally depends on it.** Rejected — this would silently reorder the milestone and enlarge this PR beyond Issue 1's actual scope. Local stub exceptions are cheap and explicitly temporary.
- **Model every configuration section listed in the LLD's "Configuration" section now, so later phases don't need to touch `models.py` again.** Rejected — fields for Perception/Cognition/Action/LLM sections don't exist yet in any LLD with enough detail to type correctly; guessing them now risks the same kind of premature-detail conflict ADR-0001 already resolved once.
- **Support TOML as well as YAML.** Rejected per earlier explicit direction — YAML only.

---

# Consequences

- Every later Phase 0 issue (Logging, DI Container, Event Bus, Plugin Framework, Kernel Bootstrap) can now depend on `shadow.config.get_settings()` for its own configuration section.
- When Issue 12 (Exception Framework) lands, `shadow/config/errors.py` needs a follow-up change to re-parent its three exceptions under the shared `ShadowError` base — tracked here so it isn't forgotten.
- Adding a new configuration section for a later phase means adding a new `BaseModel` in `models.py`, wiring it into `ApplicationSettings`, and adding its defaults to `defaults.py` — no changes needed to `loader.py`, `providers.py`, or `settings.py`.

---

# Superseded By

Not superseded.

---

# Addendum (2026-07-21): Local Development Tooling Fixes

After the initial implementation, running `pre-commit` locally surfaced tooling issues unrelated to the Configuration System's own code but blocking on every commit. Documented here since they affect how every future issue gets committed, not just this one.

## Problem

- `pre-commit`'s `mirrors-mypy` hook runs mypy inside its own isolated virtualenv, built only from that hook's `additional_dependencies` — it does not see the project's `uv`-managed venv or `pyproject.toml` dependencies at all. Even after `uv sync` installed `pydantic`, `pydantic-settings`, and `types-PyYAML` correctly into the project venv, the mypy hook still failed with `Library stubs not installed for "yaml"`, because it was running in a different, smaller environment that never had them.
- With `pydantic` unavailable to that isolated environment, mypy also could not correctly infer `ApplicationSettings.model_validate()`'s return type, and flagged an unrelated `# type: ignore` comment as unused.
- `pyproject.toml`'s dev dependency group listed `mypy>=2.3.0` — mypy has no 2.x release; this was very likely a typo for a 1.x constraint and would have caused a resolution failure or unexpected version pull independent of the environment issue above.
- No `[tool.mypy]` configuration existed, so mypy was not running with the Pydantic plugin (`pydantic.mypy`), which is what lets it understand frozen models and field defaults precisely rather than treating `BaseModel` subclasses as generic classes.

## Decision

- Replaced the `mirrors-mypy` pre-commit repo entry with a **local** hook that runs `uv run mypy` under `language: system`, so mypy always executes inside the project's actual `uv`-managed venv rather than a separate hook-managed one. This removes the need to duplicate/maintain a separate `additional_dependencies` list in sync with `pyproject.toml` going forward — whatever `uv sync` installs is what mypy sees.
- Added `[tool.mypy]` with `plugins = ["pydantic.mypy"]` and `strict = true`, plus a `[tool.pydantic-mypy]` block, to `pyproject.toml`.
- Corrected the `mypy` version constraint in the dev dependency group.
- `ruff` and `ruff-format` hooks were left on the standard `ruff-pre-commit` mirror rather than converted to the same local/`uv run` pattern, since ruff has no project dependencies to stay in sync with — its isolated hook environment is not a source of drift the way mypy's was.

## Consequences

- The local mypy hook checks the whole `shadow/` package on every commit (`pass_filenames: false`) rather than only changed files, since single-file mypy runs can miss cross-file type errors — this is intentionally slower per-commit than the ruff hooks, which do run per-file.
- Anyone running `pre-commit` locally now needs `uv` installed and `uv sync` already run — already true for this project per `CONTRIBUTING.md`, so no new requirement in practice.
- Future issues that add new runtime or dev dependencies only need to update `pyproject.toml`; no parallel `additional_dependencies` list to remember to update for mypy.