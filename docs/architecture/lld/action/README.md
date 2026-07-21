# Action Module Overview

## Purpose

The Action subsystem is responsible for executing the decisions produced by the Cognition subsystem.

It is the only subsystem within Shadow that is permitted to interact directly with the outside world.

While Cognition determines **what should be done**, the Action subsystem determines **how that operation is safely executed**, whether it involves calling an API, manipulating the filesystem, controlling a browser, interacting with desktop applications, sending notifications, or executing a multi-step workflow.

Every operation performed by the Action subsystem is observable, auditable, permission-aware, and recoverable whenever possible.

The Action subsystem answers one question:

> **"How can this decision be executed safely and reliably?"**

---

# Responsibilities

The Action subsystem is responsible for:

- Executing external operations.
- Calling REST and GraphQL APIs.
- Browser automation.
- Desktop automation.
- Filesystem manipulation.
- Notification delivery.
- Multi-step workflow execution.
- Progress reporting.
- Error recovery.
- Producing execution artifacts.

The subsystem is **not** responsible for:

- Planning
- Reasoning
- OCR
- Knowledge Retrieval
- Memory Management
- Language Model Inference
- User Interface Rendering

---

# Scope

The Action subsystem provides standardized interfaces for interacting with external systems.

Supported execution domains include:

```text
REST APIs

GraphQL APIs

Web Browsers

Desktop Applications

Filesystem Operations

Email

SMS

Push Notifications

Webhook Delivery

Workflow Automation
```

Future capabilities include:

```text
Cloud Services

Remote Agents

IoT Devices

Mobile Device Automation

Distributed Execution

Robotic Process Automation (RPA)

Serverless Functions

Container Execution
```

---

# Package Structure

```text
shadow/
└── action/
    ├── api/
    ├── browser/
    ├── desktop/
    ├── filesystem/
    ├── notifications/
    ├── workflow/
    └── models/
```

---

# Public API

```python
execute()

execute_workflow()

call_api()

browse()

control_desktop()

filesystem()

notify()
```

Every request returns an immutable `ExecutionArtifact`.

---

# Internal Components

The Action subsystem consists of six execution domains.

---

## API

Responsible for communicating with external services.

Capabilities include:

- REST
- GraphQL
- Authentication
- Retries
- Response validation
- Rate limiting

---

## Browser

Responsible for browser automation.

Capabilities include:

- page navigation
- DOM interaction
- screenshots
- downloads
- uploads
- form automation

---

## Desktop

Responsible for operating system automation.

Capabilities include:

- launching applications
- keyboard automation
- mouse automation
- clipboard access
- window management

---

## Filesystem

Responsible for secure file operations.

Capabilities include:

- read
- write
- copy
- move
- delete
- search
- metadata inspection

---

## Notifications

Responsible for user notifications.

Supported channels include:

- email
- desktop notifications
- webhooks
- push notifications
- messaging integrations

---

## Workflow Engine

Coordinates multiple execution steps.

Capabilities include:

- sequencing
- branching
- retries
- rollback
- checkpointing
- progress tracking

---

# Class Design

```text
ActionEngine
│
├── APIManager
├── BrowserManager
├── DesktopManager
├── FilesystemManager
├── NotificationManager
└── WorkflowManager
```

Only `ActionEngine` is publicly exposed.

Each domain exposes its own internal interfaces while remaining coordinated through the Action Engine.

---

# Data Models

Primary runtime models:

```text
ExecutionRequest

ExecutionArtifact

ExecutionResult

ExecutionStatus

ExecutionContext

ExecutionLog

ExecutionMetrics

ExecutionError
```

Domain-specific models include:

```text
APIRequest

BrowserSession

DesktopSession

FilesystemOperation

NotificationRequest

WorkflowExecution
```

Every execution artifact contains:

```text
Execution ID

Operation Type

Status

Outputs

Logs

Metrics

Duration

Metadata
```

Artifacts remain immutable after completion.

---

# Design Decisions

## Action owns all side effects

No subsystem outside Action may directly modify external systems.

All interactions with operating systems, browsers, APIs, files, or services must pass through Action.

---

## Domain isolation

Each execution domain is implemented independently.

Filesystem logic never depends on browser automation.

Browser automation never depends on notification delivery.

Each module has a single responsibility.

---

## Uniform execution model

Although every execution domain performs different work, every operation follows the same lifecycle:

```text
Validate

↓

Execute

↓

Monitor

↓

Collect Results

↓

Return Artifact
```

This provides a consistent programming model across the entire subsystem.

---

## Observable execution

Every operation generates execution events.

Events may be consumed by:

- monitoring
- logging
- dashboards
- audit systems

Execution is always traceable.

---

## Safe by default

Every execution domain must enforce:

- input validation
- permission checks
- resource limits
- timeout policies
- cleanup

Unsafe execution paths are prohibited.

---

# Execution Flow

## Single Operation

```text
Execution Request

↓

Validate Request

↓

Select Action Domain

↓

Execute Operation

↓

Collect Outputs

↓

Generate Execution Artifact

↓

Return
```

---

## Workflow Execution

```text
Workflow Request

↓

Parse Workflow

↓

Execute Step

↓

Success?

↓

Yes

↓

Next Step

↓

Complete

↓

Return
```

Failures may trigger retries or rollback according to workflow policy.

---

# State Management

The Action subsystem manages execution state.

Lifecycle:

```text
Created

↓

Validated

↓

Executing

↓

Completed
```

Possible terminal states:

```text
Completed

Cancelled

Failed

Timed Out

Rolled Back
```

Execution state becomes immutable once complete.

---

# Error Handling

Recoverable:

- transient network failures
- retryable API errors
- temporary browser failures
- unavailable notification providers
- filesystem contention

Fatal:

- permission denied
- invalid execution request
- unsupported operation
- security policy violation
- workflow corruption

Failures raise typed Action exceptions.

---

# Concurrency Model

The Action subsystem supports concurrent execution.

Rules:

- independent operations execute concurrently
- workflows preserve dependency ordering
- filesystem locking prevents conflicting writes
- browser sessions remain isolated
- API requests execute independently
- notification delivery is asynchronous where possible

Concurrency must never compromise execution correctness.

---

# Configuration

Supported configuration includes:

```text
Execution Timeout

Maximum Concurrent Operations

Retry Policy

Filesystem Root

Browser Provider

Notification Providers

API Timeouts

Workflow Policy

Security Policy

Logging Level
```

Configuration is loaded during application startup.

---

# Dependencies

The Action subsystem depends on:

- Kernel
- Event Bus
- Configuration
- Logging
- Security
- Cognition

It communicates with:

- Operating System
- Browsers
- External APIs
- Filesystems
- Notification Providers

It does **not** depend on:

- Perception

Perception produces information.

Cognition produces decisions.

Action executes those decisions.

---

# Security Considerations

The Action subsystem must:

- validate every request
- enforce least-privilege execution
- isolate browser sessions
- restrict filesystem access
- sanitize API inputs
- protect credentials
- audit every external operation
- enforce configurable security policies

Every external interaction should be attributable to a specific execution request.

---

# Performance Considerations

Design goals:

- low execution overhead
- scalable concurrent execution
- efficient browser session reuse
- API connection pooling
- bounded filesystem latency
- asynchronous notification delivery

External I/O should never unnecessarily block unrelated execution paths.

---

# Testing Strategy

## Unit Tests

- API execution
- browser automation
- desktop automation
- filesystem operations
- notification delivery
- workflow execution

---

## Integration Tests

- REST APIs
- GraphQL APIs
- browser automation
- operating system automation
- notification providers
- cognition integration

---

## Failure Tests

- API failures
- browser crashes
- filesystem permission errors
- notification failures
- interrupted workflows

---

## Performance Tests

- concurrent API requests
- browser throughput
- filesystem performance
- notification latency
- workflow scalability

---

# Future Extensions

The Action subsystem should support future capabilities including:

- distributed execution
- cloud-native workflows
- container orchestration
- autonomous task execution
- edge device integration
- remote desktop automation
- mobile automation
- human approval gates
- policy-driven execution routing
- self-healing workflow execution

These extensions should preserve the existing architecture while maintaining secure, observable, deterministic, and reliable execution across every supported execution domain.