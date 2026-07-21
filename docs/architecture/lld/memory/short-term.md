# Short-Term Memory Low-Level Design

## Purpose

The Short-Term Memory (STM) module maintains the active working context required for ongoing reasoning and task execution.

It provides fast, transient storage for information that is immediately relevant but does not necessarily warrant permanent persistence. The module enables Shadow to preserve conversational context, intermediate reasoning results, temporary variables, execution state, and active task information throughout a session.

Unlike Long-Term Memory, Short-Term Memory prioritizes speed, locality, and rapid updates over durability.

It answers one question:

> **"What information must Shadow keep available right now?"**

---

# Responsibilities

The Short-Term Memory module is responsible for:

- Maintaining active context.
- Storing temporary information.
- Session-scoped memory.
- Working memory management.
- Context updates.
- Temporary variable storage.
- Context expiration.
- Memory capacity management.
- Producing standardized memory artifacts.

The module is **not** responsible for:

- Persistent storage
- Knowledge archival
- Vector indexing
- Semantic organization
- Long-term learning

---

# Scope

Supported memory categories include:

```text
Conversation Context

Current Task

Intermediate Reasoning

Execution Variables

Temporary Facts

Current User Intent

Recent Tool Results

Active Workflow State
```

Supported operations include:

```text
Store

Retrieve

Update

Remove

Clear

Expire

Snapshot

Restore
```

Future capabilities include:

```text
Hierarchical Context

Adaptive Context Windows

Shared Session Memory

Cross-Agent Working Memory

Predictive Context Loading
```

---

# Package Structure

```text
shadow/
└── memory/
    └── short_term/
        ├── manager.py
        ├── session.py
        ├── context.py
        ├── eviction.py
        ├── snapshot.py
        ├── validation.py
        └── models.py
```

Expected classes:

```text
ShortTermMemory

SessionManager

ContextStore

EvictionPolicy

SnapshotManager

MemoryValidator
```

---

# Public API

```python
store()

retrieve()

update()

remove()

clear()

snapshot()

restore()

expire()
```

Every operation returns an immutable `MemoryArtifact`.

---

# Internal Components

The Short-Term Memory module consists of six logical components.

---

## Session Manager

Maintains session-specific memory.

Responsibilities include:

- session creation
- lifecycle management
- isolation
- cleanup

Each session owns an independent memory space.

---

## Context Store

Stores active memory records.

Capabilities include:

- insertion
- lookup
- update
- removal
- ordering

Optimized for low-latency access.

---

## Eviction Policy

Maintains bounded memory usage.

Supported policies include:

- Least Recently Used (LRU)
- Time-based expiration
- Capacity limits
- Priority-based retention

Eviction never affects persistent memory.

---

## Snapshot Manager

Creates temporary snapshots of working memory.

Supports:

- save
- restore
- rollback
- debugging

Snapshots are session-scoped.

---

## Memory Validator

Validates all memory operations.

Validation includes:

- session existence
- memory limits
- record integrity
- expiration rules

---

## Artifact Builder

Produces standardized execution artifacts.

Output:

```text
MemoryArtifact
```

---

# Class Design

```text
ShortTermMemory
│
├── SessionManager
├── ContextStore
├── EvictionPolicy
├── SnapshotManager
├── MemoryValidator
└── ArtifactBuilder
```

Only `ShortTermMemory` is publicly exposed.

---

# Data Models

Primary runtime models:

```text
WorkingMemoryRecord

SessionContext

TemporaryFact

ExecutionState

Snapshot

ContextWindow

MemoryArtifact
```

Example WorkingMemoryRecord:

```text
Memory ID

Session ID

Key

Value

Priority

Created Time

Last Accessed

Expiration
```

Example SessionContext:

```text
Session ID

Current Task

Conversation History

Tool Outputs

Variables

Metadata
```

---

# Design Decisions

## Session isolation

Each execution session maintains an independent working memory.

Information is never shared across unrelated sessions.

---

## Bounded capacity

Working memory is intentionally limited.

Capacity constraints prevent uncontrolled memory growth.

---

## Fast access

All common operations should complete in constant or near-constant time.

Retrieval speed is prioritized over storage efficiency.

---

## Automatic expiration

Temporary information expires automatically.

Applications should not manually manage memory cleanup.

---

## Snapshot support

Snapshots enable rollback during complex reasoning or workflow execution.

---

# Execution Flow

## Store Memory

```text
Receive Record

↓

Validate Session

↓

Check Capacity

↓

Insert Context

↓

Update Index

↓

Return Artifact
```

---

## Retrieve Memory

```text
Receive Query

↓

Locate Record

↓

Update Access Time

↓

Return Context
```

---

## Eviction

```text
Capacity Exceeded

↓

Select Victim

↓

Remove Record

↓

Update Metadata

↓

Continue Execution
```

---

# State Management

Memory lifecycle:

```text
Created

↓

Active

↓

Updated

↓

Expired
```

Terminal states:

```text
Expired

Removed

Evicted

Cleared
```

Working memory never becomes persistent without explicit consolidation.

---

# Error Handling

Recoverable:

- missing record
- expired context
- snapshot unavailable
- temporary capacity exhaustion

Fatal:

- invalid session
- corrupted context
- snapshot corruption
- memory integrity failure

Failures raise typed short-term memory exceptions.

---

# Concurrency Model

The Short-Term Memory module supports concurrent access.

Rules:

- reads execute concurrently
- writes are synchronized
- snapshots are atomic
- eviction is serialized
- session isolation is enforced

Consistency always takes precedence over throughput.

---

# Configuration

Supported configuration includes:

```text
Maximum Context Size

Session Timeout

Eviction Policy

Snapshot Limit

Memory Capacity

Expiration Time

Maximum Variables

Cleanup Interval
```

Configuration is loaded during application startup.

---

# Dependencies

The Short-Term Memory module depends on:

- Configuration
- Logging
- Event Bus

It communicates with:

- Cognition
- Workflow Engine

It does **not** depend on:

- Vector Store
- Long-Term Storage
- Perception
- Action

Long-term persistence occurs through the Consolidation module.

---

# Security Considerations

The Short-Term Memory module must:

- isolate session data
- validate memory ownership
- securely remove expired records
- prevent unauthorized access
- audit snapshot operations

Sensitive context should never persist beyond the session unless explicitly promoted.

---

# Performance Considerations

Design goals:

- O(1) retrieval
- O(1) insertion
- bounded memory growth
- efficient eviction
- minimal synchronization overhead

The module should sustain high-frequency updates without becoming a bottleneck.

---

# Testing Strategy

## Unit Tests

- insertion
- retrieval
- updates
- eviction
- expiration
- snapshots

---

## Integration Tests

- cognition integration
- workflow execution
- session lifecycle
- consolidation handoff

---

## Failure Tests

- session corruption
- snapshot failure
- concurrent writes
- memory exhaustion
- expiration edge cases

---

## Performance Tests

- high-frequency updates
- retrieval latency
- eviction throughput
- concurrent sessions
- snapshot overhead

---

# Future Extensions

The Short-Term Memory module should support future capabilities including:

- adaptive context sizing
- hierarchical working memory
- predictive context preloading
- multimodal working memory
- distributed session memory
- AI-assisted context pruning
- incremental snapshots
- context compression
- attention-aware memory prioritization
- collaborative working memory

These extensions should preserve the existing architecture while maintaining fast, deterministic, session-scoped, and reliable working memory management.