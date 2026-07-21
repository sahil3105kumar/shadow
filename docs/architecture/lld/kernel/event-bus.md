# Event Bus Low-Level Design

## Purpose

The Event Bus is the communication backbone of the Shadow runtime.

Its primary responsibility is to provide a decoupled, reliable, and deterministic mechanism for communication between independent components.

Every subsystem communicates through events rather than direct method calls wherever practical.

The Event Bus enables loose coupling, improves modularity, simplifies extensibility, and allows plugins to participate in system behavior without modifying existing code.

The Event Bus is not a message broker or distributed event streaming platform. It is an in-process runtime communication mechanism.

---

# Responsibilities

The Event Bus is responsible for:

- Publishing events.
- Delivering events to subscribers.
- Managing subscriptions.
- Supporting synchronous and asynchronous handlers.
- Preserving event ordering.
- Managing event priorities.
- Preventing duplicate subscriptions.
- Supporting event filtering.
- Providing delivery guarantees.
- Collecting event metrics.

The Event Bus is **not** responsible for:

- Business logic.
- Workflow orchestration.
- Scheduling.
- Retry policies for external APIs.
- Persistent event storage.
- Distributed messaging.

---

# Scope

The Event Bus exists as a singleton service inside the Kernel.

All runtime modules interact with the Event Bus through its public interface.

No module should communicate directly with another module unless absolutely necessary.

The preferred communication pattern is:

```text
Publisher

↓

Event Bus

↓

Subscribers
```

---

# Package Structure

```text
shadow/
└── kernel/
    └── event_bus.py
```

Expected classes:

```text
EventBus

Event

EventHandler

Subscription

EventDispatcher

SubscriptionRegistry

EventQueue

DeadLetterQueue

DispatchContext
```

---

# Public API

```python
publish(event)

publish_async(event)

subscribe(event_type, handler)

unsubscribe(event_type, handler)

has_subscribers(event_type)

clear_subscriptions()

shutdown()
```

The Event Bus exposes no internal implementation details.

---

# Internal Components

The Event Bus consists of seven logical components.

---

## Event Registry

Maintains metadata for all event types.

Tracks:

- event name
- version
- priority
- publisher
- schema

---

## Subscription Registry

Maintains every active subscription.

Tracks:

- subscriber
- event type
- priority
- execution mode
- filter

---

## Dispatcher

Responsible for delivering events.

Supports:

- synchronous dispatch
- asynchronous dispatch

---

## Event Queue

Temporary in-memory queue used for asynchronous events.

The queue is FIFO within each priority level.

---

## Dead Letter Queue

Stores events that could not be delivered.

Typical causes:

- handler exception
- invalid event
- unknown event type

Dead-letter events are logged for diagnostics.

---

## Metrics Collector

Collects runtime statistics.

Examples:

- events published
- events delivered
- failed deliveries
- queue depth
- handler latency

---

## Event Validator

Validates events before dispatch.

Checks:

- schema
- version
- metadata
- required fields

---

# Class Design

```text
EventBus
│
├── SubscriptionRegistry
├── EventDispatcher
├── EventQueue
├── DeadLetterQueue
├── MetricsCollector
└── EventValidator
```

Only `EventBus` is publicly visible.

Internal components remain private.

---

# Data Models

Primary runtime models:

```text
Event

EventMetadata

Subscription

DispatchResult

EventPriority

DeliveryMode

DeadLetterEvent

EventMetrics
```

---

## Event Structure

Every event contains two sections.

### Metadata

```text
Event ID

Event Type

Version

Timestamp

Correlation ID

Causation ID

Publisher

Priority
```

### Payload

The payload is event-specific.

The Event Bus treats payloads as opaque objects.

---

# Execution Flow

## Publishing

```text
Publisher

↓

Validate Event

↓

Determine Priority

↓

Lookup Subscribers

↓

Dispatch Event

↓

Collect Metrics

↓

Return
```

---

## Subscription

```text
Register Handler

↓

Validate Handler

↓

Store Subscription

↓

Ready
```

---

## Dispatch

```text
Receive Event

↓

Lookup Subscribers

↓

Sort by Priority

↓

Invoke Handlers

↓

Success?

↓

Yes

↓

Metrics Updated

No

↓

Dead Letter Queue
```

---

# State Management

The Event Bus has four operational states.

```text
Created

↓

Running

↓

Stopping

↓

Stopped
```

Only the Running state accepts new events.

Publishing events while Stopped raises an exception.

---

# Event Ordering

Event ordering is deterministic.

Rules:

- Events of the same priority are processed FIFO.
- Higher-priority events execute before lower-priority events.
- Handlers for a single event execute in registration order unless explicitly prioritized.
- A single event is never delivered twice to the same subscriber.

---

## Priority Levels

```text
Critical

High

Normal

Low
```

Critical events include:

- SystemStopping
- SystemFailed
- PluginFailed

Normal events include:

- MemoryCreated
- DocumentProcessed
- ConversationStarted

---

# Delivery Modes

Two delivery modes are supported.

---

## Synchronous

Publisher waits until every handler completes.

Use cases:

- lifecycle events
- startup
- shutdown
- validation

---

## Asynchronous

Publisher returns immediately.

Handlers execute independently.

Use cases:

- logging
- analytics
- notifications
- telemetry

---

# Error Handling

Recoverable:

- subscriber exception
- unknown optional subscriber
- queue overflow (configurable)

Fatal:

- corrupted event metadata
- invalid event schema
- dispatcher initialization failure

Subscriber failures must never terminate the Event Bus.

One failing subscriber must not prevent delivery to other subscribers.

---

# Concurrency Model

The Event Bus supports concurrent publishing.

Rules:

- Subscription changes are synchronized.
- Event publication is thread-safe.
- Event ordering is preserved within priority levels.
- Handlers may execute concurrently when safe.
- Lifecycle events are always dispatched synchronously.

The Event Bus must not introduce race conditions.

---

# Configuration

Supported configuration includes:

```text
Maximum Queue Size

Dispatch Mode

Maximum Handler Time

Dead Letter Queue Size

Metrics Enabled

Priority Levels

Async Worker Count

Event Validation

Tracing Enabled
```

Configuration is immutable after startup.

---

# Dependencies

The Event Bus depends on:

- Logging
- Exceptions
- Configuration

The Event Bus does **not** depend on:

- Scheduler
- Plugins
- Cognition
- Perception
- Action

Higher-level modules depend on the Event Bus.

---

# Security Considerations

The Event Bus must:

- validate every event
- reject malformed metadata
- prevent duplicate delivery
- isolate subscriber failures
- prevent unauthorized runtime mutation
- avoid exposing internal queues

Sensitive payloads should never be logged directly.

Only metadata should appear in runtime logs unless explicitly configured.

---

# Performance Considerations

Design goals:

- O(1) event publication
- O(1) subscriber lookup
- bounded queue growth
- minimal allocation
- predictable dispatch latency

The Event Bus should support thousands of events per second without becoming a bottleneck.

Long-running handlers must not block unrelated event delivery.

---

# Testing Strategy

## Unit Tests

- event publication
- subscription registration
- unsubscription
- priority ordering
- synchronous dispatch
- asynchronous dispatch
- event validation

---

## Integration Tests

- plugin subscriptions
- lifecycle events
- scheduler events
- health monitor events
- kernel startup events

---

## Failure Tests

- subscriber exceptions
- malformed events
- duplicate subscriptions
- queue overflow
- dead-letter handling

---

## Performance Tests

- publication throughput
- dispatch latency
- concurrent publishers
- queue saturation
- subscriber scalability

---

# Future Extensions

The Event Bus should support future capabilities including:

- wildcard subscriptions
- predicate-based filtering
- event replay
- persistent event storage
- distributed event transport
- remote subscribers
- event batching
- middleware/interceptors
- OpenTelemetry integration
- event tracing and visualization

These extensions should preserve the existing public API while maintaining deterministic, reliable event delivery.