# LLM Interface Low-Level Design

## Purpose

The LLM Interface is responsible for interacting with Large Language Models (LLMs) through a unified, provider-independent abstraction.

It prepares prompts, manages context, invokes models, validates responses, and normalizes outputs before they enter the Cognition pipeline.

Unlike the Reasoning Engine, the LLM Interface does **not** determine truth.

Unlike the Planner, it does **not** create execution strategies.

Unlike the Retrieval Engine, it does **not** search knowledge.

Its responsibility is limited to obtaining probabilistic language model outputs in a safe, consistent, and explainable manner.

It answers one question:

> **"Given this context, what does the selected language model produce?"**

---

# Responsibilities

The LLM Interface is responsible for:

- Prompt construction.
- Context assembly.
- Model selection.
- Model invocation.
- Response validation.
- Output normalization.
- Token accounting.
- Cost tracking.
- Retry handling.
- Producing standardized LLM responses.

The component is **not** responsible for:

- Planning
- Reasoning
- Knowledge retrieval
- Memory management
- Tool execution
- Workflow orchestration

---

# Scope

Supported providers include:

```text
OpenAI

Anthropic

Google Gemini

Local Models

Ollama

vLLM

Custom Model Providers
```

Future capabilities include:

```text
Multi-LLM Consensus

Mixture-of-Experts

Automatic Model Routing

Streaming Generation

Vision-Language Models

Speech Models

Fine-Tuned Domain Models
```

---

# Package Structure

```text
shadow/
└── cognition/
    └── llm/
        ├── manager.py
        ├── prompt.py
        ├── providers.py
        ├── validation.py
        ├── routing.py
        ├── telemetry.py
        └── models.py
```

Expected classes:

```text
LLMManager

PromptBuilder

ProviderAdapter

ResponseValidator

ModelRouter

TelemetryCollector
```

---

# Public API

```python
generate()

complete()

chat()

stream()

validate()

estimate_tokens()

select_model()
```

Every request returns an immutable `LLMResponse`.

---

# Internal Components

The LLM Interface consists of six logical components.

---

## Prompt Builder

Responsible for constructing prompts.

Inputs include:

- user requests
- retrieved context
- memory references
- system instructions
- execution metadata

Prompt construction is deterministic.

---

## Model Router

Responsible for selecting the most appropriate model.

Selection may consider:

- latency
- cost
- context length
- modality
- provider availability
- required capabilities

Routing policies are configurable.

---

## Provider Adapter

Provides a unified interface across model providers.

Responsibilities include:

- request formatting
- authentication
- retries
- provider-specific normalization
- error translation

Provider-specific behavior is hidden from higher-level systems.

---

## Response Validator

Validates generated outputs.

Checks include:

- schema validation
- JSON parsing
- required fields
- token limits
- malformed outputs

Invalid responses may trigger retries.

---

## Telemetry Collector

Collects execution metrics.

Examples:

```text
Latency

Prompt Tokens

Completion Tokens

Cost

Retries

Provider

Model

Cache Hit
```

Telemetry supports monitoring and optimization.

---

## Response Builder

Constructs the standardized response artifact.

Output:

```text
LLMResponse
```

Every response contains associated metadata.

---

# Class Design

```text
LLMManager
│
├── PromptBuilder
├── ModelRouter
├── ProviderAdapter
├── ResponseValidator
├── TelemetryCollector
└── ResponseBuilder
```

Only `LLMManager` is publicly exposed.

---

# Data Models

Primary runtime models:

```text
LLMRequest

LLMResponse

Prompt

PromptMessage

GenerationParameters

ModelDescriptor

Provider

TokenUsage

GenerationMetadata
```

Example LLMResponse:

```text
Content

Model

Provider

Finish Reason

Token Usage

Latency

Confidence (Optional)

Metadata
```

---

# Design Decisions

## Providers are abstracted

Higher-level systems interact with one interface regardless of provider.

Switching providers requires no Cognition changes.

---

## Prompt construction is deterministic

Context ordering, formatting, and instruction hierarchy follow predefined rules.

Prompt generation should be reproducible.

---

## Validation is mandatory

Every response is validated before entering downstream components.

Malformed outputs are rejected.

---

## LLMs are probabilistic

LLM responses are recommendations.

They must be verified by the Reasoning Engine whenever factual correctness is required.

---

# Execution Flow

## Generation Pipeline

```text
Generation Request

↓

Build Prompt

↓

Select Model

↓

Invoke Provider

↓

Validate Response

↓

Normalize Output

↓

Collect Telemetry

↓

Generate LLMResponse

↓

Return
```

---

## Retry Flow

```text
Provider Failure

↓

Determine Retry Policy

↓

Retry Same Provider

↓

Fallback Provider

↓

Return Response

or

Raise Exception
```

Retries remain bounded.

---

# State Management

The LLM Interface is stateless.

Each request progresses through:

```text
Received

↓

Prompt Built

↓

Generating

↓

Validated

↓

Completed
```

No conversational state is stored internally.

Conversation history is supplied externally.

---

# Error Handling

Recoverable:

- provider timeout
- malformed JSON
- token limit exceeded
- transient network failures
- unavailable model

Fatal:

- invalid prompt
- unsupported provider
- authentication failure
- validation failure after retries

Failures raise typed LLM exceptions.

---

# Concurrency Model

LLM requests support concurrent execution.

Rules:

- independent generations execute concurrently
- telemetry collection is asynchronous
- provider retries remain isolated
- response validation executes after generation

Concurrency must not affect deterministic prompt construction.

---

# Configuration

Supported configuration includes:

```text
Default Provider

Default Model

Maximum Context Length

Maximum Tokens

Temperature

Top-p

Retry Policy

Timeout

Streaming Enabled

Cache Enabled

Telemetry Enabled
```

Configuration is loaded during application startup.

---

# Dependencies

The LLM Interface depends on:

- Configuration
- Logging
- Serialization
- Security

It communicates with:

- External LLM Providers
- Local Model Servers
- Telemetry Services

It does **not** depend on:

- Planner
- Reasoning
- Retrieval
- Action

The LLM Interface provides language generation services to higher-level cognitive components.

---

# Security Considerations

The LLM Interface must:

- sanitize prompts
- protect API credentials
- prevent prompt injection propagation
- validate provider responses
- redact sensitive information
- enforce request size limits

Secrets must never be embedded directly into prompts.

---

# Performance Considerations

Design goals:

- low generation latency
- efficient prompt construction
- provider-independent scalability
- bounded retries
- predictable resource usage

Frequently repeated prompts may be served through configurable caching mechanisms.

---

# Testing Strategy

## Unit Tests

- prompt construction
- provider abstraction
- routing
- response validation
- telemetry collection
- retry policies

---

## Integration Tests

- OpenAI integration
- Anthropic integration
- Ollama integration
- vLLM integration
- end-to-end cognition pipeline

---

## Failure Tests

- provider unavailable
- malformed responses
- authentication failures
- retry exhaustion
- timeout handling

---

## Performance Tests

- concurrent generations
- token throughput
- latency benchmarks
- cache performance
- provider failover latency

---

# Future Extensions

The LLM Interface should support future capabilities including:

- automatic prompt optimization
- multi-model consensus generation
- speculative decoding
- semantic response caching
- adaptive model routing
- reinforcement-based provider selection
- multimodal generation
- structured function calling
- domain-specific fine-tuned models
- offline inference orchestration

These extensions should preserve the existing architecture while maintaining provider independence, deterministic prompt construction, secure model interaction, and reliable language generation.