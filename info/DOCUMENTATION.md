# VISTA

### Vector Intelligent Semantic Search & Text Analysis

**A Metadata-First Hybrid Semantic Search Engine for Unstructured Medical Records**

**Lead Developer:** Ansh Gaur
**Contact:** anshgaurx@gmail.com · ansh1291g@gmail.com
**GitHub:** [@anshgaurx](https://github.com/anshgaurx) · [@anshxgaur](https://github.com/anshxgaur) · [@Ansh17gaur1](https://github.com/Ansh17gaur1)
**Document Version:** 2.0
**Status:** Design + Partial Implementation

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Problem Statement & Motivation](#2-problem-statement--motivation)
3. [Goals & Non-Goals](#3-goals--non-goals)
4. [System Architecture Overview](#4-system-architecture-overview)
5. [Core Technology Stack](#5-core-technology-stack)
6. [Data Model](#6-data-model)
7. [Ingestion Pipeline (Phase A)](#7-ingestion-pipeline-phase-a)
8. [Retrieval Pipeline (Phase B)](#8-retrieval-pipeline-phase-b)
9. [Chunking Strategy](#9-chunking-strategy)
10. [Embedding Strategy](#10-embedding-strategy)
11. [FAISS Indexing Deep Dive](#11-faiss-indexing-deep-dive)
12. [PostgreSQL Schema Design](#12-postgresql-schema-design)
13. [MinIO Object Storage Design](#13-minio-object-storage-design)
14. [API Design (FastAPI)](#14-api-design-fastapi)
15. [Frontend / UI Design (Streamlit)](#15-frontend--ui-design-streamlit)
16. [Hardware & Deployment Strategy](#16-hardware--deployment-strategy)
17. [Memory Optimization Deep Dive](#17-memory-optimization-deep-dive)
18. [Security & Data Privacy](#18-security--data-privacy)
19. [Error Handling & Fault Tolerance](#19-error-handling--fault-tolerance)
20. [Evaluation Methodology](#20-evaluation-methodology)
21. [Performance Benchmarks (Target vs Actual)](#21-performance-benchmarks-target-vs-actual)
22. [Scalability Considerations](#22-scalability-considerations)
23. [Testing Strategy](#23-testing-strategy)
24. [Development Roadmap](#24-development-roadmap)
25. [Known Limitations](#25-known-limitations)
26. [Risk Register](#26-risk-register)
27. [Glossary](#27-glossary)
28. [Appendix A: Sample Queries](#28-appendix-a-sample-queries)
29. [Appendix B: Configuration Reference](#29-appendix-b-configuration-reference)
30. [References](#30-references)

---

## 1. Executive Summary

VISTA (Vector Intelligent Semantic Search & Text Analysis) is a semantic data warehouse designed to ingest, securely store, and intelligently retrieve information from a large corpus of unstructured medical reports. The target corpus is **50 GB**, comprising approximately **50,000 documents**, derived from an augmented and scaled version of the MTSamples transcription dataset.

The system is built around a **metadata-first hybrid retrieval architecture**. Rather than treating the entire corpus as a single undifferentiated vector space, VISTA separates concerns into three distinct layers:

- A **relational metadata layer** (PostgreSQL) that handles structured, filterable attributes.
- A **vector embedding layer** (FAISS) that handles unstructured semantic similarity.
- An **object storage layer** (MinIO) that handles raw document persistence.

This separation allows the system to perform **coarse filtering before fine-grained semantic search**, which reduces the effective search space dramatically before any expensive vector computation happens. It also creates a natural security boundary: personally identifiable information (PII) never enters the vector space at all.

The system is designed to run within the constraints of a free-tier cloud instance (24 GB RAM), which forces deliberate memory-engineering decisions — most notably the use of FAISS's IVF-PQ compressed indexing rather than a naive flat index.

This document describes the full system design: architecture, data model, pipelines, indexing strategy, hardware plan, security model, evaluation methodology, and roadmap.

---

## 2. Problem Statement & Motivation

Medical reports are typically stored as unstructured free text. Traditional retrieval over this kind of data falls into one of two unsatisfying categories:

1. **Pure keyword / full-text search** (e.g., basic SQL `LIKE` queries or classic inverted indices) — fast and cheap, but blind to semantic meaning. A search for "heart attack" will not reliably surface a report that says "myocardial infarction" unless the system has been explicitly taught the synonym.

2. **Pure vector / semantic search over the entire corpus** — captures meaning well, but at scale (tens of thousands of documents, each split into multiple chunks) becomes computationally expensive and memory-hungry, especially under constrained hardware.

VISTA's core motivation is to avoid choosing between these two extremes by combining them: use cheap, structured metadata filtering to shrink the candidate set first, then apply expensive, meaning-aware vector search only to that shrunk set.

A secondary motivation is **data governance**. Medical data is sensitive by nature. A system that embeds raw PII into a vector index makes that PII recoverable in ways that are hard to audit or restrict. By keeping PII exclusively inside a relational database with well-understood access control mechanisms, and keeping the vector layer semantically "blind" to identity, VISTA aims to make the privacy story easier to reason about and audit.

---

## 3. Goals & Non-Goals

### 3.1 Goals

- Ingest and index a 50 GB / ~50,000-document corpus of medical reports.
- Support hybrid queries that combine structured filters (specialty, date range, keyword) with free-text semantic search.
- Operate within a 24 GB RAM budget on commodity/free-tier cloud hardware.
- Keep raw PII out of the vector index entirely.
- Provide sub-second (target) query latency for hybrid searches once the candidate set has been narrowed.
- Provide an interactive UI for exploring and validating search results.

### 3.2 Non-Goals (for the current phase)

- VISTA is **not** attempting to be a general-purpose document management system — it is scoped to medical report retrieval.
- VISTA does **not** currently attempt real-time streaming ingestion; ingestion is treated as a batch process.
- VISTA does **not** implement a full clinical NLP pipeline (e.g., ICD-10 coding, entity linking to a medical ontology) — metadata extraction is intentionally lightweight (SpaCy/Regex-based).
- VISTA does **not** currently provide multi-tenant isolation (i.e., separate customer/hospital data boundaries) — this is a possible future extension, not a current requirement.
- VISTA is not, at this stage, HIPAA-certified or independently audited; the architecture is designed with privacy principles in mind but has not undergone formal compliance review.

---

## 4. System Architecture Overview

At a high level, VISTA consists of five cooperating components:

```
                          ┌─────────────────────┐
                          │      Streamlit        │
                          │   (Frontend / UI)     │
                          └───────────┬──────────┘
                                      │  HTTP
                                      ▼
                          ┌─────────────────────┐
                          │       FastAPI          │
                          │  (Orchestration Layer) │
                          └──────┬──────┬─────────┘
                                 │      │
                 ┌───────────────┘      └────────────────┐
                 ▼                                        ▼
      ┌─────────────────────┐                 ┌─────────────────────┐
      │      PostgreSQL        │                 │        FAISS          │
      │ (Metadata / Filtering) │                 │ (Vector Similarity)   │
      └───────────┬───────────┘                 └───────────┬───────────┘
                  │                                          │
                  └───────────────────┬──────────────────────┘
                                       ▼
                          ┌─────────────────────┐
                          │        MinIO            │
                          │  (Raw Document Store)   │
                          └─────────────────────┘
```

Each layer has a single, well-defined responsibility:

| Layer | Responsibility | What it explicitly does NOT do |
|---|---|---|
| FastAPI | Request orchestration, validation, coordination between layers | Does not persist data itself |
| PostgreSQL | Structured metadata storage, coarse filtering, source-of-truth for document existence | Does not store raw text or vectors |
| FAISS | In-memory vector similarity search | Does not store metadata or raw text |
| MinIO | Raw `.txt` file persistence | Does not perform any search or filtering |
| Streamlit | User-facing query interface, visualization | Does not talk to storage layers directly — always goes through FastAPI |

This is deliberately similar in spirit to a **CQRS-like separation** (Command/Query segregation) — write paths and read paths touch different subsystems, and each subsystem is optimized for a narrow job rather than being a jack-of-all-trades.

---

## 5. Core Technology Stack

| Component | Technology | Purpose |
|---|---|---|
| Backend API | **FastAPI** | Orchestrates ingestion, chunking, and search endpoints |
| Vector Engine | **FAISS** | Maintains chunk-level embeddings in RAM for fast semantic search |
| Metadata DB | **PostgreSQL** | Stores document-level metadata (Patient ID, Date, Specialty, Keywords) for coarse filtering |
| Object Store | **MinIO** | Stores raw, unstructured `.txt` medical reports |
| Frontend UI | **Streamlit** | Interactive search and visualization interface |
| Metadata Extraction | **SpaCy / Regex** | Lightweight structured-field extraction from free text |
| Embedding Model | **all-MiniLM-L6-v2** (or equivalent lightweight sentence-transformer) | Converts text chunks into dense vector representations |

### 5.1 Why FastAPI

FastAPI uses Python type hints and Pydantic models for automatic request validation and response serialization, which reduces boilerplate and catches malformed requests early. It natively supports asynchronous route handlers, which matters here because ingestion and retrieval are both I/O-bound workloads (disk/object-store writes, DB queries, network calls to the vector layer) rather than CPU-bound ones. Async handlers let the API server handle many concurrent ingestion/search requests without blocking on I/O wait time.

### 5.2 Why FAISS

FAISS (Facebook AI Similarity Search) is an open-source library from Meta AI Research purpose-built for efficient similarity search and clustering over dense vectors. It supports a spectrum of index types, from exact brute-force search (flat index) to approximate nearest-neighbor (ANN) structures such as HNSW and IVF-PQ. This range matters because it lets the system trade off accuracy against memory/speed depending on corpus size — a decision VISTA makes explicitly given its 24 GB RAM ceiling (see Section 11 and Section 17).

### 5.3 Why PostgreSQL

PostgreSQL is a mature, ACID-compliant relational database with strong support for structured querying, indexing (B-tree, GIN for keyword arrays), and row-level security — which is directly useful for enforcing access control over sensitive fields like Patient ID.

### 5.4 Why MinIO

MinIO provides an S3-compatible object storage API, which means the raw document storage layer can later be swapped for actual AWS S3, or another S3-compatible provider, with minimal code change. It is also self-hostable, which fits the free-tier / cost-conscious deployment strategy.

### 5.5 Why Streamlit

Streamlit allows a functional, interactive search UI to be built quickly in pure Python, without a separate frontend build pipeline (no React/webpack toolchain needed). This is well suited to a project where the frontend's job is to visualize search results and expose filter controls, not to be a polished consumer product.

---

## 6. Data Model

### 6.1 Conceptual Entities

- **Document** — A single raw medical report (`.txt` file), with a unique ID, uploaded once.
- **Metadata Record** — A structured row associated 1:1 with a Document, containing extracted fields.
- **Chunk** — A sub-segment of a Document's text, produced during ingestion, small enough to embed meaningfully.
- **Embedding** — A dense vector representation of a single Chunk, stored in FAISS.

### 6.2 Entity Relationship Summary

```
Document (1) ──────── (1) Metadata Record
    │
    │ (1)
    │
    ▼ (many)
  Chunk ──────── (1) Embedding
```

- One Document has exactly one Metadata Record.
- One Document is split into many Chunks during ingestion.
- One Chunk has exactly one Embedding in FAISS.
- A Chunk always retains a back-reference to its parent Document ID, so a semantic hit on a chunk can always be traced back to (a) its full document in MinIO and (b) its metadata row in PostgreSQL.

### 6.3 Identifiers

- `document_id` — UUID, generated at ingestion time, primary key across all three storage layers (Postgres row key, MinIO object key prefix, FAISS metadata mapping key).
- `chunk_id` — Composite or UUID, unique per chunk, used as the FAISS vector ID.

Using a consistent `document_id` across all three layers is what makes the hybrid retrieval pipeline possible — PostgreSQL's coarse filter returns a set of `document_id`s, and FAISS is queried only against chunks whose `document_id` is in that set.

---

## 7. Ingestion Pipeline (Phase A)

### 7.1 Pipeline Diagram

```
Raw .txt file
   │
   ▼
[1] MinIO Storage ──────────► returns unique S3 URI
   │
   ▼
[2] Metadata Extraction (SpaCy / Regex) ──► Patient ID, Specialty, Date, Keywords
   │
   ▼
[3] PostgreSQL Commit ──────────► S3 URI + metadata = source of truth
   │
   ▼
[4] Chunking ──► Embedding (all-MiniLM-L6-v2) ──► FAISS Index
```

### 7.2 Step-by-Step Description

**Step 1 — File Storage.**
Raw `.txt` documents are written directly into a MinIO bucket. MinIO returns a unique S3-compatible URI for each document. This URI is the durable pointer used later to fetch the original document on demand.

**Step 2 — Metadata Extraction.**
FastAPI triggers a lightweight extraction script using SpaCy (for named entity recognition where applicable) and Regex (for structured patterns like dates or ID formats) to pull out fields such as:
- Patient ID
- Medical Specialty
- Report Date
- Keywords / key phrases

This step is intentionally lightweight rather than a full clinical NLP pipeline — the goal is structured filtering support, not diagnostic coding.

**Step 3 — Postgres Commit.**
The MinIO S3 URI, together with the extracted metadata, is committed to PostgreSQL as a single row. This row is treated as the **single source of truth** for whether a document exists in the system and what its structured attributes are. If this commit fails, the document is considered not-yet-ingested even if the raw file already exists in MinIO — this ordering matters for consistency (see Section 19).

**Step 4 — Vectorization & Indexing.**
The document's text is split into chunks (see Section 9), each chunk is embedded using a lightweight local embedding model (`all-MiniLM-L6-v2` or equivalent), and the resulting vectors are added to the FAISS index, tagged with their parent `document_id`.

### 7.3 Idempotency Considerations

Because ingestion is a multi-step process across three systems, the pipeline should be designed so that re-running ingestion on the same file does not produce duplicate entries. This typically means:
- Computing a content hash of the raw file before upload, and checking PostgreSQL for an existing row with that hash before proceeding.
- Treating `document_id` assignment as deterministic (or checked-for-existence) rather than always-random, where practical.

### 7.4 Batch vs Streaming

The current design treats ingestion as a **batch** process — appropriate for the initial 50 GB corpus load, which is expected to be a one-time or periodic bulk operation rather than a continuous stream of new documents. Batch ingestion also aligns with the hardware strategy of using on-demand GPU compute for the initial vectorization pass (see Section 16).

---

## 8. Retrieval Pipeline (Phase B)

### 8.1 Pipeline Diagram

```
Query (free text + optional filters)
   │
   ▼
[1] Coarse Filter (PostgreSQL WHERE clause) ──► 50,000 docs → few hundred
   │
   ▼
[2] Fine-Grained Search (FAISS cosine similarity) ──► ranked chunks
   │
   ▼
[3] Retrieval ──► chunks + similarity scores (+ parent doc from MinIO, if requested)
```

### 8.2 Step-by-Step Description

**Step 1 — Coarse Filtering (SQL).**
When a query arrives, PostgreSQL executes a `WHERE` clause built from the explicit metadata parameters supplied by the user (e.g., specialty = "cardiology" AND report_date >= '2025-01-01'). This step alone can shrink the candidate set from the full 50,000-document corpus down to a few hundred documents, before any vector math is performed.

**Step 2 — Fine-Grained Semantic Search (FAISS).**
The user's free-text query is embedded using the same model used at ingestion time (`all-MiniLM-L6-v2`), and FAISS computes cosine similarity between the query vector and only the chunk vectors belonging to the pre-filtered document set. This is the step that gives VISTA its "semantic" search capability — it can match "myocardial infarction" against a query for "heart attack" because the embedding space captures that similarity, not just literal keyword overlap.

**Step 3 — Retrieval.**
The system returns the top-ranked chunks along with their similarity scores. If the caller requests full context, the parent document is fetched from MinIO using the `document_id` stored alongside each chunk.

### 8.3 Query Types Supported

- **Filter-only query** — pure metadata filtering, no semantic component (behaves like a normal SQL query).
- **Semantic-only query** — free-text search across the entire corpus with no metadata narrowing (falls back to searching the full FAISS index, which is the most expensive case).
- **Hybrid query** (primary use case) — metadata filter + free-text semantic search, combining both pipeline steps.

### 8.4 Why Filter-First Matters

Reducing the candidate set before the vector search step is not just a performance optimization — it changes the computational complexity of the query. A brute-force or even IVF-based vector search over a few hundred vectors is dramatically cheaper than the same search over hundreds of thousands of chunk vectors (50,000 documents × multiple chunks per document). This is the central efficiency argument behind the "metadata-first hybrid" design.

---

## 9. Chunking Strategy

*(This section documents the intended approach; exact parameters should be tuned empirically against the real corpus — see Section 20.)*

### 9.1 Why Chunk at All

Embedding an entire medical report as a single vector loses granularity — a report might discuss multiple topics (history, medications, diagnosis, plan), and a single averaged embedding would blur all of them together. Chunking allows each semantically coherent piece of the report to be matched independently against a query.

### 9.2 Chunking Approach

- **Unit of chunking:** Paragraph- or section-aware splitting where possible (using report structure/headers as natural boundaries), falling back to fixed-size token windows where no clear structural markers exist.
- **Target chunk size:** Small enough to stay within the embedding model's effective context window and to keep each chunk topically coherent, large enough to retain surrounding context (a bare few words is rarely useful on its own).
- **Overlap:** A modest overlap between consecutive chunks helps avoid losing meaning at chunk boundaries (e.g., a sentence describing a diagnosis being split awkwardly across two chunks).

### 9.3 Chunk-to-Parent Mapping

Every chunk stores:
- `chunk_id` (unique)
- `document_id` (parent reference, used for the FAISS→Postgres→MinIO join)
- `chunk_index` (ordinal position within the parent document, useful for reconstructing context or displaying "surrounding text" in the UI)

### 9.4 Medical-Text-Specific Considerations

Medical reports often have a semi-structured format (e.g., "History of Present Illness," "Medications," "Assessment and Plan" as informal section headers even within free text). Where these markers are detectable, chunking should prefer to respect them rather than blindly splitting mid-section, since splitting a diagnosis away from its surrounding clinical context would degrade retrieval quality specifically for the kind of queries this system is meant to answer.

---

## 10. Embedding Strategy

### 10.1 Model Choice

VISTA uses a lightweight local sentence-transformer model, `all-MiniLM-L6-v2` (or an equivalent lightweight alternative), rather than a large hosted embedding API. This choice is driven by:

- **Cost** — no per-call API cost for embedding 50,000 documents' worth of chunks.
- **Latency** — local inference avoids network round-trips during both ingestion and query-time embedding.
- **Hardware fit** — a small model is a better match for the 24 GB RAM / 4 OCPU target runtime than a large embedding model would be.

The tradeoff is that a smaller model may capture somewhat less semantic nuance than a large state-of-the-art embedding model — this is an accuracy-for-efficiency tradeoff consistent with the rest of the system's design philosophy.

### 10.2 Embedding Consistency

The same embedding model must be used for both ingestion-time chunk embedding and query-time query embedding — mixing models would put queries and documents in different vector spaces, making similarity scores meaningless. This should be enforced as a versioned configuration value (see Appendix B) so that a future model upgrade is a deliberate, tracked migration rather than an accidental mismatch.

### 10.3 Re-embedding / Model Migration

If the embedding model is ever upgraded, the entire FAISS index must be rebuilt from the original chunks (stored via their parent documents in MinIO) — old and new embeddings cannot coexist in the same index. This is a known operational cost of changing the embedding model and should be planned as a full reindex, not an incremental update.

---

## 11. FAISS Indexing Deep Dive

### 11.1 Index Type Selection

A standard flat index (brute-force exact search) becomes memory-heavy and slow once the number of vectors climbs past roughly one million — a threshold that is well within reach once 50,000 documents are chunked into multiple vectors each. VISTA therefore uses **IVF-PQ** rather than a flat index.

### 11.2 Inverted File Index (IVF)

IVF partitions the vector space into Voronoi cells (clusters), each represented by a centroid learned during an index-training step. At query time, only the cells nearest to the query vector are searched, rather than the entire index. This is what makes IVF an *approximate* nearest-neighbor method — there's a small chance the true nearest neighbor sits in a cell that wasn't searched, traded off against a large reduction in search time.

Key IVF parameter: `nlist` (number of clusters/cells). A larger `nlist` means finer partitioning (faster individual cell search, but more cells to potentially probe); a smaller `nlist` means coarser partitioning. The number of cells actually probed per query is controlled by `nprobe` — increasing `nprobe` trades speed for recall.

### 11.3 Product Quantization (PQ)

PQ is a vector compression technique: each vector is split into sub-vectors, each sub-vector space is clustered independently, and each sub-vector is replaced with the ID of its nearest centroid. Instead of storing full-precision floating-point vectors, the index stores compact centroid ID codes. This reduces memory usage substantially and speeds up distance calculations (which can be done via lookup tables rather than full floating-point arithmetic), at the cost of some accuracy loss relative to exact search.

Key PQ parameters: number of sub-vectors (`m`) and bits per sub-vector code (`nbits`) — together these determine the compression ratio and the accuracy/memory tradeoff.

### 11.4 Combined IVF-PQ

VISTA combines both techniques (`IndexIVFPQ` in FAISS terms): IVF narrows the search to a handful of relevant clusters, and PQ compresses the vectors within those clusters so the whole structure fits comfortably inside the 24 GB RAM budget. This combination is what makes it feasible to hold a chunk-level index for a 50,000-document corpus in memory on a free-tier ARM instance.

### 11.5 Index Training

IVF-PQ indices require a training step (to learn the cluster centroids and the PQ codebooks) before vectors can be added. Training should be performed on a representative sample of the corpus's embedding distribution — training on too small or unrepresentative a sample risks poorly-placed centroids, which would degrade retrieval quality across the board.

### 11.6 Metadata Mapping

FAISS itself stores only vectors and integer IDs — it has no native concept of documents, patients, or specialties. VISTA maintains a mapping from FAISS-internal vector IDs to `(document_id, chunk_id)` pairs, which is what allows a raw similarity score to be turned back into something the rest of the system (and the user) can act on.

---

## 12. PostgreSQL Schema Design

*(Representative schema — exact column types/constraints should be finalized during implementation.)*

### 12.1 `documents` table

| Column | Type | Notes |
|---|---|---|
| `document_id` | UUID (PK) | Primary key, shared across MinIO/FAISS references |
| `s3_uri` | TEXT | Pointer to raw file in MinIO |
| `patient_id` | TEXT | Sensitive — access-controlled |
| `specialty` | TEXT | Indexed for coarse filtering |
| `report_date` | DATE | Indexed for coarse filtering |
| `keywords` | TEXT[] | GIN-indexed for keyword filtering |
| `ingested_at` | TIMESTAMP | Audit / pipeline tracking |
| `content_hash` | TEXT | For idempotent re-ingestion checks |

### 12.2 `chunks` table (optional, if chunk metadata is tracked relationally in addition to FAISS)

| Column | Type | Notes |
|---|---|---|
| `chunk_id` | UUID (PK) | Matches FAISS vector ID mapping |
| `document_id` | UUID (FK → documents) | Parent reference |
| `chunk_index` | INTEGER | Ordinal position within document |
| `char_start` / `char_end` | INTEGER | Position within original text, for context reconstruction |

### 12.3 Indexing Strategy

- B-tree index on `specialty`, `report_date` for fast range/equality filtering.
- GIN index on `keywords` array for containment queries.
- Row-level security policies (see Section 18) scoped around `patient_id` visibility.

---

## 13. MinIO Object Storage Design

### 13.1 Bucket Layout

A single bucket (e.g., `vista-raw-reports`) with object keys derived from `document_id`, e.g.:

```
vista-raw-reports/
  └── {document_id}.txt
```

### 13.2 Access Pattern

MinIO is written to exactly once per document (at ingestion) and read from only when a retrieval request explicitly asks for full document context — the common query path (Section 8) does not touch MinIO at all, since chunk text can be served directly if stored, or reconstructed from character offsets against the parent document only when needed.

### 13.3 S3 Compatibility

Because MinIO exposes an S3-compatible API, the object storage backend can be swapped for actual AWS S3 (or another compatible provider) without changing application code beyond configuration — this is a deliberate portability decision.

---

## 14. API Design (FastAPI)

*(Representative endpoint list — reflects the pipelines described in Sections 7–8.)*

### 14.1 Ingestion Endpoints

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/ingest/document` | Upload a single raw report; triggers full Phase A pipeline |
| `POST` | `/ingest/batch` | Bulk ingestion entrypoint for the initial corpus load |
| `GET` | `/ingest/status/{document_id}` | Check ingestion pipeline status for a document |

### 14.2 Retrieval Endpoints

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/search` | Hybrid search — accepts free-text query + optional metadata filters |
| `GET` | `/documents/{document_id}` | Fetch full raw document (from MinIO) |
| `GET` | `/documents/{document_id}/metadata` | Fetch structured metadata (from PostgreSQL) |

### 14.3 Example Request/Response Shape

**Request** — `POST /search`
```json
{
  "query_text": "chest pain radiating to left arm",
  "filters": {
    "specialty": "cardiology",
    "date_from": "2025-01-01",
    "date_to": "2025-12-31"
  },
  "top_k": 10
}
```

**Response**
```json
{
  "results": [
    {
      "document_id": "…",
      "chunk_id": "…",
      "similarity_score": 0.87,
      "chunk_text": "…",
      "specialty": "cardiology",
      "report_date": "2025-03-14"
    }
  ],
  "candidate_set_size": 342,
  "query_latency_ms": 118
}
```

### 14.4 Validation

All request/response shapes are defined as Pydantic models, giving automatic validation (e.g., rejecting malformed date filters) and automatic OpenAPI/Swagger documentation generation, which is useful both for development and for demoing the API's contract.

---

## 15. Frontend / UI Design (Streamlit)

### 15.1 Core Views

- **Search view** — free-text query box, filter controls (specialty dropdown, date range picker, keyword input), results list with similarity scores.
- **Document detail view** — full raw report text, with the matched chunk highlighted in context.
- **Ingestion monitor view** *(optional/admin)* — shows pipeline status for recently ingested documents, useful during the initial bulk load.

### 15.2 Design Principles

- The UI never talks to PostgreSQL, FAISS, or MinIO directly — every interaction goes through the FastAPI layer, keeping a single, auditable entry point into the system.
- Results display both the semantic similarity score and the metadata that justified the coarse filter, so a user can sanity-check *why* a result was returned.

---

## 16. Hardware & Deployment Strategy

### 16.1 Persistent Runtime

- **Provider:** Oracle Cloud "Always Free" tier
- **Instance type:** ARM Ampere A1
- **Resources:** 24 GB RAM, 4 OCPUs
- **Role:** Hosts the always-on FastAPI service, PostgreSQL instance, MinIO instance, and the in-memory FAISS index for query-time inference.

### 16.2 Batch Ingestion Compute

The initial bulk vectorization of the 50 GB corpus is a heavy, one-time (or infrequent) computational task — better suited to a temporary, more powerful machine than to the always-on free-tier instance. VISTA's strategy is to:

1. Provision on-demand cloud GPU compute for the batch embedding pass.
2. Run chunking + embedding for the full corpus on that temporary instance.
3. Build (or update) the FAISS IVF-PQ index there.
4. Transfer the resulting index file to the persistent Oracle ARM instance for lightweight, CPU-only inference at query time.

This split — expensive compute for building, cheap compute for serving — is a common and cost-effective pattern for vector search systems, and is specifically what makes a 24 GB free-tier instance viable for a 50 GB source corpus (the *raw* corpus size is not the same as the *index* size after chunking, embedding, and PQ compression).

### 16.3 Why This Split Matters

Without this split, either (a) the always-on instance would need to be provisioned at GPU-instance cost permanently, defeating the free-tier goal, or (b) ingestion would be so slow on CPU-only hardware that the initial 50,000-document load would become impractical.

---

## 17. Memory Optimization Deep Dive

### 17.1 The Core Constraint

24 GB RAM must hold, simultaneously: the OS and running services (Postgres, MinIO, FastAPI), the PostgreSQL metadata (comparatively small), and the FAISS index (comparatively large, and the dominant memory consumer at this document count).

### 17.2 Why Flat Index Doesn't Fit

A flat (exact) FAISS index stores full-precision vectors for every chunk. At tens of thousands of documents, each split into multiple chunks, the total vector count can run into the hundreds of thousands to low millions — at which point both memory footprint and per-query search time make a flat index impractical on a 24 GB instance shared with other services.

### 17.3 How IVF-PQ Solves This

As described in Section 11, IVF narrows the *search scope* per query (fewer vectors compared per query), while PQ narrows the *storage footprint* per vector (compact centroid codes instead of full floats). Together they address both the speed problem and the memory problem simultaneously — which is why they're used in combination rather than either alone.

### 17.4 Tuning Tradeoffs

| Parameter | Increasing it… | Decreasing it… |
|---|---|---|
| `nlist` (IVF clusters) | Finer partitioning, more index structure overhead | Coarser partitioning, less overhead but bigger cells to search |
| `nprobe` (cells searched per query) | Higher recall, slower queries | Faster queries, risk of missing true nearest neighbors |
| `m` (PQ sub-vectors) | Better accuracy, more memory | Less memory, more accuracy loss |
| `nbits` (bits per PQ code) | Better accuracy, more memory | Less memory, more accuracy loss |

These parameters should be tuned empirically against the actual corpus (see Section 20) rather than fixed a priori — the "right" values depend on the real embedding distribution of medical report text.

---

## 18. Security & Data Privacy

### 18.1 Core Principle: Layer Separation as a Privacy Control

VISTA's privacy story rests on strict decoupling of the data layers:

- **No PII in the vector space.** FAISS stores only mathematical chunk representations — no patient names, IDs, or identifying headers ever enter the vector index. Even if the FAISS index were somehow exfiltrated, it would not directly expose identifying information.
- **Isolated metadata.** PostgreSQL is the sole system holding sensitive structured fields such as Patient ID. This concentrates the access-control problem into one well-understood system rather than spreading sensitive data across three different storage technologies with three different security models.

### 18.2 Role-Based Access Control (RBAC)

*(Planned; not yet fully implemented — see Section 25.)*

Access to sensitive PostgreSQL columns (notably `patient_id`) should be governed by defined roles, for example:

- **Clinician role** — full access to patient identifiers for records within their care scope.
- **Researcher / analyst role** — access to de-identified/aggregated fields only (specialty, date, keywords), no access to `patient_id`.
- **Admin role** — operational access (ingestion pipeline monitoring, index management) without necessarily needing clinical data access.

Implementation approach: PostgreSQL row-level security (RLS) policies combined with role checks enforced at the FastAPI layer (i.e., defense in depth — both the API and the database enforce the boundary, rather than relying on the API alone).

### 18.3 Data Masking

*(Planned; not yet fully implemented — see Section 25.)*

For roles without full access, sensitive fields should be masked rather than simply omitted where possible — e.g., returning a partially redacted patient identifier rather than either the full value or a hard error, depending on the use case.

### 18.4 Transport & At-Rest Security

- All API traffic should be served over TLS.
- MinIO and PostgreSQL should be configured with encryption at rest where the deployment environment supports it.
- Credentials for MinIO/PostgreSQL should be managed via environment variables or a secrets manager, never hardcoded.

### 18.5 Compliance Posture

VISTA is designed with privacy-conscious architecture principles (data minimization in the vector layer, centralized access control for sensitive fields), but it has **not** undergone formal HIPAA or equivalent compliance certification. This distinction should be stated explicitly in any presentation of the project — "designed with privacy principles in mind" is not the same claim as "compliant."

---

## 19. Error Handling & Fault Tolerance

### 19.1 Ingestion Failure Modes

| Failure point | Handling strategy |
|---|---|
| MinIO upload fails | Abort pipeline before metadata extraction; no partial state created |
| Metadata extraction fails/produces low-confidence fields | Flag document for manual review; still commit best-effort metadata with a `needs_review` flag |
| Postgres commit fails | Treat document as not-ingested even though the raw file may exist in MinIO; retry or alert |
| Embedding/FAISS indexing fails | Document exists in Postgres/MinIO but is not searchable; flag as `indexing_incomplete` and retry separately, since re-running embedding does not require re-running earlier steps |

### 19.2 Query-Time Failure Modes

| Failure point | Handling strategy |
|---|---|
| PostgreSQL unavailable | Fail the request clearly rather than silently falling back to unfiltered FAISS search across the entire corpus |
| FAISS index unavailable/not loaded | Fail clearly; do not silently return stale or empty results without indicating degraded state |
| MinIO unavailable (full-document fetch) | Chunk-level results can still be returned; only the "view full document" action is degraded |

### 19.3 Consistency Model

Because the three storage layers are separate systems, VISTA does not have cross-system transactional guarantees out of the box. The design compensates with:
- A defined ingestion **order** (MinIO → metadata extraction → Postgres commit → embedding/indexing) so that partial failures have a predictable, recoverable state.
- Status flags (`needs_review`, `indexing_incomplete`) rather than silent failure, so partial ingestion states are visible and actionable rather than hidden.

---

## 20. Evaluation Methodology

To move VISTA from "designed architecture" to "validated system," the following evaluation approach is recommended.

### 20.1 Retrieval Quality

- Construct a labeled evaluation set: a sample of queries with known relevant documents/chunks (can be bootstrapped from MTSamples' existing specialty/category labels).
- Measure **Recall@k** and **Precision@k** for the hybrid pipeline.
- Measure the same metrics for FAISS's IVF-PQ index **against a flat (exact) index baseline** on a smaller subset, to quantify the accuracy cost of compression directly.

### 20.2 Latency

- Measure end-to-end query latency (p50, p95, p99) under the hybrid pipeline, broken down by:
  - Coarse SQL filter time
  - FAISS search time
  - Total round-trip time including network/serialization

### 20.3 Memory

- Measure actual peak RAM usage of the FAISS index at full 50,000-document scale, and compare against the 24 GB target to confirm the IVF-PQ parameters chosen in Section 17.4 actually hold in practice, not just in theory.

### 20.4 Ingestion Throughput

- Measure documents-per-second (or GB-per-hour) throughput through the full Phase A pipeline, both on the batch GPU ingestion compute and, separately, to confirm the persistent instance is not expected to bear that load.

### 20.5 Ablation Studies (Optional, Stretch Goal)

- Compare hybrid (filter + semantic) retrieval quality against semantic-only retrieval, to empirically justify the metadata-first design choice rather than asserting it.
- Compare different chunk sizes/overlap settings against retrieval quality, to justify the final chunking parameters chosen in Section 9.

---

## 21. Performance Benchmarks (Target vs Actual)

*(Actual figures to be filled in once benchmarking, per Section 20, has been run. Placeholder structure provided so results can be dropped in directly.)*

| Metric | Target | Actual |
|---|---|---|
| Query latency (p50) | < 200 ms | *TBD* |
| Query latency (p95) | < 800 ms | *TBD* |
| Recall@10 (IVF-PQ vs flat baseline) | > 90% of flat-index recall | *TBD* |
| Peak FAISS RAM usage @ 50k docs | < 18 GB (leaving headroom under 24 GB) | *TBD* |
| Ingestion throughput (batch GPU pass) | *TBD target* | *TBD* |
| Coarse SQL filter time | < 50 ms | *TBD* |

---

## 22. Scalability Considerations

### 22.1 Beyond 50,000 Documents

If the corpus grows significantly beyond the current target:
- `nlist` (IVF cluster count) should scale with corpus size to keep per-cell candidate counts reasonable.
- The index may eventually need to be sharded across multiple instances rather than held entirely on a single 24 GB machine — the current single-instance design has a natural ceiling.

### 22.2 Multi-Tenancy (Future Extension)

The current design assumes a single logical corpus. Supporting multiple isolated tenants (e.g., multiple hospitals with data that must not cross-contaminate in search results) would require tenant-scoped filtering to be enforced at the PostgreSQL coarse-filter stage *and* at the FAISS layer (e.g., separate indices per tenant, or a mandatory tenant-ID filter applied before any similarity search) — this is explicitly out of scope for the current phase (see Section 3.2) but is a natural extension point.

### 22.3 Streaming Ingestion (Future Extension)

Moving from batch to near-real-time ingestion would require the FAISS index to support incremental additions efficiently, and would shift the batch-GPU-then-transfer deployment pattern (Section 16.2) toward a more continuously-running ingestion service — a meaningfully different operational model than the current one.

---

## 23. Testing Strategy

### 23.1 Unit Tests

- Metadata extraction correctness (SpaCy/Regex field extraction against known sample inputs).
- Chunking boundary correctness (no dropped text, no duplicated overlap errors).
- API request/response schema validation (Pydantic models).

### 23.2 Integration Tests

- Full ingestion pipeline, end-to-end, against a small test corpus (MinIO write → metadata extraction → Postgres commit → embedding → FAISS index update).
- Full retrieval pipeline, end-to-end, verifying that a known query returns the expected known document among top results.

### 23.3 Load/Stress Tests

- Concurrent ingestion requests, to validate the async FastAPI handlers behave correctly under load.
- Concurrent search requests, to validate FAISS query performance under realistic concurrent access patterns rather than single-query benchmarks only.

### 23.4 Regression Tests

- Re-run the Section 20 evaluation suite whenever the embedding model, chunking strategy, or FAISS parameters change, to catch quality regressions before they ship.

---

## 24. Development Roadmap

### Phase 1 — Foundation *(current)*
- [x] Architecture design finalized
- [x] Technology stack selected and justified
- [ ] PostgreSQL schema implemented
- [ ] MinIO bucket structure implemented
- [ ] Basic FastAPI ingestion endpoint (single-document)

### Phase 2 — Core Pipelines
- [ ] Metadata extraction script (SpaCy/Regex)
- [ ] Chunking implementation
- [ ] Embedding pipeline (`all-MiniLM-L6-v2`)
- [ ] FAISS IVF-PQ index construction and training

### Phase 3 — Retrieval & UI
- [ ] Hybrid search endpoint (coarse filter + FAISS)
- [ ] Streamlit search UI
- [ ] Document detail view

### Phase 4 — Scale-Up
- [ ] Batch GPU ingestion pipeline for full 50 GB corpus
- [ ] Index transfer to persistent Oracle ARM instance
- [ ] Full corpus ingested and indexed

### Phase 5 — Hardening
- [ ] RBAC implementation in PostgreSQL/FastAPI
- [ ] Data masking implementation
- [ ] Error handling / fault tolerance per Section 19

### Phase 6 — Evaluation
- [ ] Evaluation set construction
- [ ] Benchmarks run per Section 20/21
- [ ] Ablation studies (chunking, hybrid vs semantic-only)

---

## 25. Known Limitations

- RBAC and data masking are currently **designed but not implemented** — see Section 18.2–18.3.
- No formal compliance certification (HIPAA or equivalent) has been pursued.
- The system assumes a single-tenant deployment; multi-tenant isolation is not yet supported (Section 22.2).
- Ingestion is batch-oriented; there is no current support for real-time/streaming document ingestion (Section 22.3).
- IVF-PQ introduces approximate (not exact) search results — some accuracy loss relative to a flat index is an inherent, accepted tradeoff (Section 11.3).
- Exact dataset-scaling methodology (how MTSamples was augmented from its native size to 50,000 entries) needs to be explicitly documented for reproducibility and to withstand technical scrutiny.
- Benchmarked performance numbers (Section 21) are not yet populated — claims about latency/memory/accuracy are currently targets, not measured results.

---

## 26. Risk Register

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| FAISS index doesn't fit in 24 GB at full scale | Medium | High | Tune IVF-PQ parameters early against real corpus size; test incrementally rather than only at full 50k scale |
| PQ compression degrades retrieval quality unacceptably | Medium | Medium | Benchmark against flat-index baseline (Section 20.1) before committing to final parameters |
| Metadata extraction (SpaCy/Regex) misses or mis-extracts fields | Medium | Medium | `needs_review` flagging (Section 19.1); manual spot-checking during initial ingestion |
| RBAC/masking not implemented before any demo involving real-looking PII | Low (synthetic data) / High (real data) | High | Restrict to synthetic/de-identified data until Section 18.2–18.3 are implemented |
| Batch GPU ingestion cost exceeds expectations | Low | Medium | Use on-demand (not reserved) GPU compute, scoped tightly to the ingestion window |
| Single-instance deployment becomes a bottleneck if corpus grows | Low (at current 50k scale) | Medium | Documented scaling path in Section 22.1 |

---

## 27. Glossary

- **ANN (Approximate Nearest Neighbor):** A class of search algorithms that trade a small amount of accuracy for large gains in speed, compared to exact nearest-neighbor search.
- **Chunk:** A sub-segment of a document's text, small enough to be meaningfully embedded as a single vector.
- **Coarse filtering:** Narrowing a candidate set using cheap, structured criteria (e.g., SQL `WHERE`) before applying expensive semantic search.
- **Embedding:** A dense numerical vector representation of text, positioned in a vector space such that semantically similar texts have similar vectors.
- **FAISS:** Facebook AI Similarity Search — an open-source library for efficient vector similarity search.
- **IVF (Inverted File Index):** A FAISS indexing technique that partitions vectors into clusters to reduce the search space per query.
- **PQ (Product Quantization):** A vector compression technique that reduces memory footprint by replacing sub-vectors with centroid IDs.
- **PII (Personally Identifiable Information):** Data that could identify a specific individual (e.g., Patient ID, name).
- **RBAC (Role-Based Access Control):** An access control model where permissions are assigned to roles rather than individuals directly.
- **Recall@k:** The fraction of relevant results found within the top-k returned results.

---

## 28. Appendix A: Sample Queries

**Example 1 — Hybrid query**
> Free text: "shortness of breath and fatigue"
> Filters: specialty = "cardiology", date range = last 12 months

**Example 2 — Filter-only query**
> Filters: specialty = "oncology", keywords contains "chemotherapy"
> (no free-text component)

**Example 3 — Semantic-only query**
> Free text: "unexplained weight loss and night sweats"
> (no filters — searches full corpus)

---

## 29. Appendix B: Configuration Reference

*(Representative — exact values to be finalized during implementation and tuning.)*

```yaml
embedding:
  model_name: "all-MiniLM-L6-v2"
  model_version: "v1"

chunking:
  strategy: "section-aware-with-fallback"
  target_chunk_tokens: 256
  overlap_tokens: 32

faiss:
  index_type: "IVF-PQ"
  nlist: 1024        # tune against corpus size, Section 17.4
  nprobe: 16          # tune against latency/recall tradeoff
  pq_m: 16            # number of PQ sub-vectors
  pq_nbits: 8         # bits per PQ code

storage:
  minio_bucket: "vista-raw-reports"
  postgres_schema: "vista"

deployment:
  persistent_runtime: "oracle-arm-a1"
  persistent_ram_gb: 24
  persistent_ocpus: 4
  batch_ingestion_compute: "on-demand-gpu"
```

---

## 30. References

- FAISS: Johnson, J., Douze, M., & Jégou, H. — *Billion-scale similarity search with GPUs* (Facebook AI Research).
- MTSamples dataset — publicly available medical transcription sample dataset (source corpus for augmentation).
- FastAPI documentation — https://fastapi.tiangolo.com
- Sentence-Transformers (`all-MiniLM-L6-v2`) — https://www.sbert.net
- MinIO documentation — https://min.io/docs
- PostgreSQL documentation — https://www.postgresql.org/docs

---

*End of document.*
