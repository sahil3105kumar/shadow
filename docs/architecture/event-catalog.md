# Event Catalog

> Naming rules, payload shape, and delivery guarantees live in `event-spec.md`. This file is the actual, growing list of event names in use, so no two domains invent the same name for different things, or different names for the same thing.

---

# How to use this file

- **Adding a new event?** Append it to the table for your domain, in the same PR that introduces it. Follow the `<Domain>.<PastTenseAction>` convention from `event-spec.md`.
- **Before adding one, search this file first.** If something close already exists, prefer reusing or extending it over creating a near-duplicate.
- Events here are grouped by **publishing domain**, not by consumer. A row's "Consumed by" column may list multiple domains.
- Status:
  - `Implemented` — the event is actually published/consumed in code today.
  - `Planned` — reserved name for a milestone that hasn't started; listed here early to prevent collisions later.

---

# Kernel Events

| Event | Payload (summary) | Consumed by | Status |
|---|---|---|---|
| `System.Started` | startup timestamp, config snapshot hash | Health Monitor, Logging | Planned (Milestone 1, Kernel Bootstrap issue) |
| `System.Stopped` | shutdown reason, uptime | Health Monitor, Logging | Planned |
| `Kernel.Bootstrapped` | container/service list initialized | Health Monitor | Planned |
| `Plugin.Loaded` | plugin id, version, manifest | Health Monitor, Logging | Planned (Milestone 1, Plugin Framework issue) |
| `Plugin.Unloaded` | plugin id, reason | Health Monitor, Logging | Planned |
| `Plugin.Failed` | plugin id, error | Health Monitor, Logging | Planned |

---

# Configuration Events

| Event | Payload (summary) | Consumed by | Status |
|---|---|---|---|
| `Configuration.Loaded` | source layers merged, redacted snapshot | Kernel, Logging, Health Monitor | Planned (Milestone 1, Configuration issue — Issue 1) |
| `Configuration.ValidationFailed` | offending key(s), reason | Kernel (fatal — halts bootstrap) | Planned |

Configuration is frozen after load (see `lld/infrastructure/configuration.md`), so there is intentionally no `Configuration.Updated` — live reload is a documented Future Extension, not current scope.

---

# Logging Events

Logging is a sink, not a publisher — see `lld/infrastructure/logging.md`. It has no events of its own.

---

# Exception Events

Exceptions represent failures, they don't publish events about themselves — see `lld/infrastructure/exceptions.md` ("The Exception Framework does not recover from failures. It only represents them."). Any domain that raises a `ShadowError` subclass is responsible for publishing its own `<Domain>.Failed`-style event where relevant (e.g. `Plugin.Failed` above), not the Exception Framework.

---

# Perception Events

| Event | Payload (summary) | Consumed by | Status |
|---|---|---|---|
| `Document.Processed` | document id, extracted metadata reference | Cognition, Memory | Planned (Phase 2) |
| `Audio.Transcribed` | transcript reference, language, duration | Cognition, Memory | Planned (Phase 2) |
| `Image.Analyzed` | image id, detected artifacts reference | Cognition, Memory | Planned (Phase 2) |
| `Screen.Captured` | capture id, timestamp | Cognition | Planned (Phase 2) |

---

# Memory Events

| Event | Payload (summary) | Consumed by | Status |
|---|---|---|---|
| `Memory.Created` | memory id, type (short-term/episodic/semantic), reference | Cognition (via Memory Access) | Planned (Phase 2) |
| `Memory.Updated` | memory id, version | Cognition (via Memory Access) | Planned (Phase 2) |
| `Memory.Deleted` | memory id, reason | Cognition (via Memory Access) | Planned (Phase 2) |
| `Memory.Linked` | source memory id, target memory id, relationship | Cognition (via Memory Access) | Planned (Phase 2) |

Cognition never queries Memory storage directly — it only ever consumes these through the Memory Access client's synchronous public API (`retrieve_context()`, `remember()`), or reacts to these events. See ADR-0001 for why Cognition does not own a second Memory implementation.

---

# Cognition Events

| Event | Payload (summary) | Consumed by | Status |
|---|---|---|---|
| `Conversation.Started` | conversation id, session context | Memory, Action | Planned (Phase 5) |
| `Conversation.MessageReceived` | message id, conversation id | Cognition internal, Memory | Planned |
| `Conversation.Completed` | conversation id, outcome summary | Memory | Planned |
| `Plan.Created` | plan id, step count | Action (indirectly, via Action.Requested below) | Planned |
| `Action.Requested` | execution request id, target Action domain (api/browser/desktop/filesystem/notifications/workflow), payload reference, correlation id | **Action** | Planned (Phase 5, see ADR-0001) |

`Action.Requested` is the concrete event that replaces the direct `Orchestrator → Action` call removed in ADR-0001. This is the **only** way Cognition ever triggers Action; there is no synchronous call path between the two domains.

---

# Action Events

| Event | Payload (summary) | Consumed by | Status |
|---|---|---|---|
| `Action.Started` | execution request id (correlates to `Action.Requested`) | Health Monitor, Logging | Planned (Phase 5) |
| `Action.Completed` | execution request id, `ExecutionArtifact` reference | Cognition, Memory | Planned |
| `Action.Failed` | execution request id, error, recoverable flag | Cognition, Memory | Planned |

---

# Infrastructure Events

| Event | Payload (summary) | Consumed by | Status |
|---|---|---|---|
| `Backup.Completed` | backup id, size, target | Logging | Planned (later phase) |
| `Sync.Completed` | device id, changeset summary | Logging | Planned (Phase 8, Distributed) |
| `Authentication.Succeeded` | principal id | Security audit log | Planned |
| `Storage.Updated` | affected keys/paths | Logging | Planned |

---

# Naming collisions to watch for

- **`Memory` (Kernel/Health Monitor context) vs. `Memory` (the domain).** Health Monitor's "monitored components" list refers to system resource memory, not the Memory domain — if a resource-memory event is ever added (e.g. for OOM warnings), do not name it `Memory.*`; use `Resource.MemoryPressure` or similar to avoid confusion with the Memory domain's event prefix.
- **`Plan.*` vs. `Action.Requested`.** `Plan.Created` (Cognition-internal, Planner → Orchestrator) is not the same as `Action.Requested` (Orchestrator → Action, cross-domain). Don't collapse these into one event — they cross a domain boundary at different points and have different consumers.