# Shadow

> **A Privacy-First Personal Cognitive Operating System**

<p align="center">
  <i>Remember what matters. Understand the present. Help shape the future.</i>
</p>

---

## Overview

**Shadow** is a long-term engineering effort to build a **self-hosted, modular, privacy-first Cognitive Operating System (COS)**. It is not another AI chatbot, an LLM wrapper, or a collection of automation scripts. Shadow is designed to become a lifelong digital companion—a second brain that grows alongside its user, remembers what they choose to preserve, understands the context of their life, and assists in thinking, planning, creating, and acting.

Unlike traditional AI assistants, Shadow treats artificial intelligence as **infrastructure**, not the product itself. Large language models, speech models, vision models, and future AI systems are replaceable implementation details. The user's memories, knowledge, relationships, and experiences are not.

Every architectural decision is guided by one unwavering principle:

> **The user owns their data, their infrastructure, and ultimately their intelligence.**

Shadow operates through a conversational **Persona**. The default persona is **Mahoraga**, but it is completely customizable. Users should be able to rename it, change its personality, voice, appearance, and behavior without affecting the underlying platform. Shadow is the operating system; Mahoraga is simply one way to interact with it.

---
## Why Shadow?

Modern AI assistants are stateless, cloud-dependent, and disposable. They forget context, require repeated prompting, and treat conversations as isolated interactions. Shadow takes a fundamentally different approach. It is designed to preserve knowledge, maintain long-term context, and continuously evolve with its user while ensuring that privacy, ownership, and control remain uncompromised.

---

# Vision

To build a lifelong cognitive operating system that can:

* 🧠 **Remember** conversations, documents, projects, code, photos, videos, and experiences.
* 👁️ **Understand** text, speech, images, videos, live camera feeds, screens, and future modalities.
* 🕸️ **Organize** knowledge into a semantic memory and interconnected knowledge graph.
* 💡 **Reason** about problems, plans, goals, and decisions using contextual understanding.
* ⚡ **Act** safely across computers, phones, browsers, APIs, smart devices, and future interfaces.
* 🌱 **Evolve** continuously alongside its user while remaining private, transparent, and self-hosted.

Shadow is not designed to replace human intelligence.

It is designed to **extend** it.

---

# Design Philosophy

Shadow follows a small set of principles that influence every architectural and engineering decision.

### Privacy First

Personal data belongs exclusively to the user.

### Local First

Whenever practical, computation should happen on hardware owned by the user.

### Self-Hosted

Infrastructure should be owned—not rented.

### Modular by Design

Every subsystem should be independently replaceable without affecting the rest of the platform.

### Event-Driven

Components communicate through immutable events instead of direct dependencies.

### AI Agnostic

Models evolve.

Memories persist.

### Human in Control

Every sensitive action must remain transparent, auditable, and permission-based.

---

# System Architecture

Shadow is architected like an operating system rather than a chatbot.

At its center is a lightweight **Kernel** responsible for coordinating the platform while remaining completely unaware of domain-specific logic or AI implementations.

```text
Shadow
│
├── Kernel
│   ├── Event Bus
│   ├── Scheduler
│   ├── Lifecycle Manager
│   ├── Resource Manager
│   ├── Plugin Loader
│   ├── Configuration
│   └── Security
│
├── Perception
├── Cognition
├── Action
└── Infrastructure
```

---

# Core Components

## Kernel

The deterministic core of Shadow.

The Kernel is responsible for orchestrating the entire platform while remaining domain-blind. It never performs reasoning, OCR, speech recognition, or LLM inference. Instead, it provides the stable runtime that every subsystem depends upon.

Responsibilities include:

* Event routing
* Scheduling
* Resource management
* Lifecycle management
* Configuration
* Plugin loading
* Authentication & security
* Fault recovery
* System health monitoring

The goal is simple:

> **AI failures should never become system failures.**

---

## Perception

Perception enables Shadow to understand the outside world.

It transforms raw inputs into structured events without making decisions.

Examples include:

* Text
* Speech
* OCR
* Images
* Video
* Screen understanding
* Browser state
* Documents
* Calendar
* Notifications
* Sensors

Example flow:

```text
Screen Capture
      │
      ▼
 Layout Detection
      │
      ▼
 OCR + Vision
      │
      ▼
 Structured Event
```

Perception answers only one question:

> **"What happened?"**

---

## Cognition

Cognition is the intelligence layer of Shadow.

It transforms events into understanding by combining reasoning, memory, planning, and contextual retrieval.

Responsibilities include:

* Long-term memory
* Semantic retrieval
* Knowledge graph
* Planning
* Reasoning
* Reflection
* Persona
* Context management

Cognition answers:

> **"What does this mean?"**

---

## Action

The Action layer interacts with the outside world.

Unlike Cognition, it never reasons.

It simply executes validated requests.

Capabilities include:

* Desktop automation
* Browser automation
* Mobile integration
* File management
* APIs
* Smart devices
* External services

Action answers:

> **"What should be executed?"**

---

## Infrastructure

Infrastructure provides the services required to keep Shadow operational.

Examples include:

* Storage
* Networking
* Synchronization
* Encryption
* Authentication
* Backups
* Monitoring
* Telemetry

Infrastructure exists so the user never has to think about it.

---

# Event-Driven Architecture

Shadow is fundamentally event-driven.

Every subsystem communicates exclusively through the Kernel's Event Bus.

```text
Perception
      │
      ▼
  Event Bus
      │
 ┌────┼────┐
 │    │    │
Memory Planner Logging
 │
 ▼
Action
```

The Event Bus is more than a message queue.

It is responsible for:

* Event routing
* Event prioritization
* Topic debouncing
* Backpressure handling
* Idempotent execution
* Fault isolation
* Recovery
* Observability

No subsystem communicates directly with another.

This keeps every component independently deployable, replaceable, and testable.

---

# Engineering Principles

Shadow is built as a distributed cognitive system rather than a traditional software application.

Key engineering goals include:

* Domain-driven architecture
* Event sourcing
* Fault tolerance
* Deterministic orchestration
* Modular components
* AI model independence
* Local-first execution
* Secure-by-default permissions
* Horizontal scalability
* Long-term maintainability

Every component should fail independently without compromising the stability of the platform.

---

# Development Roadmap

Development is organized around **capabilities**, not technologies.

Each phase should produce a usable system.

| Phase              | Goal                                            |
| ------------------ | ----------------------------------------------- |
| Foundation         | Build the Kernel and runtime                    |
| Conversation       | Create the Persona and conversational interface |
| Memory             | Build semantic memory and retrieval             |
| Vision             | Add perception through OCR, images, and video   |
| Actions            | Enable desktop, browser, and mobile automation  |
| Planning           | Introduce reasoning, goals, and scheduling      |
| Knowledge          | Expand memory into a complete second brain      |
| Ecosystem          | Add plugins and external integrations           |
| Distributed Shadow | Synchronize across multiple devices             |
| Autonomous Shadow  | Long-term planning and proactive assistance     |

The guiding principle throughout development is simple:

> **If development stopped today, would I still use Shadow every day?**

If the answer is **no**, the phase is not complete.

---

# Project Status

Shadow is currently in the architecture and foundation stage.

The immediate objective is to build a stable Kernel and event-driven runtime capable of supporting future cognitive capabilities without requiring architectural rewrites.

---

# License

This project is under active development.

The license will be determined before the first public release.
