# High-Level Design: Action

> *"Action transforms decisions into real-world execution."*

---

# Purpose

The Action domain is responsible for executing approved operations outside of Shadow.

It receives validated requests from Cognition, performs the requested work through supported interfaces, monitors execution, and reports results back to the system.

Action answers one question:

> **"How do we safely perform this task?"**

The Action domain never decides *what* should be done. It only determines *how* to execute an approved task.

---

# Responsibilities

* Desktop automation
* Browser automation
* API execution
* File operations
* Device interaction
* Notification delivery
* Workflow execution
* External application control
* Task monitoring
* Execution reporting

---

# Non-Responsibilities

Action shall never:

* Perform reasoning
* Understand user intent
* Generate responses
* Store long-term memory
* Route events
* Manage system resources
* Make autonomous decisions

---

# Architectural Position

```text id="hyx7cv"
                     Cognition
                          │
                  Action Request
                          │
                          ▼
                    ┌───────────┐
                    │  Action   │
                    └───────────┘
                          │
      ┌──────────┬────────┼─────────┬──────────┐
      ▼          ▼        ▼         ▼          ▼
   Desktop    Browser    APIs     Files    Devices
                          │
                          ▼
                     Result Events
```

---

# Core Responsibilities

The Action domain is composed of specialized executors that perform work across different environments.

---

## Execution Manager

Coordinates every execution request.

Responsibilities include:

* Request validation
* Executor selection
* Lifecycle management
* Retry coordination
* Status tracking

---

## Desktop Executor

Interacts with desktop environments.

Examples include:

* Opening applications
* Keyboard automation
* Mouse automation
* Window management
* Clipboard interaction

---

## Browser Executor

Interacts with web browsers.

Examples include:

* Navigation
* Form completion
* Downloads
* Uploads
* Authentication workflows
* Web automation

---

## API Executor

Communicates with external services.

Responsibilities include:

* HTTP requests
* Authentication
* Webhooks
* API integrations
* Rate limiting

---

## File Executor

Performs filesystem operations.

Examples include:

* Reading files
* Writing files
* Moving files
* Organizing directories
* Backup operations

---

## Device Executor

Interacts with connected devices.

Examples include:

* Mobile devices
* IoT devices
* Smart home systems
* External peripherals
* Future hardware integrations

---

## Notification Manager

Delivers information to users through supported channels.

Examples include:

* Desktop notifications
* Mobile notifications
* Email
* Messaging platforms

---

## Workflow Engine

Coordinates multi-step execution.

Responsibilities include:

* Sequential execution
* Conditional execution
* Parallel execution
* Rollback handling
* Progress tracking

---

# Execution Pipeline

```text id="pn6b6o"
Action Request
       │
       ▼
Validation
       │
       ▼
Executor Selection
       │
       ▼
Permission Verification
       │
       ▼
Execution
       │
       ▼
Monitoring
       │
       ▼
Result Event
```

---

# Inputs

Action consumes:

* Approved action requests
* Workflow events
* Scheduler events
* System events
* User approvals

---

# Outputs

Action publishes:

* Execution started
* Progress updates
* Completion events
* Failure events
* Retry events
* Audit events

All outcomes are communicated through the Event Bus.

---

# Safety Principles

Every execution must adhere to the following principles:

* Explicit user approval where required
* Least privilege
* Reversible operations when possible
* Complete audit trail
* Idempotent execution where applicable
* Secure credential handling

No executor may bypass system security policies.

---

# Failure Handling

Action shall:

* Detect execution failures.
* Retry recoverable operations.
* Abort unrecoverable workflows safely.
* Report detailed execution status.
* Preserve partial progress when appropriate.

Execution failures must never compromise overall system stability.

---

# Extensibility

Future execution environments may include:

* Robotics
* Autonomous vehicles
* Industrial systems
* Wearables
* AR/VR platforms
* Cloud orchestration
* Distributed device networks

New executors should integrate without modifying existing execution logic.

---

# Success Criteria

Action succeeds when:

* Approved requests are executed reliably.
* Execution remains observable and auditable.
* Failures are isolated and recoverable.
* External systems remain abstracted behind executors.
* User control is maintained throughout every operation.
