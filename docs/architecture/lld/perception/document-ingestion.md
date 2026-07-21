# Document Ingestion Low-Level Design

## Purpose

The Document Ingestion component is the entry point into the Perception subsystem.

Its responsibility is to safely receive documents from external sources, identify their characteristics, validate them, prepare them for downstream processing, and convert them into a standardized internal representation.

It does **not** perform OCR, semantic analysis, reasoning, or AI inference.

It answers one question:

> **"What document have I received, and how should it be processed?"**

---

# Responsibilities

The Document Ingestion component is responsible for:

- Accepting input documents.
- Detecting document type.
- Detecting MIME type.
- Validating file integrity.
- Extracting document metadata.
- Splitting multi-page documents.
- Detecting embedded text layers.
- Routing documents to the appropriate processing pipeline.
- Generating ingestion metadata.
- Producing standardized document objects.

The component is **not** responsible for:

- OCR
- Image preprocessing
- Information extraction
- Reasoning
- Chunking
- Embedding generation
- LLM interaction

---

# Scope

Supported input sources include:

- Local files
- API uploads
- CLI inputs
- Plugin-generated documents

Supported document formats:

```text
PDF

PNG

JPEG

TIFF

BMP

WEBP

TXT

Markdown

HTML
```

Future support:

```text
DOCX

PPTX

XLSX

Emails

ZIP archives

EPUB

RTF
```

---

# Package Structure

```text
shadow/
└── perception/
    └── ingestion/
        ├── manager.py
        ├── detector.py
        ├── validator.py
        ├── loader.py
        ├── router.py
        ├── metadata.py
        └── models.py
```

Expected classes:

```text
DocumentIngestionManager

DocumentLoader

DocumentDetector

DocumentValidator

DocumentRouter

MetadataExtractor
```

---

# Public API

```python
ingest()

detect()

validate()

load()

extract_metadata()

route()
```

Every ingestion request returns a `DocumentArtifact`.

---

# Internal Components

The Document Ingestion component consists of six logical components.

---

## Document Loader

Responsible for:

- opening files
- streaming large documents
- validating accessibility
- reading document headers

Large files should be streamed whenever possible.

---

## Document Detector

Responsible for detecting:

- MIME type
- extension
- encoding
- document family

Detection prioritizes content signatures over filename extensions.

---

## Validator

Responsible for validating:

- supported format
- maximum size
- corruption
- accessibility
- file completeness

Invalid documents are rejected before further processing.

---

## Metadata Extractor

Extracts metadata including:

```text
Filename

Extension

MIME Type

Size

Checksum

Creation Time

Modification Time

Page Count

Language (if detectable)

Embedded Text Presence
```

Metadata extraction must not modify the document.

---

## Document Router

Determines which downstream pipeline receives the document.

Routing examples:

```text
PDF with text layer
        ↓
Native Text Extraction

Scanned PDF
        ↓
OCR Pipeline

Image
        ↓
OCR Pipeline

Plain Text
        ↓
Text Pipeline

HTML
        ↓
HTML Parser
```

Routing decisions are deterministic.

---

## Artifact Builder

Constructs the standardized runtime representation.

Output:

```text
DocumentArtifact
```

Every downstream component consumes this artifact.

---

# Class Design

```text
DocumentIngestionManager
│
├── DocumentLoader
├── DocumentDetector
├── Validator
├── MetadataExtractor
├── Router
└── ArtifactBuilder
```

Only `DocumentIngestionManager` is publicly exposed.

---

# Data Models

Primary runtime models:

```text
DocumentArtifact

DocumentMetadata

DocumentSource

DocumentType

MimeType

RoutingDecision

ValidationResult
```

Example DocumentArtifact:

```text
Document ID

Source

Filename

Type

Metadata

Pages

Pipeline

Timestamp
```

---

# Design Decisions

## Content determines type

File extensions are advisory.

The detector uses file signatures and document structure to determine the actual format.

---

## Immutable artifacts

After ingestion, the original document representation never changes.

Subsequent stages generate derived artifacts instead of modifying the source.

---

## Routing is deterministic

Identical documents must always follow identical processing paths.

This simplifies testing, reproducibility, and debugging.

---

## Metadata precedes processing

Metadata extraction always occurs before OCR or preprocessing.

Downstream components should never re-read document headers.

---

# Execution Flow

## Ingestion

```text
Receive Document

↓

Validate Access

↓

Detect Format

↓

Extract Metadata

↓

Validate Document

↓

Determine Processing Pipeline

↓

Build DocumentArtifact

↓

Return
```

---

## Routing

```text
DocumentArtifact

↓

Evaluate Characteristics

↓

Select Pipeline

↓

Attach Routing Metadata

↓

Dispatch
```

---

# State Management

The Document Ingestion component is stateless.

Each document progresses through:

```text
Received

↓

Loaded

↓

Validated

↓

Routed

↓

Completed
```

Artifacts become immutable after completion.

---

# Error Handling

Recoverable:

- unsupported optional metadata
- missing creation timestamp
- unknown language

Fatal:

- unreadable document
- corrupted file
- unsupported format
- invalid MIME type
- inaccessible source

All failures raise typed ingestion exceptions.

---

# Concurrency Model

Document ingestion supports concurrent execution.

Rules:

- independent documents process concurrently
- metadata extraction is isolated
- routing decisions are independent
- large document streaming does not block other requests

Each ingestion request owns its execution context.

---

# Configuration

Supported configuration includes:

```text
Maximum File Size

Allowed MIME Types

Allowed Extensions

Streaming Threshold

Temporary Workspace

Checksum Algorithm

Maximum Page Count

Supported Encodings
```

Configuration is loaded during application startup.

---

# Dependencies

The Document Ingestion component depends on:

- Kernel
- Configuration
- Filesystem
- Logging
- Security
- Serialization

It does **not** depend on:

- OCR
- Cognition
- Memory
- LLM
- Action

Instead, it routes documents toward the appropriate perception pipeline.

---

# Security Considerations

The Document Ingestion component must:

- validate every input
- reject malformed documents
- prevent directory traversal
- sanitize filenames
- enforce size limits
- isolate temporary storage
- verify MIME types using content inspection

Documents should always be treated as **untrusted input**.

---

# Performance Considerations

Design goals:

- fast format detection
- streaming support
- low memory usage
- deterministic routing
- scalable concurrent ingestion

Metadata extraction should avoid loading entire documents into memory whenever possible.

---

# Testing Strategy

## Unit Tests

- MIME detection
- document validation
- metadata extraction
- routing decisions
- artifact construction

---

## Integration Tests

- PDF ingestion
- image ingestion
- HTML ingestion
- text ingestion
- API upload pipeline

---

## Failure Tests

- corrupted PDF
- oversized document
- unsupported MIME type
- inaccessible file
- malformed image

---

## Performance Tests

- large PDF ingestion
- concurrent uploads
- streaming performance
- metadata extraction latency
- routing throughput

---

# Future Extensions

The Document Ingestion component should support future capabilities including:

- cloud storage connectors
- remote URL ingestion
- archive extraction
- encrypted document handling
- incremental document streaming
- distributed ingestion workers
- document deduplication
- automatic language detection
- content fingerprinting
- ingestion policy engine

These extensions should preserve the existing architecture while maintaining secure, deterministic, and scalable document ingestion.