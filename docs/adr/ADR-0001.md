# ADR-0001: Domain-Separation Fixes Across the Low-Level Design

**Status:** Accepted
**Date:** 2026-07-20
**Related Documents:** `architecture/system-overview.md`, `architecture/lld/infrastructure/exceptions.md`, `architecture/lld/infrastructure/filesystem.md`, `architecture/lld/infrastructure/logging.md`, `architecture/lld/infrastructure/security.md`, `architecture/lld/infrastructure/serialization.md`, `architecture/lld/action/README.md`, `architecture/lld/cognition/README.md`, `architecture/lld/cognition/orchestration.md`, `architecture/lld/cognition/memory-access.md`

---

# Context

The full Low-Level Design (39 files across `kernel/`, `infrastructure/`, `perception/`, `cognition/`, `action/`, `memory/`) was written before any implementation began. Before starting Milestone 1 ("Phase 0: Foundation"), the LLD was reviewed end-to-end for internal consistency against `architecture/system-overview.md`'s core rule: domains are strictly separated and communicate only through the immutable Event Bus, never through direct imports or calls.

That review found six categories of conflict. This ADR documents what was found, what was decided, and why — before any code existed, so no decision here required reversing shipped code.

---

# Problem Statement

1. **Misplaced modules.** `infrastructure/exceptions.md`'s package structure listed Kernel's and Configuration's modules (`kernel.py`, `configuration.py`, `scheduler.py`, `events.py`, `plugins.py`) as flat files inside `shadow/infrastructure/`, contradicting the dedicated `kernel/README.md` and `infrastructure/configuration.md`, which each place those modules elsewhere.
2. **Filename collisions.** `infrastructure/filesystem.md`, `logging.md`, `security.md`, and `serialization.md` each declared their own submodules (`manager.py`, `validator.py`, etc.) as flat siblings directly inside `shadow/infrastructure/`. `filesystem.md` and `security.md` both declared `validator.py` at that same flat path — a literal collision.
3. **Circular dependency.** `action/README.md` listed Cognition as a direct dependency of Action. `cognition/README.md` explicitly forbade Cognition depending on Action. `cognition/orchestration.md` (a Cognition sub-component) then listed Action as a direct dependency anyway — contradicting its own domain's README and creating an Action → Cognition → Action cycle.
4. **Duplicate memory implementation.** The top-level Memory domain (`memory/episodic.md`, `memory/semantic.md`, `memory/short-term.md`, etc.) already owns `EpisodicMemory`, `SemanticMemory`, and `ShortTermMemory` under `shadow/memory/`. `cognition/memory-access.md` independently re-implemented `EpisodicMemory`, `SemanticMemory`, `WorkingMemory`, and a full `MemoryManager` with its own storage adapters under `shadow/cognition/memory/` — the same responsibility, owned twice.
5. **Competing schedulers.** `kernel/scheduler.md` claimed ownership of "every runtime job registered with the system," yet `cognition/orchestration.md` and `action/workflows.md` each defined their own, separately named `Scheduler`-class components with no stated relationship to the Kernel's.
6. **Ambiguous "depends on" language.** Every domain's Scope section states communication is Event-Bus-only, but most "Dependencies" sections read like direct API/import dependencies. This ambiguity is the root cause of #3, and was addressed wherever it produced an actual cycle rather than rewritten everywhere.

---

# Decision

All decisions below apply the same rule: **the Kernel and domain READMEs (`kernel/README.md`, `cognition/README.md`, `action/README.md`, `memory/README.md`) are the authority on domain ownership and dependency direction. A sub-component LLD file may never contradict its own domain's README.**

1. **Exceptions is a standalone top-level package**, `shadow/exceptions/`, alongside `shadow/config/` — not nested inside `shadow/infrastructure/`, `shadow/kernel/`, or `shadow/config/`, all of which depend on it and therefore cannot contain it. `base.py` holds `ShadowError` and shared metadata models; one file per raising domain (`kernel.py`, `configuration.py`, etc.) holds that domain's exception subclasses. The filename indicates which domain *raises* the error, not where the file physically lives.

2. **Every Infrastructure component gets its own subpackage.** `shadow/infrastructure/filesystem/`, `shadow/infrastructure/logging/`, `shadow/infrastructure/security/`, `shadow/infrastructure/serialization/` — each nested, none flat. This is the standard fix for sibling-file collisions and requires no further special-casing as new Infrastructure components are added; the rule is now "every component is a subpackage," full stop.

3. **Action and Cognition communicate only through the Event Bus, with no import dependency in either direction on the other.** Concretely:
   - `action/README.md`: Action no longer lists Cognition as a dependency. It documents that it receives execution requests exclusively as events (published by Cognition's Orchestrator) and publishes results the same way.
   - `cognition/orchestration.md`: the Orchestrator no longer lists Action as a dependency. Its Dispatcher's possible destinations no longer include Action. Its execution flow step "Invoke Action (Optional)" is now "Publish Execution Request Event (Optional — consumed by Action)."
   - This is not a documentation-only fix — it removes an actual import cycle that would have existed in code.

4. **Cognition's memory component is a thin client, not a second Memory implementation.** `cognition/memory-access.md` was rewritten in full: renamed `shadow/cognition/memory/` → `shadow/cognition/memory_access/`; removed `WorkingMemory`, `EpisodicMemory`, `SemanticMemory`, `MemoryManager`, and the direct vector/graph/relational-DB adapter; replaced with `MemoryAccessClient`, `MemoryQueryTranslator`, `ContextBuilder`, `RankingHintProvider`, and `CognitiveSessionContext` — all of which delegate reads and writes to `shadow/memory/`'s public Retrieval and write APIs. Cognition now has exactly one thing it owns here: the session-scoped pointer list to memories it's currently using, not the memories themselves.

5. **Orchestration's scheduler is renamed and scoped down to avoid ownership confusion.** `cognition/orchestration.md`'s `Scheduler` → `PlanStepScheduler`, with an explicit note: it only orders steps within a single Cognition request and does not own timers or system jobs — those go through the Kernel's `Scheduler`. Action's `workflows.md` already used a distinctly named `StepScheduler` at a different granularity (workflow steps vs. plan steps), so no rename was needed there — only the clarifying relationship to the Kernel Scheduler.

6. **"Depends on" ambiguity is not resolved globally.** We did not rewrite every LLD file's Dependencies section to distinguish "imports and calls directly" from "communicates with via events" — that would have been a large, low-value pass. It was fixed specifically everywhere it produced an actual cycle (item 3). Future LLD authors should default to event-mediated communication between domains and reserve direct dependencies for intra-domain components or domain → Infrastructure/Kernel calls, which are one-directional by construction.

---

# Alternatives Considered

- **Leave `shadow/cognition/memory/` as-is and treat it as "Cognition's private cache of Memory data."** Rejected — a private cache that duplicates class names and write paths with the domain it's caching from is not a cache, it's a second source of truth, and the LLD as written gave it its own storage adapters, which is a real duplication, not a caching pattern.
- **Let Action depend on Cognition directly, since "Cognition decides, Action executes" is a real one-directional relationship conceptually.** Rejected — the *conceptual* relationship is one-directional, but the LLD as written also had Cognition's Orchestrator depending on Action, which made the *implementation* relationship circular. Event-Bus-mediation preserves the one-directional conceptual relationship without creating an import cycle.
- **Flatten Infrastructure into fewer, larger files instead of one subpackage per component, to reduce folder depth.** Rejected — the entire reason for the collision was flat files; fewer, larger files would still collide once any two components define a same-named class.

---

# Consequences

- No `shadow/` code needed to be written or reverted — all six fixes landed before Milestone 1, Issue 1 implementation began.
- `docs/architecture/lld/cognition/README.md`'s package listing was updated (`memory/` → `memory_access/`) to stay consistent with the rewritten `memory-access.md`.
- Future LLD additions for new Cognition or Action sub-components should be checked against their domain README's Dependencies section before being accepted, specifically for accidental reintroduction of a cross-domain import.
- The Memory subsystem (`shadow/memory/`) is now unambiguously the only owner of memory storage in the codebase; any future LLD proposing to store memory-like data elsewhere should be treated as a domain-separation violation by default, not a judgment call each time.

---

# Superseded By

Not superseded.