# Event Specification

> *"Everything that happens inside Shadow is represented as an event."*

---

# Purpose

The Event Specification defines the communication model used throughout Shadow.

All domains communicate by publishing and subscribing to immutable events through the Event Bus.

This document defines event structure, lifecycle, delivery guarantees, naming conventions, and interaction patterns.

---

# Design Principles

The event system follows these principles:

* Event-driven architecture
* Loose coupling
* Immutable events
* Domain independence
* Asynchronous communication
* Replayability
* Observability
* Version compatibility

---

# Event Definition

An event represents a completed fact that occurred within the system.

Events describe **what happened**, never **what should happen**.

Examples:

* DocumentProcessed
* MemoryCreated
* TaskCompleted
* PluginLoaded
* ConversationStarted

---

# Event Structure

Every event consists of:

## Metadata

* Event ID
* Event Type
* Event Version
* Timestamp
* Source Domain
* Correlation ID
* Causation ID
* Producer
* Priority

---

## Payload

Contains the domain-specific data describing the event.

Payloads should contain only information required by subscribers.

---

## Context

Optional contextual information including:

* User
* Workspace
* Session
* Device
* Locale
* Environment

---

# Event Naming

Events use the format:

```text id="fq3qpa"
<Domain>.<PastTenseAction>
```

Examples:

```text id="es8j4q"
Document.Processed
Conversation.Started
Conversation.Ended
Memory.Created
Memory.Updated
Memory.Deleted
Knowledge.Linked
Task.Created
Task.Completed
Action.Executed
Plugin.Loaded
Plugin.Unloaded
System.Started
System.Stopped
```

Events describe completed actions.

Commands and requests are not events.

---

# Event Lifecycle

```text id="h1t8xe"
Something Happens
        │
        ▼
Event Created
        │
        ▼
Validation
        │
        ▼
Published
        │
        ▼
Event Bus
        │
        ▼
Subscribers
        │
        ▼
Processing
        │
        ▼
Completion
```

---

# Event Categories

## System Events

Examples:

* System.Started
* System.Stopped
* System.Updated

---

## Conversation Events

Examples:

* Conversation.Started
* Conversation.MessageReceived
* Conversation.Completed

---

## Perception Events

Examples:

* Document.Processed
* Audio.Transcribed
* Image.Analyzed
* Screen.Captured

---

## Memory Events

Examples:

* Memory.Created
* Memory.Updated
* Memory.Deleted
* Memory.Linked

---

## Knowledge Events

Examples:

* Entity.Created
* Relationship.Linked
* Graph.Updated

---

## Planning Events

Examples:

* Plan.Created
* Goal.Completed
* Task.Generated

---

## Action Events

Examples:

* Action.Started
* Action.Completed
* Action.Failed

---

## Plugin Events

Examples:

* Plugin.Loaded
* Plugin.Unloaded
* Plugin.Updated

---

## Infrastructure Events

Examples:

* Backup.Completed
* Sync.Completed
* Authentication.Succeeded
* Storage.Updated

---

# Event Delivery

The Event Bus shall provide:

* Ordered delivery within a stream
* At-least-once delivery
* Retry support
* Dead-letter handling
* Subscriber isolation

Subscribers should remain independent.

---

# Event Ordering

Ordering guarantees apply only within related event streams.

Global ordering is not required.

---

# Event Immutability

Published events are immutable.

Corrections must be represented by new events.

Historical events are never modified.

---

# Event Versioning

Each event contains an explicit version.

Versioning enables:

* Backward compatibility
* Schema evolution
* Independent domain upgrades

Breaking changes require a new event version.

---

# Correlation

Related events share a Correlation ID.

This enables tracking complete workflows across multiple domains.

Example:

```text id="hvcvcy"
Upload Document
        │
        ▼
Document.Processed
        │
        ▼
Memory.Created
        │
        ▼
Knowledge.Updated
        │
        ▼
Conversation.Responded
```

All events belong to the same correlation chain.

---

# Event Processing

Subscribers should:

* Validate payloads
* Process independently
* Handle duplicate delivery
* Publish resulting events
* Avoid blocking other subscribers

Processing should be idempotent whenever possible.

---

# Error Handling

Failures during processing shall:

* Be isolated
* Be logged
* Trigger retries when appropriate
* Publish failure events
* Preserve the original event

One subscriber failure must not affect others.

---

# Security

Events shall:

* Respect permission boundaries
* Avoid exposing sensitive information
* Preserve auditability
* Maintain integrity during transmission

Sensitive data should be referenced rather than embedded whenever practical.

---

# Observability

Every event should be traceable using:

* Event ID
* Correlation ID
* Causation ID
* Timestamp
* Producer
* Subscriber logs

The complete lifecycle of an event should be reconstructable.

---

# Extensibility

New event types may be introduced without affecting existing domains.

Domains should subscribe only to events relevant to their responsibilities.

No domain should require knowledge of another domain's internal implementation.

---

# Success Criteria

The event system succeeds when:

* Domains remain loosely coupled.
* Events provide a complete history of system behavior.
* Communication remains reliable and observable.
* New domains integrate without modifying existing ones.
* Every significant system change is represented as an immutable event.
