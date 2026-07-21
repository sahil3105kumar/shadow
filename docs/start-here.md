# Start Here

> This is the one page you read before anything else. Everything else in `docs/` is reference material you dip into, not a book you read cover to cover.

---

# What Shadow is, in one paragraph

Shadow is a self-hosted, privacy-first Cognitive Operating System. A domain-blind Kernel routes immutable events between four domains — Perception (what happened), Cognition (what it means / what to do), Action (how to safely do it), and Infrastructure (storage, security, logging) — that never call each other directly. If you only read one more document after this one, read `architecture/system-overview.md`.

---

# The docs folder is layered, not linear

```text
docs/
├── start_here.md          ← you are here
├── product/                why Shadow exists — read once, rarely revisited
├── architecture/
│   ├── system-overview.md  the constitution — read once, fully
│   ├── event-spec.md       how domains talk — read once, fully
│   ├── data-model.md       what owns what data — read once, fully
│   ├── event-catalog.md    the actual event names in use — check before adding a new one
│   ├── plugin-system.md
│   ├── security.md
│   ├── hld/                 one README per domain — read the one you're about to touch
│   └── lld/                  one file per component — reference only, opened per GitHub issue
├── engineering/              how we work — branch/PR/testing conventions
└── adr/                      why we made specific calls — read when you need the "why"
```

You should never need to hold all of `lld/` in your head at once. That's the mistake that made this feel overwhelming the first time through. The LLD is a reference shelf, not a novel.

---

# The reading order (once, at the start of the project)

1. `product/vision.md`, `product/principles.md` — skim, you already know these.
2. `architecture/system-overview.md` — read fully. This is the one document that, if you internalize it, makes every LLD file predictable before you even open it.
3. `architecture/event-spec.md` — read fully. Every cross-domain interaction in this project is an event; this is the only communication mechanism.
4. `architecture/data-model.md` — read fully. Tells you which domain owns which entity, so you never duplicate storage (see ADR-0001 for what happens when that rule gets missed).

That's it. Everything past this point is per-issue lookup, not upfront reading.

---

# The loop you actually live in while building

```text
Pick the next open issue in the current GitHub milestone
        │
        ▼
Open only the HLD file for that issue's domain (if you haven't already)
        │
        ▼
Open only the LLD file(s) that match the issue
        │
        ▼
Implement + test against that spec
        │
        ▼
Update architecture/event-catalog.md if you introduced a new event
        │
        ▼
Open a PR (see engineering/ + .github/pull_request_template.md)
        │
        ▼
Move to the next issue
```

You do not re-read the whole `lld/` tree per issue. You open the one or two files that match. If something in the LLD contradicts `system-overview.md` or another LLD file, that's a conflict — write an ADR resolving it (see `adr/README.md`) before implementing, don't silently pick one.

---

# Where we are right now

- **Milestone 1 — "Phase 0: Foundation"** is the active milestone. 12 issues, in dependency order: Configuration → Logging → Dependency Injection → Event Bus → Plugin Framework → Kernel Bootstrap & Lifecycle → Testing Infrastructure → CI Pipeline → Docker Dev Environment → CLI → Exception Framework → Phase 0 Integration & Validation.
- Only Kernel and Infrastructure HLD/LLD are relevant right now. Perception, Cognition, Action, and Memory HLD/LLD exist already (Phases 2–4+) but are not needed until their milestone opens — don't pre-read them.
- `docs/adr/ADR-0001-*.md` documents the domain-separation conflicts found and fixed in the LLD before any code was written, and why.

---

# If you get lost again

Come back to this file. It is the map. Everything else is territory you visit as needed.