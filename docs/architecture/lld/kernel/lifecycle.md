# Lifecycle Manager Low-Level Design

## Purpose

The Lifecycle Manager is responsible for controlling the operational state of the Shadow runtime.

It acts as the single authority for state transitions, ensuring every subsystem starts, operates, and shuts down in a deterministic and predictable manner.

Every runtime state transition must pass through the Lifecycle Manager.

The Lifecycle Manager guarantees that no subsystem can enter an invalid state.

---

# Responsibilities

The Lifecycle Manager is responsible for:

- Managing runtime state transitions.
- Starting the runtime.
- Stopping the runtime.
- Restarting the runtime.
- Suspending runtime activities.
- Resuming suspended services.
- Publishing lifecycle events.
- Coordinating graceful shutdown.
- Preventing illegal state transitions.
- Tracking runtime uptime and status.

The Lifecycle Manager is **not** responsible for:

- Creating services.
- Dependency resolution.
- Plugin discovery.
- Event dispatch.
- Scheduling.
- Health monitoring.

---

# Scope

The Lifecycle Manager owns the application's operational state from startup until termination.

It operates continuously after Bootstrap completes successfully.

Every subsystem must respect the lifecycle state before performing work.

---

# Package Structure

```text
shadow/
└── kernel/
    └── lifecycle.py
```

Expected classes:

```text
LifecycleManager

LifecycleState

LifecycleTransition

LifecycleContext
```

---

# Public API

```python
start()

stop()

restart()

pause()

resume()

state()

uptime()

is_running()

is_stopped()

is_paused()
```

No subsystem should modify lifecycle state directly.

All transitions occur through the Lifecycle Manager.

---

# Internal Components

The Lifecycle Manager consists of five logical components.

---

## State Controller

Maintains the current runtime state.

Responsible for validating all state transitions.

---

## Transition Manager

Executes transitions between lifecycle states.

Ensures transitions occur atomically.

---

## Event Publisher

Publishes lifecycle events.

Examples:

- SystemStarting
- SystemStarted
- SystemStopping
- SystemStopped
- SystemPaused
- SystemResumed
- SystemFailed

---

## Shutdown Coordinator

Coordinates graceful shutdown.

Responsible for stopping services in reverse dependency order.

---

## Runtime Clock

Tracks:

- startup time
- uptime
- restart count
- shutdown duration

---

# Class Design

```text
LifecycleManager
│
├── StateController
├── TransitionManager
├── EventPublisher
├── ShutdownCoordinator
└── RuntimeClock
```

Each component has a single responsibility.

---

# Data Models

Primary runtime models:

```text
LifecycleState

LifecycleEvent

TransitionRequest

TransitionResult

RuntimeStatus

ShutdownContext
```

---

# Execution Flow

### Startup

```text
Bootstrap Complete

↓

Lifecycle.start()

↓

State = Starting

↓

Publish SystemStarting

↓

Start Services

↓

Validate Runtime

↓

State = Running

↓

Publish SystemStarted
```

---

### Shutdown

```text
Shutdown Requested

↓

State = Stopping

↓

Publish SystemStopping

↓

Stop Scheduler

↓

Stop Plugins

↓

Drain Event Queue

↓

Dispose Services

↓

State = Stopped

↓

Publish SystemStopped
```

---

### Restart

```text
Restart Requested

↓

Stopping

↓

Stopped

↓

Starting

↓

Running
```

Restart is implemented as a complete shutdown followed by a fresh startup.

---

### Pause

```text
Pause Requested

↓

Pause Scheduler

↓

Suspend Background Jobs

↓

State = Paused

↓

Publish SystemPaused
```

Core services remain active while background execution is suspended.

---

### Resume

```text
Resume Requested

↓

Resume Scheduler

↓

Resume Background Jobs

↓

State = Running

↓

Publish SystemResumed
```

---

# State Management

The Lifecycle Manager operates as a finite state machine.

```text
Created

↓

Starting

↓

Running

↓

Paused

↓

Running

↓

Stopping

↓

Stopped
```

Failure state:

```text
Starting

↓

Failed
```

or

```text
Running

↓

Failed
```

---

Valid transitions:

```text
Created → Starting

Starting → Running

Running → Paused

Paused → Running

Running → Stopping

Stopping → Stopped

Stopped → Starting
```

Invalid transitions include:

```text
Running → Created

Paused → Created

Stopped → Running

Failed → Running
```

These transitions must raise lifecycle exceptions.

---

# Error Handling

Recoverable failures:

- Plugin pause failure
- Background task timeout
- Event publication failure

Fatal failures:

- Failed startup validation
- Service initialization failure
- Corrupted runtime state

Fatal failures transition the runtime to:

```text
Failed
```

Once failed, the runtime must either:

- restart
- terminate

No further work is accepted.

---

# Concurrency Model

Lifecycle transitions are serialized.

Only one transition may execute at any time.

Rules:

- Startup is exclusive.
- Shutdown is exclusive.
- Restart is exclusive.
- Pause is exclusive.
- Resume is exclusive.

Concurrent lifecycle requests are rejected.

---

# Configuration

Lifecycle behavior depends on:

```text
KernelSettings

ShutdownTimeout

StartupTimeout

PauseTimeout

HealthCheckInterval

RestartPolicy
```

Configuration is immutable after startup.

---

# Dependencies

Depends on:

- Configuration
- Logging
- Event Bus
- Scheduler
- Plugin Manager
- Health Monitor

Does not depend on:

- Perception
- Cognition
- Action

---

# Security Considerations

Only the Kernel may invoke lifecycle transitions.

External components cannot:

- force shutdown
- restart services
- modify runtime state

Lifecycle events must be authenticated within the runtime.

Illegal transitions are rejected immediately.

---

# Performance Considerations

Goals:

- deterministic transitions
- bounded shutdown latency
- minimal synchronization overhead
- fast pause/resume
- consistent restart behavior

Lifecycle operations should not block unrelated runtime activities longer than necessary.

---

# Testing Strategy

Unit Tests

- valid transitions
- invalid transitions
- uptime tracking
- restart behavior
- pause/resume

Integration Tests

- startup sequence
- graceful shutdown
- restart
- plugin shutdown
- scheduler coordination

Failure Tests

- failed startup
- interrupted shutdown
- invalid transitions
- concurrent transition requests

Performance Tests

- startup duration
- shutdown duration
- restart duration
- pause latency
- resume latency

---

# Future Extensions

The Lifecycle Manager should support future capabilities including:

- hot restart
- rolling service restart
- checkpoint/restore
- maintenance mode
- distributed lifecycle coordination
- runtime snapshots
- service-level lifecycle management
- automatic recovery policies

These extensions must preserve the existing public API and state transition guarantees.