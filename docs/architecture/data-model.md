# Data Model

> *"Data represents the long-term state of Shadow. Events describe how that state changes."*

---

# Purpose

The Data Model defines the logical information architecture of Shadow.

It specifies the core entities, their relationships, ownership boundaries, persistence principles, and lifecycle without prescribing a specific database technology.

The model is intended to remain stable even as storage implementations evolve.

---

# Design Principles

The data model follows these principles:

* User ownership
* Domain separation
* Explicit relationships
* Technology independence
* Schema evolution
* Auditability
* Durability
* Minimal duplication

---

# Core Entities

Shadow persists information as a collection of interconnected entities.

---

## User

Represents the owner or authorized user of the system.

Responsibilities include:

* Identity
* Preferences
* Permissions
* Personas
* Settings

A User owns every Workspace.

---

## Workspace

Represents an isolated organizational boundary.

Examples include:

* Personal
* Research
* Work
* University
* Projects

Every persistent entity belongs to exactly one Workspace.

---

## Conversation

Represents an interaction session between the user and Shadow.

Contains:

* Messages
* Context references
* Participants
* Metadata
* Timeline

Conversations are immutable historical records.

---

## Message

Represents a single communication within a Conversation.

Examples include:

* User message
* Assistant response
* System notification
* Tool output

Messages reference context rather than duplicating information.

---

## Memory

Represents persistent knowledge approved for long-term retention.

Examples include:

* Preferences
* Facts
* Recurring workflows
* Important events
* Long-term notes

Memories are retrievable through semantic similarity.

---

## Knowledge Entity

Represents a structured concept within the Knowledge Graph.

Examples include:

* Person
* Organization
* Project
* Document
* Concept
* Location

Entities exist independently of conversations.

---

## Relationship

Represents an explicit connection between two Knowledge Entities.

Examples include:

* WorksOn
* Owns
* References
* DependsOn
* RelatedTo
* MemberOf

Relationships form the Knowledge Graph.

---

## Document

Represents an imported or generated document.

Examples include:

* PDF
* DOCX
* Markdown
* Notes
* Reports

Documents may produce memories and knowledge entities.

---

## Media

Represents non-textual assets.

Examples include:

* Images
* Audio
* Video
* Screenshots

Media remains independent from derived understanding.

---

## Task

Represents a unit of planned or executable work.

Contains:

* Objective
* Status
* Priority
* Dependencies
* Deadlines

Tasks may belong to workflows.

---

## Workflow

Represents a collection of related Tasks.

Supports:

* Sequential execution
* Parallel execution
* Conditional execution

---

## Plugin

Represents an installed extension.

Contains:

* Metadata
* Version
* Permissions
* Configuration
* Lifecycle state

Plugins remain isolated from core system data.

---

## Configuration

Represents persistent system configuration.

Examples include:

* Runtime settings
* Feature flags
* Environment preferences
* Plugin settings

Configuration remains separate from user content.

---

# Entity Relationships

```text id="s2hgr7"
User
 │
 ▼
Workspace
 │
 ├──────────────┐
 ▼              ▼
Conversation   Memory
 │              │
 ▼              ▼
Message     Knowledge Entity
                │
                ▼
          Relationship
                │
                ▼
            Knowledge Graph

Workspace
 │
 ├──────────────┐
 ▼              ▼
Document      Media
 │
 ▼
Knowledge Entity

Workflow
 │
 ▼
Task

Workspace
 │
 ▼
Plugin

Workspace
 │
 ▼
Configuration
```

---

# Ownership Model

Every persistent entity has exactly one owner.

Ownership hierarchy:

```text id="4m9s1d"
User
 │
 ▼
Workspace
 │
 ▼
Entity
```

Cross-workspace references should be avoided unless explicitly supported.

---

# Identity

Every entity possesses:

* Unique identifier
* Creation timestamp
* Modification timestamp
* Version
* Owner
* Workspace
* Metadata

Identifiers remain immutable throughout the entity lifecycle.

---

# Lifecycle

Every entity follows a common lifecycle.

```text id="7o1sfp"
Created
    │
    ▼
Updated
    │
    ▼
Referenced
    │
    ▼
Archived
    │
    ▼
Deleted
```

Deletion policies depend on entity type.

---

# Persistence Principles

Persistent data should:

* Survive system restarts
* Preserve integrity
* Support version evolution
* Remain recoverable
* Support backup and restoration

Persistence mechanisms remain implementation-independent.

---

# Relationships

Relationships should be explicit rather than inferred during storage.

Relationship types include:

* Ownership
* Reference
* Dependency
* Association
* Hierarchy
* Temporal sequence

The Knowledge Graph is responsible for managing semantic relationships.

---

# Indexing

Entities should support indexing by:

* Identifier
* Workspace
* Timestamp
* Entity type
* Metadata
* Semantic embeddings (where applicable)

Indexing strategies remain implementation-specific.

---

# Versioning

Every persistent entity supports versioning.

Version history enables:

* Auditing
* Conflict resolution
* Synchronization
* Rollback
* Schema migration

Version history should not modify historical records.

---

# Data Integrity

The system shall maintain:

* Referential integrity
* Ownership integrity
* Schema validity
* Version consistency
* Relationship consistency

Integrity checks should occur during persistence.

---

# Backup and Recovery

Persistent data should support:

* Full backup
* Incremental backup
* Point-in-time recovery
* Integrity verification

Recovery should preserve relationships between entities.

---

# Security

Persistent data shall:

* Respect ownership boundaries
* Enforce authorization
* Support encryption
* Protect sensitive information
* Maintain audit history

Security policies apply consistently across all entity types.

---

# Extensibility

New entity types may be introduced without affecting existing entities.

Extensions should:

* Preserve ownership rules
* Respect relationship models
* Integrate with existing lifecycle management

The logical data model should remain stable as new capabilities are added.

---

# Success Criteria

The data model succeeds when:

* Information remains durable and consistent.
* Relationships are explicit and navigable.
* Storage implementations remain replaceable.
* User ownership is preserved.
* New entity types integrate without disrupting the existing model.
