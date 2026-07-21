# Dependency Injection Container Low-Level Design

## Purpose

The Dependency Injection (DI) Container is the central service registry of the Shadow runtime.

Its primary responsibility is to manage the creation, registration, resolution, and lifetime of application services.

The DI Container removes direct dependencies between components by ensuring that services interact through abstractions rather than concrete implementations.

Every long-lived runtime service must be registered with the container.

The container is created during bootstrap and remains alive for the entire lifetime of the application.

---

# Responsibilities

The Dependency Injection Container is responsible for:

- Registering services.
- Resolving dependencies.
- Managing service lifetimes.
- Preventing duplicate registrations.
- Detecting dependency cycles.
- Supporting lazy initialization.
- Providing singleton instances.
- Supporting interface-based resolution.
- Managing service disposal during shutdown.

The container is **not** responsible for:

- Business logic.
- Configuration loading.
- Event routing.
- Plugin discovery.
- Scheduling.
- Runtime state management.

---

# Scope

The DI Container owns the dependency graph of the application.

Every subsystem receives its dependencies through the container.

No component should instantiate another service directly using constructors outside of composition root (Bootstrap).

---

# Package Structure

```text
shadow/
└── kernel/
    └── container.py
```

Expected classes:

```text
Container

ServiceDescriptor

ServiceLifetime

RegistrationBuilder

ResolutionContext
```

---

# Public API

```python
register()

register_singleton()

register_factory()

register_instance()

resolve()

try_resolve()

contains()

remove()

freeze()

dispose()
```

The API intentionally remains small.

Once the container is frozen, no additional registrations are permitted.

---

# Internal Components

The DI Container consists of six logical components.

---

## Service Registry

Maintains metadata for every registered service.

Tracks:

- service identifier
- implementation type
- lifetime
- factory
- dependencies

---

## Resolver

Constructs dependency graphs.

Responsible for recursively resolving services while detecting circular dependencies.

---

## Lifetime Manager

Controls object lifetime.

Supported lifetimes:

```text
Singleton

Transient

Scoped (reserved for future use)
```

Initially, Shadow primarily uses singleton services.

---

## Factory Manager

Supports deferred object construction.

Factories are invoked only when a service is first requested (lazy initialization).

---

## Dependency Validator

Validates the dependency graph before runtime.

Checks:

- missing services
- duplicate registrations
- dependency cycles
- invalid interfaces

---

## Disposal Manager

Responsible for graceful cleanup.

Services are disposed in reverse dependency order.

---

# Class Design

```text
Container
│
├── ServiceRegistry
├── Resolver
├── LifetimeManager
├── FactoryManager
├── DependencyValidator
└── DisposalManager
```

The `Container` class is the only public entry point.

Internal components remain private.

---

# Data Models

Primary runtime models:

```text
ServiceDescriptor

ServiceIdentifier

Registration

DependencyNode

ResolutionGraph

ResolutionContext

ServiceLifetime
```

Example ServiceDescriptor:

```text
Service Name

Implementation Type

Lifetime

Factory

Dependencies

Initialized

Instance
```

---

# Execution Flow

## Registration

```text
Bootstrap

↓

Create Container

↓

Register Service

↓

Validate Registration

↓

Store Descriptor
```

---

## Resolution

```text
resolve(Service)

↓

Lookup Descriptor

↓

Already Initialized?

↓

Yes
↓

Return Singleton

No

↓

Resolve Dependencies

↓

Construct Object

↓

Cache Instance

↓

Return Service
```

---

## Shutdown

```text
Shutdown Requested

↓

Reverse Dependency Graph

↓

Dispose Services

↓

Release Resources

↓

Clear Registry
```

---

# State Management

The container has four operational states.

```text
Created

↓

Registering

↓

Frozen

↓

Disposed
```

### Registering

Services may be added.

### Frozen

No new registrations allowed.

Only resolution operations are permitted.

### Disposed

Container cannot resolve services.

Attempting to use a disposed container raises an exception.

---

# Error Handling

Recoverable:

- optional service unavailable
- duplicate optional registration

Fatal:

- circular dependency
- missing required dependency
- duplicate required service
- constructor failure
- frozen container modification
- resolution after disposal

Fatal errors during bootstrap prevent the application from starting.

---

# Concurrency Model

The container supports concurrent service resolution after bootstrap.

Rules:

- Registration is single-threaded.
- Resolution is thread-safe.
- Singleton creation is atomic.
- Service registry is immutable after freezing.
- Disposal is exclusive.

No service may be constructed more than once.

---

# Configuration

The container has minimal configuration.

Supported settings include:

```text
Lazy Initialization

Dependency Validation

Singleton Verification

Circular Dependency Detection

Strict Registration Mode
```

Configuration is loaded during bootstrap.

---

# Dependencies

The DI Container depends only on:

- Exceptions
- Logging (optional for diagnostics)

It must **not** depend on:

- Event Bus
- Scheduler
- Plugins
- Cognition
- Perception
- Action

The container is one of the lowest-level components in the architecture.

---

# Security Considerations

The container is a privileged runtime component.

Security requirements include:

- Reject duplicate critical services.
- Prevent service replacement after freezing.
- Validate factory signatures.
- Prevent runtime mutation of registrations.
- Restrict access to internal registry structures.

Service resolution should never expose internal container state.

---

# Performance Considerations

The container should prioritize predictable performance.

Goals:

- O(1) service lookup.
- Constant-time singleton retrieval.
- Minimal allocation during resolution.
- Lazy object creation.
- Fast dependency graph traversal.

Dependency validation should occur once during startup.

Runtime resolution should avoid repeated graph analysis.

---

# Testing Strategy

## Unit Tests

- service registration
- singleton resolution
- transient resolution
- factory registration
- lazy initialization
- service removal
- container freezing

---

## Integration Tests

- bootstrap registration
- dependency graph resolution
- plugin service registration
- scheduler resolution
- event bus resolution

---

## Failure Tests

- circular dependency detection
- missing dependency
- duplicate registration
- frozen container modification
- resolution after disposal

---

## Performance Tests

- registration throughput
- singleton resolution latency
- transient construction latency
- dependency graph resolution time

---

# Future Extensions

The DI Container should support future capabilities including:

- scoped lifetimes
- named service registrations
- conditional registrations
- automatic constructor injection
- assembly/module scanning
- child containers
- runtime diagnostics
- dependency graph visualization
- service interception (AOP)
- decorator-based registration

These extensions should remain backward compatible with the existing API and preserve deterministic service resolution.