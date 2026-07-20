# Shadow Documentation

Welcome to the official documentation for **Shadow**, a privacy-first Personal Cognitive Operating System (COS).

This documentation is organized from **vision to implementation**, allowing readers to understand not only *how* Shadow works, but *why* it was designed that way.

---

# Documentation Philosophy

Every document in this repository answers a different question.

| Layer        | Question                               |
| ------------ | -------------------------------------- |
| README       | What is Shadow?                        |
| Product      | Why are we building it?                |
| Architecture | How is it designed?                    |
| Engineering  | How do we build and maintain it?       |
| ADR          | Why were architectural decisions made? |

Documentation should be read in this order.

---

# Repository Structure

```text
docs/
│
├── index.md
│
├── product/
│   ├── vision.md
│   ├── principles.md
│   ├── prd.md
│   ├── glossary.md
│   └── roadmap.md
│
├── architecture/
│   ├── system-overview.md
│   ├── srs.md
│   │
│   ├── hld/
│   │   ├── kernel.md
│   │   ├── perception.md
│   │   ├── cognition.md
│   │   ├── action.md
│   │   └── infrastructure.md
│   │
│   ├── lld/
│   │   ├── kernel/
│   │   ├── perception/
│   │   ├── cognition/
│   │   ├── action/
│   │   └── infrastructure/
│   │
│   ├── event-spec.md
│   ├── data-model.md
│   ├── plugin-system.md
│   ├── security.md
│   └── deployment.md
│
├── engineering/
│   ├── engineering.md
│   ├── coding-style.md
│   ├── testing.md
│   ├── performance.md
│   └── release-process.md
│
└── adr/
```

---

# Reading Order

The documentation is intentionally layered.

Each layer builds upon the one before it.

```text
README
    │
    ▼
Vision
    │
    ▼
Principles
    │
    ▼
PRD
    │
    ▼
Glossary
    │
    ▼
Roadmap
    │
    ▼
System Overview
    │
    ▼
SRS
    │
    ▼
High-Level Design (HLD)
    │
    ▼
Low-Level Design (LLD)
    │
    ▼
Implementation
```

Readers are encouraged to follow this order when first exploring the project.

---

# Product Documentation

The Product layer defines the purpose and direction of Shadow.

| Document          | Purpose                                                                             |
| ----------------- | ----------------------------------------------------------------------------------- |
| **vision.md**     | Defines why Shadow exists and the long-term vision of the platform.                 |
| **principles.md** | Establishes the architectural and engineering principles that guide every decision. |
| **prd.md**        | Describes the capabilities Shadow should provide from a product perspective.        |
| **glossary.md**   | Defines the official terminology used throughout the project.                       |
| **roadmap.md**    | Describes the long-term evolution of Shadow through capability-driven milestones.   |

The Product layer answers:

> **"What are we building, and why?"**

---

# Architecture Documentation

The Architecture layer defines how Shadow is designed.

## System Overview

Introduces the overall architecture of the platform, its domains, responsibilities, and information flow.

This is the recommended starting point for anyone interested in understanding the system.

---

## Software Requirements Specification (SRS)

Defines the functional and non-functional requirements that every implementation must satisfy.

The SRS is technology-independent.

---

## High-Level Design (HLD)

Each major domain has its own High-Level Design document.

| Document              | Responsibility                                                      |
| --------------------- | ------------------------------------------------------------------- |
| **kernel.md**         | Runtime coordination, scheduling, lifecycle, and event routing.     |
| **perception.md**     | Processing external inputs into structured information.             |
| **cognition.md**      | Memory, reasoning, planning, and knowledge management.              |
| **action.md**         | Safe execution of tasks in the external world.                      |
| **infrastructure.md** | Shared platform services such as storage, security, and deployment. |

---

## Low-Level Design (LLD)

The Low-Level Design directory contains implementation-oriented specifications for each architectural domain.

LLDs describe:

* Components
* Interfaces
* Internal workflows
* Algorithms
* Data structures
* State management
* Error handling
* Testing considerations

Unlike HLDs, these documents may evolve as the implementation changes.

---

## Supporting Architecture Documents

| Document             | Purpose                                                                                    |
| -------------------- | ------------------------------------------------------------------------------------------ |
| **event-spec.md**    | Defines Shadow's event model, event lifecycle, schemas, and communication patterns.        |
| **data-model.md**    | Describes persistent entities, relationships, and storage abstractions.                    |
| **plugin-system.md** | Defines the plugin architecture, extension interfaces, and lifecycle.                      |
| **security.md**      | Documents authentication, authorization, encryption, permissions, and security principles. |
| **deployment.md**    | Covers deployment models, environments, configuration, and operational concerns.           |

The Architecture layer answers:

> **"How is Shadow designed?"**

---

# Engineering Documentation

The Engineering layer defines how Shadow is developed and maintained.

| Document               | Purpose                                                           |
| ---------------------- | ----------------------------------------------------------------- |
| **engineering.md**     | Engineering philosophy, workflows, and development standards.     |
| **coding-style.md**    | Coding conventions and repository-wide style guidelines.          |
| **testing.md**         | Testing strategy, quality assurance, and validation requirements. |
| **performance.md**     | Performance objectives, profiling, and optimization guidelines.   |
| **release-process.md** | Versioning, release workflow, and deployment practices.           |

This layer answers:

> **"How do we build Shadow?"**

---

# Architecture Decision Records (ADR)

The `adr/` directory records significant architectural decisions made throughout the lifetime of the project.

Each ADR captures:

* The problem.
* The chosen solution.
* Alternatives considered.
* Trade-offs.
* Long-term consequences.

Architectural decisions should never be lost in commit history or chat conversations.

---

# Documentation Principles

Every document should strive to be:

* Clear before clever.
* Technology-independent where practical.
* Focused on a single responsibility.
* Easy to maintain.
* Consistent with the Vision and Principles.
* Useful years after it is written.

Documentation is treated as part of the architecture—not as an afterthought.

---

# Contributor Guide

If you are new to Shadow, read the documents in the following order:

1. README
2. Vision
3. Principles
4. PRD
5. Glossary
6. Roadmap
7. System Overview
8. SRS
9. Relevant HLD
10. Relevant LLD

This progression mirrors the evolution of the project—from philosophy to architecture to implementation.

---

# Documentation Flow

```text
Why
│
├── README
├── Vision
└── Principles
        │
        ▼
What
│
├── PRD
├── Glossary
└── Roadmap
        │
        ▼
How
│
├── System Overview
├── SRS
├── HLD
├── LLD
└── Supporting Architecture
        │
        ▼
Build
│
├── Engineering
└── Code
        │
        ▼
Evolve
│
└── ADR
└── RFCs

```

---

# Closing Note

Shadow is intended to evolve over decades.

Its architecture, implementation, and technologies will change, but its documentation should continue to tell a coherent story—from the vision that inspired the platform to the engineering decisions that shaped it.

Well-maintained documentation is an integral part of Shadow itself.
