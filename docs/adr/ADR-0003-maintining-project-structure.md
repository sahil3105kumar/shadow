# ADR-0002: Centralize Project Tooling Configuration in `pyproject.toml`

**Status:** Accepted  
**Date:** 2026-07-21  
**Related Documents:** `pyproject.toml`

---

# Context

Shadow uses several development tools throughout its development workflow, including Ruff for linting, MyPy for static type checking, and Pytest for testing.

Initially, MyPy and Pytest were configured inside `pyproject.toml`, while Ruff used a separate `ruff.toml` configuration file. Although this layout is fully supported, it distributes project tooling configuration across multiple files, making it less obvious where contributors should look when modifying project-wide development settings.

The Python ecosystem has standardized on `pyproject.toml` as the canonical location for project metadata and tool configuration. All tools currently used by Shadow support configuration from this file.

---

# Problem Statement

Maintaining a separate `ruff.toml` creates an unnecessary second source of configuration for development tooling.

Contributors must inspect multiple files to understand how the project's linting, formatting, testing, and type-checking behavior is configured. As additional tools are introduced, this fragmentation would continue to grow unless a consistent configuration strategy is adopted.

---

# Decision

Shadow adopts **`pyproject.toml` as the single source of truth for project tooling configuration** whenever a tool officially supports it.

As part of this decision:

- Ruff configuration is moved from `ruff.toml` into the `[tool.ruff]` section of `pyproject.toml`.
- Ruff linting rules are defined under `[tool.ruff.lint]`.
- The standalone `ruff.toml` file is removed.
- Existing MyPy and Pytest configurations remain in `pyproject.toml`.

Going forward, new development tools should also be configured in `pyproject.toml` whenever officially supported. Separate configuration files should only be introduced when a tool cannot be configured through `pyproject.toml` or when a dedicated configuration file provides a clear technical advantage.

---

# Alternatives Considered

## Continue using `ruff.toml`

Rejected.

While fully supported by Ruff, a separate configuration file provides no additional functionality and unnecessarily fragments project configuration.

## Use dedicated configuration files for every development tool

Rejected.

Although this isolates each tool's configuration, it increases maintenance overhead, makes project configuration less discoverable, and adds unnecessary files to the repository root.

---

# Consequences

- `pyproject.toml` becomes the canonical location for project tooling configuration.
- Contributors only need to inspect one file to understand the project's development tooling.
- Repository configuration becomes easier to review and maintain.
- The repository root contains fewer configuration files.
- Future tooling follows a consistent configuration convention.

---

# Superseded By

Not superseded.