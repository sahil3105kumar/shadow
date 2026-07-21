# Logging System Low-Level Design

## Purpose

The Logging System is responsible for collecting, formatting, enriching, and routing diagnostic information generated throughout the Shadow runtime.

It provides a centralized, structured, and configurable logging framework that enables debugging, observability, auditing, and operational monitoring without coupling application components to specific logging implementations.

Every component within Shadow writes logs through the Logging System.

The Logging System is initialized during bootstrap and remains available for the lifetime of the application.

---

# Responsibilities

The Logging System is responsible for:

- Initializing the logging infrastructure.
- Providing logger instances.
- Producing structured logs.
- Managing log levels.
- Routing logs to configured destinations.
- Formatting log records.
- Attaching contextual metadata.
- Rotating log files.
- Redacting sensitive information.
- Supporting application diagnostics.

The Logging System is **not** responsible for:

- Runtime metrics.
- Health monitoring.
- Event storage.
- Business analytics.
- Alerting.
- Exception handling.

---

# Scope

The Logging System owns every log record produced by the runtime.

Every subsystem—including Kernel, Infrastructure, Perception, Cognition, Action, Plugins, CLI, and API—must log through the Logging System.

Direct use of Python's logging module outside this subsystem is prohibited.

---

# Package Structure

```text
shadow/
└── infrastructure/
    └── logging/
        ├── __init__.py
        ├── formatter.py
        ├── handlers.py
        ├── filters.py
        ├── context.py
        └── factory.py
```
Nested under its own subpackage — not flat inside `shadow/infrastructure/` — for the same reason as Filesystem, Security, and Serialization: flat siblings would collide across components.

Expected classes:

```text
LoggingManager

LoggerFactory

StructuredFormatter

LogHandler

LogContext

LogFilter
```

---

# Public API

```python
initialize()

get_logger()

set_level()

flush()

shutdown()
```

Logger instances are obtained exclusively through `get_logger()`.

---

# Internal Components

The Logging System consists of six logical components.

---

## Logging Manager

Coordinates initialization and shutdown of the logging subsystem.

Responsible for:

- configuration
- handler registration
- lifecycle management

---

## Logger Factory

Creates logger instances.

Responsibilities:

- component loggers
- child loggers
- contextual loggers

Every logger is uniquely identified by component name.

---

## Structured Formatter

Transforms log records into structured output.

Supported formats:

- JSON
- Console (human-readable)

Every record contains consistent metadata.

---

## Log Handlers

Responsible for routing log records.

Supported handlers:

- Console
- File

Future handlers:

- Syslog
- HTTP
- OpenTelemetry
- Cloud Logging

---

## Context Manager

Maintains contextual information.

Examples:

```text
Request ID

Job ID

Conversation ID

Plugin ID

Correlation ID

Thread ID
```

Context is automatically attached to every log entry.

---

## Log Filters

Responsible for:

- level filtering
- component filtering
- sensitive data masking
- duplicate suppression

Filters execute before handlers.

---

# Class Design

```text
LoggingManager
│
├── LoggerFactory
├── StructuredFormatter
├── LogHandler
├── ContextManager
└── LogFilter
```

Only `LoggingManager` is publicly exposed.

---

# Data Models

Primary runtime models:

```text
LogRecord

LogContext

LogLevel

LogHandlerConfig

FormatterConfig

LogMetadata
```

Example LogRecord:

```text
Timestamp

Level

Logger

Message

Component

Module

Thread

Context

Exception

Metadata
```

---

# Design Decisions

## Structured logging by default

Every log is structured.

Logs are intended for both humans and machines.

This simplifies:

- searching
- filtering
- aggregation
- diagnostics

---

## Context is automatic

Application code should not manually attach runtime metadata.

The Logging System automatically enriches every record with available context.

---

## Logging is centralized

All runtime components use the same logging infrastructure.

No component configures its own handlers or formatters.

---

## Logging is non-blocking

Whenever practical, log writing should avoid blocking application execution.

Slow log destinations should not degrade application responsiveness.

---

# Execution Flow

## Initialization

```text
Bootstrap

↓

Load Logging Configuration

↓

Create Formatter

↓

Create Handlers

↓

Register Filters

↓

Initialize Logging Manager

↓

Ready
```

---

## Logging

```text
Component

↓

Get Logger

↓

Create Log Record

↓

Attach Context

↓

Apply Filters

↓

Format Record

↓

Dispatch to Handlers

↓

Complete
```

---

## Shutdown

```text
Shutdown Requested

↓

Flush Handlers

↓

Close Files

↓

Release Resources

↓

Shutdown Complete
```

---

# State Management

The Logging System operates as a finite state machine.

```text
Created

↓

Initializing

↓

Running

↓

Stopping

↓

Stopped
```

Logging requests received after shutdown are ignored or redirected to a fallback handler.

---

# Error Handling

Recoverable:

- handler failure
- formatter failure
- unavailable log destination
- disk full (temporary)

Fatal:

- logging initialization failure
- invalid logging configuration

Logging failures should never terminate the application.

When possible, failures fall back to console logging.

---

# Concurrency Model

The Logging System supports concurrent logging.

Rules:

- Logger creation is synchronized.
- Log writing is thread-safe.
- Context is isolated per execution context.
- Handler flushing is serialized.
- Shutdown waits for pending log writes.

Concurrent logging must not corrupt log output.

---

# Configuration

Supported configuration includes:

```text
Log Level

Output Format

Console Logging

File Logging

Log Directory

Maximum File Size

Rotation Policy

Retention Count

Timestamp Format

Sensitive Field Masking
```

Configuration is loaded during bootstrap.

---

# Dependencies

The Logging System depends on:

- Configuration
- Filesystem
- Exceptions

It does **not** depend on:

- Kernel
- Scheduler
- Event Bus
- Plugin Manager
- Cognition
- Perception
- Action

Every other subsystem depends on the Logging System.

---

# Security Considerations

The Logging System must:

- redact secrets
- prevent credential leakage
- sanitize user input
- avoid logging sensitive payloads
- validate log destinations
- protect log integrity

Sensitive information includes:

- passwords
- API keys
- access tokens
- session identifiers
- authentication credentials
- encryption keys

These values must never appear in log output.

---

# Performance Considerations

Design goals:

- low logging overhead
- efficient formatting
- minimal memory allocation
- asynchronous output when appropriate
- bounded shutdown latency

Logging should not become a performance bottleneck.

---

# Testing Strategy

## Unit Tests

- logger creation
- formatter output
- handler registration
- filtering
- context propagation
- log level changes
- shutdown

---

## Integration Tests

- bootstrap initialization
- kernel logging
- plugin logging
- scheduler logging
- configuration integration

---

## Failure Tests

- invalid configuration
- handler failure
- formatter exception
- file permission errors
- disk full simulation

---

## Performance Tests

- logging throughput
- concurrent logging
- formatting latency
- file rotation performance

---

# Future Extensions

The Logging System should support future capabilities including:

- distributed tracing
- OpenTelemetry exporters
- cloud logging providers
- log streaming
- dynamic log levels
- audit log separation
- structured search indexes
- remote log aggregation
- runtime log reconfiguration
- AI-assisted log analysis

These extensions should preserve the existing public API while maintaining structured, secure, and high-performance logging.