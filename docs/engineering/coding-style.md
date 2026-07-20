# Coding Style Guide

> *"Code is read far more often than it is written."*

---

# Purpose

This document defines the coding standards followed throughout the Shadow codebase.

Consistent code improves readability, maintainability, collaboration, and long-term evolution.

These guidelines apply to every contribution regardless of programming language.

---

# Core Principles

Every contribution should be:

* Readable
* Predictable
* Consistent
* Maintainable
* Testable
* Modular

---

# General Rules

Code should:

* Express intent clearly.
* Prefer explicitness over cleverness.
* Minimize complexity.
* Avoid unnecessary abstraction.
* Follow existing project conventions.

Consistency is preferred over personal preference.

---

# Naming

Names should:

* Be descriptive.
* Reflect intent.
* Avoid abbreviations unless universally understood.
* Remain consistent across the project.

Examples include:

* Nouns for data structures
* Verbs for functions
* Adjectives for boolean values

---

# File Organization

Each file should have a single responsibility.

Files should remain focused and reasonably sized.

Closely related functionality should remain together.

---

# Functions

Functions should:

* Perform one logical task.
* Have clear inputs.
* Produce predictable outputs.
* Avoid hidden side effects.
* Remain easy to test.

Large functions should be decomposed into smaller units.

---

# Classes

Classes should:

* Represent a single concept.
* Encapsulate related behavior.
* Expose minimal public interfaces.
* Hide implementation details.

Inheritance should be used sparingly.

---

# Modules

Modules should:

* Be cohesive.
* Minimize dependencies.
* Avoid circular references.
* Expose clear interfaces.

Implementation details should remain internal.

---

# Comments

Comments should explain:

* Why something exists.
* Architectural decisions.
* Non-obvious constraints.
* Complex algorithms.

Comments should not describe obvious code.

Outdated comments should be removed.

---

# Formatting

Formatting should remain consistent throughout the repository.

Formatting rules should be enforced automatically whenever possible.

Manual formatting should be minimized.

---

# Imports

Imports should:

* Be explicit.
* Avoid unused dependencies.
* Follow a consistent ordering.
* Minimize coupling.

Wildcard imports should be avoided.

---

# Constants

Constants should:

* Replace magic values.
* Have descriptive names.
* Remain immutable.

Configuration belongs outside source code.

---

# Error Handling

Errors should:

* Be handled explicitly.
* Provide meaningful diagnostics.
* Preserve context.
* Avoid silent failures.

Exceptions should represent exceptional situations.

---

# Logging

Logs should:

* Describe meaningful events.
* Support diagnostics.
* Avoid sensitive information.
* Remain structured.

Logging should never replace proper error handling.

---

# Configuration

Configuration should:

* Remain external.
* Be validated.
* Support environment overrides.
* Avoid hardcoded values.

---

# Dependencies

Dependencies should:

* Be minimized.
* Be actively maintained.
* Serve a clear purpose.

Redundant dependencies should be removed.

---

# Testing

Code should be written with testing in mind.

Implementation should remain deterministic wherever practical.

Functions should avoid hidden dependencies.

---

# Performance

Readable code should be preferred unless profiling demonstrates a measurable performance benefit.

Optimization should remain localized.

---

# Security

Code should:

* Validate external input.
* Respect permission boundaries.
* Protect secrets.
* Fail securely.

Security-sensitive code should remain simple and auditable.

---

# Documentation

Public interfaces should be documented.

Architectural decisions should reference the appropriate design documentation.

Documentation should evolve alongside implementation.

---

# Deprecation

Deprecated functionality should:

* Be clearly identified.
* Provide migration guidance.
* Remain compatible for an appropriate transition period.

Removal should follow documented versioning policies.

---

# Code Review Checklist

Every contribution should be reviewed for:

* Correctness
* Readability
* Maintainability
* Architecture
* Testing
* Security
* Documentation
* Performance implications

---

# Success Criteria

The coding style succeeds when:

* Code is understandable without extensive explanation.
* Contributors produce consistent implementations.
* Maintenance costs remain low.
* Architectural intent is preserved throughout the codebase.
