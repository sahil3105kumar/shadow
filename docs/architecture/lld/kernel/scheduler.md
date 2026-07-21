# Scheduler Low-Level Design

## Purpose

The Scheduler is responsible for executing deferred, recurring, and scheduled tasks within the Shadow runtime.

It provides a centralized mechanism for managing time-based operations while abstracting away timer management, task triggering, and execution coordination.

The Scheduler enables system maintenance, periodic health checks, background synchronization, cleanup operations, and delayed execution.

The Scheduler is **not** a workflow engine, job queue, or orchestration framework.

---

# Responsibilities

The Scheduler is responsible for:

- Scheduling one-time tasks.
- Scheduling recurring tasks.
- Scheduling delayed execution.
- Executing scheduled jobs.
- Cancelling scheduled jobs.
- Pausing scheduled jobs.
- Resuming paused jobs.
- Tracking job status.
- Monitoring execution metrics.
- Publishing scheduler events.

The Scheduler is **not** responsible for:

- Business workflows.
- AI task planning.
- Long-running computations.
- External distributed scheduling.
- Retry policies for application logic.
- Dependency resolution.

---

# Scope

The Scheduler owns every runtime job registered with the system.

Jobs may originate from:

- Kernel
- Infrastructure
- Plugins
- Perception
- Cognition
- Action

The Scheduler is responsible only for *when* a job executes.

It has no knowledge of *why* the job exists.

---

# Package Structure

```text
shadow/
└── kernel/
    └── scheduler.py
```

Expected classes:

```text
Scheduler

Job

JobTrigger

JobRegistry

JobExecutor

SchedulePolicy

ExecutionContext
```

---

# Public API

```python
schedule()

schedule_once()

schedule_after()

schedule_interval()

cancel()

pause()

resume()

run_now()

list_jobs()

status()

shutdown()
```

Jobs are referenced by unique identifiers.

---

# Internal Components

The Scheduler consists of six logical components.

---

## Job Registry

Maintains metadata for every scheduled job.

Tracks:

- identifier
- owner
- trigger
- next execution
- status
- execution count

---

## Trigger Manager

Determines when jobs should execute.

Supported trigger types:

- Immediate
- Delayed
- Interval
- Cron (future extension)

---

## Execution Engine

Responsible for invoking jobs.

Responsibilities:

- acquire execution context
- invoke task
- record completion
- publish events

---

## Timer Service

Maintains internal timing.

Responsible for:

- wake-up intervals
- timer precision
- delayed execution

---

## Metrics Collector

Collects execution statistics.

Examples:

- jobs executed
- failed jobs
- execution duration
- skipped jobs
- queue depth

---

## Cleanup Manager

Removes completed or expired jobs according to policy.

---

# Class Design

```text
Scheduler
│
├── JobRegistry
├── TriggerManager
├── ExecutionEngine
├── TimerService
├── MetricsCollector
└── CleanupManager
```

Only the `Scheduler` class is publicly visible.

---

# Data Models

Primary runtime models:

```text
Job

JobState

JobTrigger

SchedulePolicy

ExecutionResult

ExecutionContext

JobMetrics
```

Example Job:

```text
Job ID

Name

Owner

Trigger

State

Priority

Last Run

Next Run

Retry Count

Metadata
```

---

# Design Decisions

## The Scheduler is time-based only

The Scheduler determines **when** work executes.

It never decides **what** work should execute.

Planning belongs to the Cognition module.

Workflow execution belongs to the Action module.

---

## Jobs are lightweight

A scheduled job should perform minimal work.

Long-running operations should delegate to background workers or asynchronous services.

---

## Jobs are deterministic

Every scheduled job should produce predictable behavior based on its trigger and current runtime state.

---

## Scheduling is in-memory

The Scheduler maintains its state in memory.

Jobs are recreated during application startup.

Persistent scheduling may be introduced in future versions.

---

# Execution Flow

## Scheduling

```text
Create Job

↓

Validate Trigger

↓

Register Job

↓

Compute Next Execution

↓

Waiting
```

---

## Execution

```text
Timer Tick

↓

Find Due Jobs

↓

Validate State

↓

Execute Job

↓

Publish Completion Event

↓

Update Metrics

↓

Compute Next Execution
```

---

## Cancellation

```text
Cancel Request

↓

Locate Job

↓

Remove Trigger

↓

Update Registry

↓

Cancelled
```

---

# State Management

Jobs operate as finite state machines.

```text
Created

↓

Scheduled

↓

Waiting

↓

Running

↓

Completed
```

Recurring jobs:

```text
Waiting

↓

Running

↓

Waiting
```

Failure path:

```text
Running

↓

Failed
```

Cancelled jobs:

```text
Waiting

↓

Cancelled
```

Only valid transitions are permitted.

---

# Error Handling

Recoverable:

- job execution failure
- timeout
- cancelled job
- missed execution window

Fatal:

- corrupted registry
- invalid trigger
- scheduler initialization failure
- timer failure

Job failures must not terminate the Scheduler.

Failures are isolated to the individual job.

---

# Concurrency Model

The Scheduler supports concurrent job execution.

Rules:

- Registry modifications are synchronized.
- Independent jobs may execute concurrently.
- A single job instance cannot execute more than once simultaneously unless explicitly configured.
- Timer management is single-threaded.
- Shutdown waits for active jobs to complete or timeout.

Concurrency must preserve deterministic scheduling behavior.

---

# Configuration

Supported configuration includes:

```text
Maximum Concurrent Jobs

Default Timeout

Timer Resolution

Cleanup Interval

Maximum Retry Count

Metrics Enabled

Graceful Shutdown Timeout

Auto Cleanup Policy
```

Configuration is loaded during bootstrap.

---

# Dependencies

The Scheduler depends on:

- Configuration
- Logging
- Event Bus
- Exceptions

The Scheduler does **not** depend on:

- Cognition
- Perception
- Action
- Plugin implementations

Other modules submit jobs through the Scheduler's public API.

---

# Security Considerations

The Scheduler must:

- validate job registrations
- reject duplicate identifiers
- prevent unauthorized cancellation
- isolate job failures
- protect internal registry structures
- prevent resource exhaustion through excessive scheduling

Only trusted runtime components may register system-level jobs.

---

# Performance Considerations

Design goals:

- efficient trigger evaluation
- minimal timer overhead
- bounded scheduling latency
- scalable concurrent execution
- low memory footprint

The Scheduler should support thousands of registered jobs while maintaining predictable execution timing.

---

# Testing Strategy

## Unit Tests

- job registration
- delayed scheduling
- interval scheduling
- cancellation
- pause/resume
- trigger calculation

---

## Integration Tests

- scheduler startup
- plugin jobs
- lifecycle coordination
- event publication
- graceful shutdown

---

## Failure Tests

- invalid trigger
- execution timeout
- concurrent scheduling
- cancelled job execution
- registry corruption

---

## Performance Tests

- scheduling throughput
- timer accuracy
- concurrent execution
- large registry performance

---

# Future Extensions

The Scheduler should support future capabilities including:

- cron expressions
- persistent schedules
- distributed scheduling
- job priorities
- execution windows
- dependency-aware scheduling
- calendar-based scheduling
- retry policies
- rate limiting
- execution tracing

These extensions should preserve the existing public API while maintaining deterministic scheduling behavior.