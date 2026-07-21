# Memory Access Low-Level Design

## Purpose

The Memory Access component gives the Cognition subsystem a single, convenient interface for requesting relevant information from Shadow's Memory subsystem (`shadow/memory/`) and shaping it into context that Reasoning and Planning can consume.

It does **not** store, index, or persist memory itself. All storage — working/short-term memory, episodic memory, semantic memory, long-term memory, and vector search — is owned exclusively by the top-level Memory subsystem. Memory Access is a thin client over that subsystem's public Retrieval API, not a second implementation of it.

The Memory Access component answers one question:

> **"What information do I already know that is relevant to the current task?"**

It does **not** determine whether retrieved information is true or how it should be used.

Those responsibilities belong to the Reasoning Engine.

---

# Responsibilities

The Memory Access component is responsible for:

- Translating cognitive queries into Memory subsystem retrieval requests.
- Assembling ranked, budgeted context windows for Reasoning and Planning.
- Tracking which memory references are active in the current cognitive session.
- Forwarding "remember this" requests to the Memory subsystem's write API.
- Producing standardized context artifacts for downstream cognitive components.

The component is **not** responsible for:

- Reasoning
- Planning
- Knowledge retrieval (owned by the Knowledge component)
- Memory storage, indexing, or persistence
- Vector search implementation
- Embedding generation
- LLM inference

---

# Scope

Memory Access reads from and writes to the following memory domains, all owned by `shadow/memory/`:

```text
Short-Term Memory (shadow/memory/short_term)

Episodic Memory (shadow/memory/episodic)

Semantic Memory (shadow/memory/semantic)

Vector Store (shadow/memory/vector_store)
```

It owns none of them. It owns only the session-scoped view Cognition currently has into them.

Future capabilities include:

```text
Adaptive context budgeting

Cross-session memory hints

Personalized ranking weights

Predictive pre-fetching of likely-relevant memories
```

---

# Package Structure

```text
shadow/
└── cognition/
    └── memory_access/
        ├── __init__.py
        ├── client.py
        ├── context_builder.py
        ├── query_translator.py
        ├── ranking_hints.py
        ├── session.py
        └── models.py
```

Named `memory_access` (not `memory`) to make clear this package does not own memory storage — that remains `shadow/memory/`.

Expected classes:

```text
MemoryAccessClient

ContextBuilder

MemoryQueryTranslator

RankingHintProvider

CognitiveSessionContext
```

---

# Public API

```python
retrieve_context()

remember()

update_session()

clear_session()
```

Every request returns an immutable `ContextResult`.

---

# Internal Components

The Memory Access component consists of four logical components.

---

## Memory Query Translator

Converts a cognitive request (e.g. "what do I know about X for this task") into one or more retrieval requests against the Memory subsystem's public Retrieval Engine (`shadow/memory/retrieval`).

Does not query storage directly — always goes through Memory's Retrieval API.

---

## Context Builder

Takes the raw results returned by Memory's Retrieval Engine and assembles them into a ranked, size-budgeted context window suitable for Reasoning or the LLM component.

Responsibilities include:

- deduplicating overlapping results
- truncating to a configured token/size budget
- attaching provenance (which memory type each item came from)

Ranking itself is performed by Memory's Retrieval Engine; the Context Builder only applies Cognition-specific presentation and budgeting on top of already-ranked results.

---

## Ranking Hint Provider

Supplies Cognition-specific ranking preferences (e.g. "prefer recent episodic memory for this conversational task") as parameters passed into Memory's Retrieval Engine. It does not perform ranking itself.

---

## Cognitive Session Context

Tracks which memory references are currently active for the in-progress cognitive session — a lightweight, session-scoped pointer list, not a memory store. Session-scoped working state that must outlive a single request is written back to Memory's Short-Term Memory via the write API, not held here.

---

# Class Design

```text
MemoryAccessClient
│
├── MemoryQueryTranslator
├── ContextBuilder
├── RankingHintProvider
└── CognitiveSessionContext
```

Only `MemoryAccessClient` is publicly exposed.

---

# Data Models

Primary runtime models:

```text
ContextRequest

ContextResult

ContextItem

MemoryReference

SessionPointer
```

Example ContextItem:

```text
Source Memory Type

Memory Reference

Content

Relevance Score (as returned by Memory's Retrieval Engine)

Timestamp

Provenance
```

---

# Design Decisions

## Memory Access does not own storage

Every write and read is delegated to the Memory subsystem's public API. This is the core boundary that distinguishes Memory Access from Memory: Memory Access has no persistence layer of its own.

---

## Memory Access is a translation and shaping layer

Its job is API translation (cognitive intent → Memory API calls) and presentation (raw results → budgeted context), not memory management.

---

## Context is immutable

A `ContextResult` returned to Reasoning or Planning does not change after being built. A new request produces a new result.

---

## Session state is a pointer list, not a store

`CognitiveSessionContext` tracks references to memories, not the memories themselves. Anything that must persist beyond the current request is written through to Memory's Short-Term Memory.

---

# Execution Flow

## Context Retrieval

```text
Cognitive Query

↓

Translate to Memory Retrieval Request(s)

↓

Call Memory Subsystem Retrieval API

↓

Build Ranked, Budgeted Context

↓

Return ContextResult
```

---

## Remember Request

```text
Remember Request

↓

Validate Entry

↓

Forward to Memory Subsystem Write API

↓

Return Reference
```

---

## Session Update

```text
Session Event

↓

Update Session Pointer List

↓

Optionally Write Through to Short-Term Memory
```

---

# State Management

The Memory Access component is stateless beyond the current session's pointer list.

Session Context lifecycle:

```text
Created

↓

Active

↓

Detached

↓

Cleared
```

All persistent memory lifecycles (working, episodic, semantic, long-term) are managed exclusively by the Memory subsystem, not here.

---

# Error Handling

Recoverable:

- Memory subsystem returns no results
- partial retrieval across memory types
- low-confidence matches

Fatal:

- Memory subsystem retrieval API unavailable
- invalid context request

Failures raise typed Memory Access exceptions and are distinct from failures raised inside the Memory subsystem itself, which are propagated rather than reinterpreted.

---

# Concurrency Model

Memory Access supports concurrent context requests.

Rules:

- independent context requests execute concurrently
- calls into the Memory subsystem's Retrieval API may execute in parallel per query
- session pointer updates are synchronized
- context results are immutable once built

Concurrent access must preserve consistency with the underlying Memory subsystem's own concurrency guarantees.

---

# Configuration

Supported configuration includes:

```text
Context Size Budget

Default Ranking Hints

Session Timeout

Maximum Retrieved Items Per Query

Provenance Verbosity
```

Configuration is loaded during application startup.

---

# Dependencies

The Memory Access component depends on:

- Configuration
- Logging
- Serialization
- Security
- Memory (`shadow/memory/` — specifically its Retrieval Engine, Short-Term Memory, and Consolidation public write APIs)

It does **not** depend on:

- Planner
- Reasoning
- Action
- LLM

It does **not** implement memory storage, indexing, or persistence — see Design Decisions above. Higher-level cognitive components consume memory exclusively through this interface, and this interface consumes the Memory subsystem exclusively through its public API.

---

# Security Considerations

The Memory Access component must:

- enforce memory access permissions before forwarding requests to Memory
- isolate user sessions
- prevent unauthorized retrieval
- sanitize context before it reaches Reasoning or the LLM component
- securely expire session pointers

Memory Access relies on the Memory subsystem's own access controls for data-at-rest protection; it does not duplicate them.

---

# Performance Considerations

Design goals:

- low-latency context assembly
- minimal overhead on top of the Memory subsystem's own retrieval latency
- efficient budgeting/truncation
- bounded session pointer list size

Memory Access should add negligible overhead relative to the Memory subsystem's own retrieval cost.

---

# Testing Strategy

## Unit Tests

- query translation
- context building and budgeting
- ranking hint construction
- session pointer lifecycle

---

## Integration Tests

- Memory subsystem Retrieval Engine integration
- Memory subsystem write-through (remember requests)
- cognition orchestration integration

---

## Failure Tests

- Memory subsystem unavailable
- empty retrieval results
- oversized context requests
- expired sessions

---

## Performance Tests

- context assembly latency
- concurrent request handling
- session pointer list growth under load

---

# Future Extensions

The Memory Access component should support future capabilities including:

- adaptive context budgeting based on downstream component
- cross-session memory hints
- personalized ranking weight profiles
- predictive pre-fetching of likely-relevant memories

These extensions should preserve the existing boundary: Memory Access shapes and routes; the Memory subsystem stores and retrieves.