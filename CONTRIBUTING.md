# Contributing to Shadow

This is the practical companion to `docs/engineering/engineering.md`, which covers philosophy and standards. This file covers the commands you'll actually run.

New here? Read `docs/start_here.md` first — it explains how the rest of `docs/` is organized and how to avoid reading all of it before you can start.

---

## Setup

Requirements: Python 3.12+, [uv](https://docs.astral.sh/uv/) for dependency management.

```bash
git clone https://github.com/sahil3105kumar/shadow.git
cd shadow
uv sync --all-groups
```

This installs the dev dependency group: `mypy`, `ruff`, `pytest`, `pytest-asyncio`, `pytest-cov`, `pre-commit`, `structlog`, `typer`, `rich`, `pydantic`, `pydantic-settings`.

Set up pre-commit hooks once:

```bash
uv run pre-commit install
```

---

## Everyday commands

```bash
# Run the test suite
uv run pytest

# Run tests with coverage
uv run pytest --cov=shadow

# Lint
uv run ruff check .

# Auto-fix lint issues where possible
uv run ruff check . --fix

# Format
uv run ruff format .

# Type-check
uv run mypy shadow/
```

All four (`pytest`, `ruff check`, `ruff format --check`, `mypy`) must pass before a PR is merged — this is what the `.github/pull_request_template.md` checklist is asking about.

---

## Branching and commits

Branch naming, per `docs/engineering/engineering.md`:

```
feature/<short-description>
fix/<short-description>
refactor/<short-description>
docs/<short-description>
chore/<short-description>
release/<version>
```

Example: `feature/config-system`, `fix/event-bus-deadletter`.

Commit messages: a short imperative subject line, optionally followed by a body explaining *why* (not just *what* — the diff already shows what). See the `ADR-0001` commit in this repo's history for an example of a multi-file logical-change commit message.

---

## Picking up an issue

1. Check the current milestone on GitHub — work top-to-bottom within a milestone unless an issue is explicitly unblocked out of order.
2. Read `docs/start_here.md`'s "loop" section if you haven't already.
3. Open the matching HLD (`docs/architecture/hld/<domain>.md`) if you haven't touched that domain yet this session, then the specific LLD file(s) (`docs/architecture/lld/<domain>/<component>.md`) for the issue.
4. If the LLD contradicts `system-overview.md`, another LLD file, or an existing ADR — stop and write a new ADR resolving it before implementing. Don't silently pick an interpretation (see `docs/adr/ADR-0001-*.md` for the shape this takes).
5. If you introduce a new cross-domain event, add it to `docs/architecture/event-catalog.md` in the same PR.

---

## Pull requests

- One logical change per PR — matches the issue you picked up, not several.
- Fill out `.github/pull_request_template.md` fully; don't delete checklist items instead of checking or explaining them.
- Include tests for new code. `docs/engineering/testing.md` covers the testing strategy expected per component (unit / integration / failure / performance tiers, per the LLD's own "Testing Strategy" section for that component).
- Update the relevant doc if behavior changes: the matching LLD file if a component's actual interface diverges from what's documented, or `event-catalog.md` for new events.

---

## Where things live

| You're touching | Look here first |
|---|---|
| A new config key, exception type, or log format | `docs/architecture/lld/infrastructure/` |
| Kernel bootstrap, event bus, scheduler, plugin loading | `docs/architecture/lld/kernel/` |
| Anything cross-domain | `docs/architecture/event-spec.md` + `event-catalog.md` — never a direct import between domains |
| "Why was it built this way" | `docs/adr/` |

If you're unsure which domain owns something, check `docs/architecture/data-model.md` before guessing — domain ownership of data is documented, not inferred from convenience.

---

## Questions

Open a discussion or issue using `.github/ISSUE_TEMPLATE/architecture.md` for design questions, or `feature_request.md` / `bug_report.md` for the obvious cases.
