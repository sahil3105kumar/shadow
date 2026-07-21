# Planner Low-Level Design

## Purpose

The Planner is responsible for transforming high-level objectives into structured, executable plans.

It decomposes complex goals into smaller tasks, identifies dependencies, selects execution strategies, and produces an execution graph that can be consumed by the Orchestrator.

The Planner determines **what needs to happen**, not **how each task is executed**.

Execution belongs to the Action subsystem.

Reasoning belongs to the Reasoning subsystem.

---

# Responsibilities

The Planner is responsible for:

- Goal decomposition.
- Task generation.
- Dependency analysis.
- Execution ordering.
- Parallelization analysis.
- Resource estimation.
- Plan optimization.
- Constraint satisfaction.
- Failure recovery planning.
- Producing executable plans.

The Planner is **not** responsible for:

- Executing tasks.
- Calling tools.
- Performing reasoning.
- Accessing memory.
- LLM inference.
- Managing workflows.
- Monitoring execution.

---

# Scope

The Planner operates on every task requiring multiple execution steps.

Typical use cases include:

```text
Question Answering

Document Analysis

Research Tasks

Workflow Automation

Code Generation

Multi-step Tool Usage

Data Processing Pipelines

Agent Coordination
```

Future capabilities include:

```text
Hierarchical Planning

Goal Scheduling

Learning-Based Planning

Multi-Agent Planning

Long-Term Goal Management

Adaptive Planning
```

---

# Package Structure

```text
shadow/
└── cognition/
    └── planner/
        ├── planner.py
        ├── decomposer.py
        ├── dependency.py
        ├── optimizer.py
        ├── validator.py
        ├── estimator.py
        └── models.py
```

Expected classes:

```text
Planner

GoalDecomposer

DependencyAnalyzer

PlanOptimizer

PlanValidator

ResourceEstimator
```

---

# Public API

```python
plan()

decompose()

optimize()

validate()

estimate()

replan()
```

Every planning request returns an immutable `ExecutionPlan`.

---

# Internal Components

The Planner consists of six logical components.

---

## Goal Decomposer

Responsible for transforming objectives into smaller tasks.

Example:

```text
Analyze contract

↓

Extract text

↓

Retrieve clauses

↓

Compare statutes

↓

Generate report
```

Decomposition is deterministic.

---

## Dependency Analyzer

Responsible for identifying relationships between tasks.

Dependency types include:

- sequential
- parallel
- conditional
- optional

The resulting dependency graph must be acyclic.

---

## Plan Optimizer

Responsible for improving execution efficiency.

Optimization considers:

- dependency reduction
- parallel execution
- resource utilization
- estimated latency

Optimization must preserve correctness.

---

## Resource Estimator

Estimates resources required for execution.

Examples:

```text
CPU

GPU

Memory

Disk

Network

Estimated Time
```

Estimates guide orchestration decisions.

---

## Plan Validator

Validates generated plans.

Checks include:

- dependency cycles
- unreachable tasks
- invalid transitions
- missing objectives
- unsupported operations

Only validated plans may proceed to execution.

---

## Execution Graph Builder

Constructs the standardized execution graph.

Output:

```text
ExecutionPlan
```

The plan becomes the input for the Orchestrator.

---

# Class Design

```text
Planner
│
├── GoalDecomposer
├── DependencyAnalyzer
├── PlanOptimizer
├── ResourceEstimator
├── PlanValidator
└── ExecutionGraphBuilder
```

Only `Planner` is publicly exposed.

---

# Data Models

Primary runtime models:

```text
ExecutionPlan

PlanNode

PlanEdge

Goal

Task

Dependency

Constraint

ExecutionEstimate
```

Example PlanNode:

```text
Task ID

Task Type

Dependencies

Constraints

Priority

Estimated Duration

Required Resources
```

---

# Design Decisions

## Planning precedes execution

Every non-trivial request produces a plan before any action is executed.

Execution should never improvise missing steps.

---

## Plans are immutable

Once validated, execution plans cannot be modified.

Changes require generating a new plan.

---

## Dependencies are explicit

Every dependency is represented in the execution graph.

Implicit execution order is prohibited.

---

## Planning is explainable

Every generated task should be traceable to the originating goal.

This supports debugging and user-facing explanations.

---

# Execution Flow

## Planning Pipeline

```text
Goal

↓

Analyze Goal

↓

Decompose

↓

Generate Tasks

↓

Analyze Dependencies

↓

Optimize

↓

Validate

↓

Generate ExecutionPlan

↓

Return
```

---

## Replanning

```text
Execution Failure

↓

Analyze Failure

↓

Reuse Valid Tasks

↓

Generate Remaining Tasks

↓

Validate

↓

Return Updated Plan
```

Replanning minimizes redundant work.

---

# State Management

The Planner is stateless.

Each planning request progresses through:

```text
Received

↓

Decomposing

↓

Optimizing

↓

Validated

↓

Completed
```

Execution plans remain immutable.

---

# Error Handling

Recoverable:

- incomplete objectives
- missing optional constraints
- low-confidence decomposition

Fatal:

- dependency cycle
- invalid execution graph
- unsupported objective
- planner failure

Failures raise typed planning exceptions.

---

# Concurrency Model

Planning supports parallel execution.

Rules:

- independent subtasks may be generated concurrently
- dependency analysis is synchronized
- optimization stages execute independently
- validation occurs after graph construction

The resulting execution graph remains deterministic.

---

# Configuration

Supported configuration includes:

```text
Maximum Planning Depth

Maximum Task Count

Optimization Strategy

Parallelism Policy

Resource Limits

Constraint Validation

Planning Timeout

Replanning Enabled
```

Configuration is loaded during application startup.

---

# Dependencies

The Planner depends on:

- Configuration
- Logging
- Exceptions
- Knowledge
- Retrieval

It may optionally consult:

- Memory
- LLM

It does **not** depend on:

- Action
- Tool Execution
- Workflow Runtime

The Planner decides *what should happen* without executing any step.

---

# Security Considerations

The Planner must:

- validate planning inputs
- reject malformed goals
- enforce execution constraints
- prevent recursive planning loops
- validate resource estimates
- isolate externally generated plans

Plans generated from untrusted sources must always be revalidated.

---

# Performance Considerations

Design goals:

- bounded planning latency
- scalable task decomposition
- efficient dependency analysis
- minimal memory overhead
- deterministic optimization

Planning should remain efficient even for large task graphs.

---

# Testing Strategy

## Unit Tests

- goal decomposition
- dependency analysis
- optimization
- validation
- resource estimation
- execution graph generation

---

## Integration Tests

- document analysis planning
- research workflows
- code generation plans
- tool orchestration plans
- agent workflows

---

## Failure Tests

- cyclic dependencies
- invalid goals
- unreachable tasks
- optimization failures
- replanning failures

---

## Performance Tests

- large execution graphs
- concurrent planning requests
- optimization latency
- dependency analysis throughput
- planning scalability

---

# Future Extensions

The Planner should support future capabilities including:

- hierarchical task networks (HTN)
- probabilistic planning
- reinforcement learning-based planning
- constraint satisfaction planning
- temporal planning
- distributed planning
- collaborative multi-agent planning
- self-improving planning strategies
- execution cost prediction
- simulation-based plan verification

These extensions should preserve the existing architecture while maintaining deterministic, explainable, and efficient plan generation.