# VISTA
### Vector Intelligent Semantic Search & Text Analysis

**A Metadata-First, Box-Clustered Semantic Search Engine for Unstructured Medical Records**

**Lead Developer:** Ansh Gaur
**Contact:** anshgaurx@gmail.com · ansh1291g@gmail.com
**GitHub:** [@anshgaurx](https://github.com/anshgaurx) · [@anshxgaur](https://github.com/anshxgaur) · [@Ansh17gaur1](https://github.com/Ansh17gaur1)
**Document Version:** 3.0 (corrected — box-clustering architecture)
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
8. [Box-Clustering Layer (Phase B)](#8-box-clustering-layer-phase-b)
9. [Retrieval Pipeline (Phase C)](#9-retrieval-pipeline-phase-c)
10. [Chunking & Embedding Strategy](#10-chunking--embedding-strategy)
11. [Cosine Similarity & K-Means Deep Dive](#11-cosine-similarity--k-means-deep-dive)
12. [FAISS Box-Index Design](#12-faiss-box-index-design)
13. [Priority Scoring Layer](#13-priority-scoring-layer)
14. [Neon (PostgreSQL) Schema Design](#14-neon-postgresql-schema-design)
15. [DuckDB Metadata Analytics Design](#15-duckdb-metadata-analytics-design)
16. [MinIO Object Storage Design](#16-minio-object-storage-design)
17. [API Design](#17-api-design)
18. [Frontend / UI Design](#18-frontend--ui-design)
19. [Hardware & Deployment Strategy](#19-hardware--deployment-strategy)
20. [Memory & Compute Optimization](#20-memory--compute-optimization)
21. [Security & Data Privacy](#21-security--data-privacy)
22. [Error Handling & Fault Tolerance](#22-error-handling--fault-tolerance)
23. [Evaluation Methodology](#23-evaluation-methodology)
24. [Performance Benchmarks (Target vs Actual)](#24-performance-benchmarks-target-vs-actual)
25. [Team Ownership Map](#25-team-ownership-map)
26. [Development Roadmap](#26-development-roadmap)
27. [Known Limitations](#27-known-limitations)
28. [Risk Register](#28-risk-register)
29. [Glossary](#29-glossary)
30. [Appendix: Configuration Reference](#30-appendix-configuration-reference)
31. [References](#31-references)

---

## 1. Executive Summary

VISTA (Vector Intelligent Semantic Search & Text Analysis) is a semantic data warehouse that ingests, organizes, and retrieves unstructured medical reports by **meaning**, not keywords. The target corpus is **50,000+ documents** derived from an augmented MTSamples transcription dataset.

**This version of the document corrects the previous design.** Earlier drafts described a "flat FAISS index over every chunk" approach. The team's actual, agreed architecture is a **box-clustering** approach instead: rather than embedding and indexing every single document individually, documents are grouped into semantic **boxes** (clusters), a short summary is generated and embedded for each box, and only those box-level summary embeddings are indexed in FAISS. A query matches to the nearest box first, and a **priority score** (freshness + call frequency + importance) then selects the best file inside that box. This is dramatically cheaper computationally than per-document embedding at scale, while still being tested against a per-document baseline to confirm retrieval quality holds up (Section 23).

The system separates concerns into four layers:

- **Object storage** (MinIO) — raw file persistence.
- **Relational warehouse** (Neon / PostgreSQL) — structured, filterable metadata, linked by a stable `document_id`.
- **Analytics layer** (DuckDB) — fast local analytics over metadata to compute freshness/frequency signals.
- **Vector layer** (FAISS) — indexes only box-summary embeddings, not every document.

This document describes the corrected end-to-end design: architecture, data model, pipelines, clustering methodology, indexing strategy, hardware plan, security model, evaluation methodology, team ownership, and roadmap.

---

## 2. Problem Statement & Motivation

Medical reports are stored as unstructured free text across fragmented hospital systems. Traditional retrieval falls into two unsatisfying categories:

1. **Pure keyword search** — fast and cheap, but blind to meaning. A search for "heart attack" won't reliably surface "myocardial infarction."
2. **Pure per-document semantic search** — captures meaning well, but embedding and indexing every individual document (and every chunk of every document) becomes computationally expensive at scale, especially under constrained hardware.

VISTA's core research question is: **can grouping documents into semantic boxes first, and only embedding a summary per box, match the retrieval quality of full per-document semantic search — at a fraction of the compute cost?** This is the central hypothesis the project (and the paper built alongside it) is testing.

A secondary motivation is **data governance**. Medical data is sensitive. Keeping raw PII out of the vector space entirely, and concentrated instead inside a relational warehouse with well-understood access controls, keeps the privacy story auditable.

---

## 3. Goals & Non-Goals

### 3.1 Goals

- Ingest and organize a 50,000+ document corpus of medical reports.
- Cluster documents into semantic "boxes" instead of embedding every document individually.
- Support hybrid queries: natural-language query → nearest box → priority-ranked file within that box.
- Operate within a modest RAM/compute budget by keeping the FAISS index small (box-level, not document-level).
- Keep raw PII out of the vector index entirely.
- Empirically compare box-clustering retrieval quality against a per-document baseline.

### 3.2 Non-Goals (current phase)

- Not a general-purpose document management system — scoped to medical report retrieval.
- Not real-time streaming ingestion — ingestion is a batch process.
- No full clinical NLP pipeline (no ICD-10 coding, no ontology entity linking).
- No multi-tenant isolation yet.
- Not HIPAA-certified or formally audited — architecture is privacy-conscious, not compliance-certified.

---

## 4. System Architecture Overview

```
Raw Medical Reports (PDFs, images, text)
        │
        ▼
ETL Pipeline — clean, deduplicate, remove errors      (Aashita)
        │
        ▼
OCR Processing (PaddleOCR, for image-based reports)    (Aditi)
        │
        ├──────────────────────────────┐
        ▼                              ▼
Raw File Storage (MinIO)     Structured Warehouse (Neon/PostgreSQL)     (Ankit)
        │                              │
        │                              ▼
        │                     Metadata Analytics (DuckDB)               (Anant)
        │                              │
        │                              ▼
        │                     Priority Scoring Layer
        │                     priority = freshness + call_frequency + importance
        ▼
Document Embeddings (Sentence Transformer, all-MiniLM-L6-v2)            (Arpit)
        │
        ▼
Cosine Similarity Computation (pairwise document similarity)            (Arpit)
        │
        ▼
K-Means Clustering — groups documents into semantic "boxes"             (Ansh, Ankit)
        │
        ▼
Box Summary Generation + Box Summary Embedding                          (Ansh, Ankit, Arpit)
        │
        ▼
FAISS Index — indexes box summary embeddings ONLY                       (Ansh, Ankit)
        │
        ▼
User NLP Query ──► matched to nearest box ──► File Selection Within
Matched Box (using Priority Score) ──► Ranked Result Returned to User
```

Each layer has one job:

| Layer | Responsibility | Does NOT do |
|---|---|---|
| ETL | Clean, dedupe, error-strip raw files | Storage, embedding |
| OCR | Convert scanned/image text to machine-readable text | Storage, clustering |
| MinIO | Raw file persistence | Search, filtering |
| Neon/PostgreSQL | Structured metadata, source of truth for document existence | Vectors, raw file bytes |
| DuckDB | Fast analytics over metadata (freshness, frequency) | Long-term storage of raw data |
| Arpit's embedding layer | Turns text into vectors, computes similarity math | Clustering decisions, storage |
| K-Means / Box layer | Groups documents into boxes, generates+embeds box summaries | Per-document embedding storage |
| FAISS | Similarity search over box embeddings only | Metadata storage, raw text storage |
| Priority layer | Ranks files inside a matched box | Box matching itself |

---

## 5. Core Technology Stack

| Component | Technology | Purpose | Owner |
|---|---|---|---|
| ETL | Python | Cleaning, deduplication, error removal | Aashita |
| OCR | PaddleOCR | Text extraction from scanned/image reports | Aditi |
| Object Store | MinIO | Raw file persistence, S3-compatible | Ankit |
| Metadata Warehouse | Neon (PostgreSQL) | Structured, filterable metadata | Ankit |
| Metadata Analytics | DuckDB | Freshness/frequency analytics, feeds priority score | Anant |
| Embedding Model | Sentence Transformers (`all-MiniLM-L6-v2`) | Converts text into 384-D vectors | Arpit |
| Similarity Math | Cosine similarity | Pairwise document similarity for clustering | Arpit |
| Clustering | K-Means | Groups documents into semantic boxes | Ansh, Ankit |
| Vector Search | FAISS | Indexes box summary embeddings for fast retrieval | Ansh, Ankit |
| Backend API | FastAPI | Orchestrates ingestion and search endpoints | Team |
| Frontend UI | Streamlit | Interactive search/dashboard | Team |
| Deployment | Docker | Containerized services | Team |

### 5.1 Why box-clustering instead of a flat/IVF-PQ per-document index

The original design considered indexing every chunk of every document directly in FAISS (using IVF-PQ compression to fit memory constraints). The team's revised approach avoids this cost altogether at the source: instead of compressing a huge number of document-level vectors, it **reduces the number of vectors that need to be indexed in the first place** by summarizing clusters of similar documents into one searchable unit per cluster. This is a different lever on the same problem — fewer, richer vectors instead of many, compressed vectors — and is the core distinction this project is testing empirically (Section 23).

### 5.2 Why Neon instead of self-hosted PostgreSQL

Neon is a managed, serverless PostgreSQL provider — it gives the team a standard PostgreSQL interface (same schema design, same SQL, same row-level security features) without needing to operate the database server itself, which suits a small student team without dedicated DB-ops time.

### 5.3 Why DuckDB alongside Neon

DuckDB is an embedded, in-process analytical database optimized for fast columnar aggregation — well suited to the kind of "how often was this accessed, how old is it" analytical queries the priority scoring layer needs, without adding load to the transactional Neon warehouse.

### 5.4 Why MinIO

S3-compatible, self-hostable object storage — raw report files are stored here and referenced everywhere else by `document_id`, so the storage backend can later be swapped to real AWS S3 with minimal code change.

### 5.5 Why FAISS

FAISS (Facebook AI Similarity Search) supports both exact and approximate similarity search. Because VISTA now indexes only box-level summary embeddings (a small number of vectors — one per box, not one per document), a simple flat FAISS index is sufficient; the IVF-PQ compression discussed in earlier drafts is not required at this scale, though it remains an option if the number of boxes grows very large.

---

## 6. Data Model

### 6.1 Conceptual Entities

- **Document** — a single raw medical report, unique `document_id`.
- **Metadata Record** — structured row per document (specialty, date, keywords, priority signals).
- **Document Embedding** — a vector representation of a document's cleaned text (used as clustering input, not directly searched).
- **Box** — a cluster of similar documents, produced by K-Means.
- **Box Summary** — a short, generated text summary representing a box's contents.
- **Box Embedding** — the vector representation of a box summary; this is what FAISS actually indexes.

### 6.2 Entity Relationship Summary

```
Document (many) ──► belongs to ──► (1) Box
Document (1) ──────── (1) Metadata Record
Box (1) ──────────── (1) Box Summary ──────── (1) Box Embedding
```

- Many documents belong to one box.
- Every document keeps its `document_id` and its `box_id`, so a box match can always be traced back to the specific candidate documents inside it.
- Only Box Embeddings are stored in FAISS — individual Document Embeddings are intermediate artifacts used to compute clustering, not permanently indexed for search.

### 6.3 Identifiers

- `document_id` — UUID, primary key across MinIO, Neon, and box membership.
- `box_id` — identifier for a K-Means cluster, primary key for the FAISS box index.

---

## 7. Ingestion Pipeline (Phase A)

```
Raw file
   │
   ▼
[1] ETL — clean, deduplicate, remove errors                  (Aashita)
   │
   ▼
[2] OCR — PaddleOCR text extraction for image-based reports  (Aditi)
   │
   ▼
[3] MinIO storage (raw file) + Neon commit (metadata row)    (Ankit)
   │
   ▼
[4] DuckDB analytics pass (freshness/frequency signals)      (Anant)
```

**Step 1 — ETL.** Aashita's pipeline ingests raw files in mixed formats, runs duplicate detection (content-hash based) and strips malformed/corrupt files, producing a clean file batch.

**Step 2 — OCR.** Aditi's pipeline splits cleaned files into text-native files (pass-through) and image-based/scanned files (routed through PaddleOCR), producing normalized machine-readable text for every document regardless of original format.

**Step 3 — Storage.** Ankit's pipeline writes the raw file to MinIO and a metadata row (linked by `document_id`) to Neon. This row is the source of truth for whether a document exists in the system.

**Step 4 — Analytics.** Anant's DuckDB layer reads from the Neon warehouse to compute freshness and (initially simulated, later real) access-frequency signals, feeding the priority scoring layer (Section 13).

### 7.1 Idempotency

Re-running ingestion on the same file should not create duplicates — Aashita's ETL stage computes a content hash and checks for an existing row before proceeding.

---

## 8. Box-Clustering Layer (Phase B)

This is the layer that distinguishes VISTA's current design from a conventional per-document semantic search system.

```
Cleaned document text
   │
   ▼
[1] Document Embeddings — Sentence Transformer (all-MiniLM-L6-v2)   (Arpit)
   │
   ▼
[2] Cosine Similarity Matrix — pairwise document similarity          (Arpit)
   │
   ▼
[3] K-Means Clustering — groups documents into boxes                 (Ansh, Ankit)
   │
   ▼
[4] Box Summary Generation — short summary per cluster                (Ansh, Ankit)
   │
   ▼
[5] Box Summary Embedding — Sentence Transformer on the summary text  (Arpit)
   │
   ▼
[6] FAISS Index — box summary embeddings only                         (Ansh, Ankit)
```

**Step 1–2 — Embeddings & similarity math (Arpit).** Every cleaned document is embedded, and cosine similarity is computed between document vectors. Vectors are unit-normalized before this step so the similarity math is correct (an easy thing to get subtly wrong).

**Step 3 — Clustering (Ansh, Ankit).** K-Means groups the similarity matrix into a chosen number of clusters (`k`), each becoming a "box" — e.g., a box that turns out to contain mostly blood-test reports.

**Step 4 — Summarization (Ansh, Ankit).** A short text summary is generated for each box, describing its dominant content (e.g., "Blood test and lab result reports").

**Step 5 — Box embedding (Arpit).** The box summary text is embedded using the same model used for documents, so query embeddings, document embeddings, and box embeddings all live in the same vector space.

**Step 6 — Indexing (Ansh, Ankit).** Only the box summary embeddings go into FAISS — this is what keeps the searchable index small regardless of how large the underlying document corpus grows.

### 8.1 Open design question — full corpus vs. sample-based embedding

Whether Arpit computes document embeddings for **every** document (to feed clustering) or only for a **representative sample**, with the remainder assigned to clusters afterward via a cheaper nearest-centroid comparison, is a decision that materially affects both compute cost and the "avoided full-corpus embedding" claim in the paper. This should be decided explicitly and documented before final benchmarking (see Section 23).

---

## 9. Retrieval Pipeline (Phase C)

```
User NLP Query
   │
   ▼
[1] Query Embedding (same Sentence Transformer model)
   │
   ▼
[2] FAISS search over Box Embeddings ──► nearest box match
   │
   ▼
[3] File Selection Within Matched Box, ranked by Priority Score
   │
   ▼
Ranked Result Returned to User
```

**Step 1.** The doctor's free-text query (e.g., "blood reports") is embedded with the same model used for documents and box summaries.

**Step 2.** FAISS compares the query embedding against box embeddings only — a search over a handful of boxes, not tens of thousands of documents — and returns the nearest matching box (e.g., the "Blood Reports" box).

**Step 3.** Within that box, candidate documents are ranked using the priority score (Section 13) — how often a file has been accessed, how recent it is, and its computed importance — and the top result(s) are returned.

### 9.1 Why box-first matters

Narrowing the search to box-level embeddings, instead of searching every document vector, is what gives VISTA its computational efficiency argument: query cost scales with the number of boxes, not the number of documents.

---

## 10. Chunking & Embedding Strategy

### 10.1 Chunking

Full medical reports are used as the unit of embedding for clustering purposes (rather than splitting into sub-document chunks), since the goal is document-to-box assignment, not sub-document passage retrieval. If a future iteration needs passage-level detail within a matched file, section-aware chunking (respecting informal headers like "History," "Medications," "Assessment") remains the recommended fallback strategy, with a modest overlap between chunks to avoid splitting meaning at boundaries.

### 10.2 Embedding Model

VISTA uses `all-MiniLM-L6-v2`, a lightweight local sentence-transformer, for documents, box summaries, and queries alike — chosen for zero per-call API cost, low latency (no network round-trip), and a good fit for modest hardware. The same model version must be used everywhere embeddings are compared, or similarity scores become meaningless; this should be a versioned config value (Section 30).

### 10.3 Re-embedding

If the embedding model is ever upgraded, all document embeddings, box summary embeddings, and the FAISS index must be rebuilt together — old and new embeddings cannot be mixed.

---

## 11. Cosine Similarity & K-Means Deep Dive

### 11.1 Cosine Similarity

Cosine similarity measures the angle between two vectors rather than raw distance, which avoids bias toward document length:

$$\cos(\theta) = \frac{A \cdot B}{\Vert A \Vert \Vert B \Vert}$$

| Score Range | Meaning |
|:---:|---|
| 1.0 | Near-identical clinical meaning |
| 0.8+ | Highly related medical context |
| 0.5 | Moderately related context |
| 0.0 | Completely unrelated records |
| -1.0 | Semantically opposite concepts |

Vectors must be unit-normalized before this calculation for the result to be correct — verified by spot-checking that two obviously-related reports score higher than two obviously-unrelated ones.

### 11.2 K-Means Clustering

K-Means partitions documents into `k` clusters by minimizing distance to learned cluster centroids. Choosing `k` is a key tuning decision: too few boxes produces overly broad, low-precision groupings (e.g., one giant "medical reports" box); too many boxes fragments genuinely related documents across multiple boxes and erodes the compute-savings argument. `k` should be chosen empirically and sanity-checked by hand — does the "blood reports" box actually look like blood reports when inspected manually?

### 11.3 Box Priority (separate from document priority)

Boxes themselves can carry a priority weight (e.g., a "blood reports" box might be flagged high-priority at 0.87) reflecting the clinical urgency or frequency of that category, distinct from the per-document priority score computed in Section 13 that ranks files *within* a box.

---

## 12. FAISS Box-Index Design

### 12.1 Index Type

Because the number of vectors indexed equals the number of boxes (typically small — tens to low hundreds, not tens of thousands), a simple flat FAISS index (exact search) is sufficient at current scale — no IVF-PQ compression is required. This should be revisited only if the number of boxes grows into the thousands.

### 12.2 Metadata Mapping

FAISS stores only vectors and integer IDs. VISTA maintains a mapping from FAISS vector ID → `box_id`, and separately, `box_id` → member `document_id`s (in Neon), so a box match can be resolved down to actual candidate files.

---

## 13. Priority Scoring Layer

Owned by Anant, this layer ranks files **within** a matched box.

```
priority_score = freshness + call_frequency + importance
```

- **Freshness** — based on report date; more recent reports score higher.
- **Call frequency** — how often a document has been accessed (currently simulated/pilot-phase access-log data; to be replaced with real usage data as the system is used).
- **Importance** — a weighting reflecting clinical significance of the document/category.

Weights (`w1`, `w2`, `w3`) applied to each component should be explicitly chosen and documented, not left as unexplained magic numbers — this is one of the required weekly check-in answers (Section 25).

---

## 14. Neon (PostgreSQL) Schema Design

### 14.1 `documents` table

| Column | Type | Notes |
|---|---|---|
| `document_id` | UUID (PK) | Shared across MinIO/box references |
| `s3_uri` | TEXT | Pointer to raw file in MinIO |
| `box_id` | UUID (FK) | Which box this document currently belongs to |
| `specialty` | TEXT | Indexed for filtering |
| `report_date` | DATE | Indexed, feeds freshness score |
| `keywords` | TEXT[] | GIN-indexed |
| `call_count` | INTEGER | Feeds call_frequency score |
| `priority_score` | FLOAT | Computed, cached for fast retrieval |
| `content_hash` | TEXT | Idempotent re-ingestion checks |
| `ingested_at` | TIMESTAMP | Audit/pipeline tracking |

### 14.2 `boxes` table

| Column | Type | Notes |
|---|---|---|
| `box_id` | UUID (PK) | Matches FAISS vector ID mapping |
| `summary_text` | TEXT | Generated box summary |
| `box_priority` | FLOAT | Category-level priority weight |
| `document_count` | INTEGER | Number of member documents |

### 14.3 Indexing Strategy

B-tree on `specialty`, `report_date`, `box_id`; GIN on `keywords`; row-level security scoped around any sensitive identifying fields.

---

## 15. DuckDB Metadata Analytics Design

DuckDB runs analytical queries directly against exported/synced metadata from Neon — aggregating call frequency over time windows, computing freshness distributions, and feeding the priority formula in Section 13. It is chosen specifically because it's fast for this kind of columnar aggregation without needing a separate analytics server.

---

## 16. MinIO Object Storage Design

### 16.1 Bucket Layout

```
vista-raw-reports/
  └── {document_id}.txt
```

### 16.2 Access Pattern

MinIO is written to once per document at ingestion, and read from only when a user explicitly requests the full raw file — the box-match + priority-rank query path does not need to touch MinIO at all.

---

## 17. API Design

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/ingest/document` | Upload a single raw report; triggers ETL → OCR → storage |
| `POST` | `/ingest/batch` | Bulk ingestion for initial corpus load |
| `POST` | `/cluster/rebuild` | Re-run embedding + K-Means + box summary generation |
| `POST` | `/search` | Query → nearest box → priority-ranked file(s) |
| `GET` | `/documents/{document_id}` | Fetch raw document from MinIO |
| `GET` | `/boxes/{box_id}` | Inspect a box's summary and member documents |

**Example — `POST /search`**
```json
{
  "query_text": "blood test results",
  "top_k": 5
}
```

**Response**
```json
{
  "matched_box": "blood_reports",
  "box_similarity_score": 0.91,
  "results": [
    {
      "document_id": "…",
      "priority_score": 0.87,
      "report_date": "2025-03-14",
      "specialty": "hematology"
    }
  ]
}
```

---

## 18. Frontend / UI Design

- **Search view** — free-text query box, results ranked by priority within the matched box.
- **Box explorer view** — browse all boxes, their summaries, and member document counts (useful for manually sanity-checking clustering quality).
- **Document detail view** — full raw report text.
- The UI never talks to Neon, DuckDB, MinIO, or FAISS directly — every interaction goes through the API layer.

---

## 19. Hardware & Deployment Strategy

- **Persistent runtime:** modest cloud instance running FastAPI, the FAISS box index (small — one vector per box), and connecting to Neon (managed) and MinIO.
- **Batch clustering compute:** the K-Means + embedding pass over the corpus is the heaviest one-time/periodic job and should be run as a batch process, similar in spirit to a scheduled reindex rather than continuous streaming.

---

## 20. Memory & Compute Optimization

Because FAISS now indexes box-level embeddings rather than document-level (or chunk-level) embeddings, the memory footprint of the vector index is dramatically smaller than a per-document design at the same corpus size — this is the primary lever VISTA uses to stay within modest hardware, replacing the earlier IVF-PQ compression strategy as the main cost-control mechanism (compression is still an available fallback if box count grows very large).

---

## 21. Security & Data Privacy

- **No PII in the vector space** — FAISS stores only box summary embeddings, never raw identifying document text.
- **Isolated metadata** — Neon is the sole system holding sensitive structured fields.
- **RBAC (planned)** — clinician / researcher / admin roles with different access to sensitive fields, enforced via Neon row-level security plus API-layer checks.
- **Compliance posture** — privacy-conscious architecture, not a certified-compliant system; this distinction should always be stated explicitly.

---

## 22. Error Handling & Fault Tolerance

| Failure point | Handling strategy |
|---|---|
| MinIO upload fails | Abort before metadata commit; no partial state |
| OCR fails on a file | Flag `needs_review`, continue pipeline for other files |
| Neon commit fails | Treat document as not-ingested even if raw file exists in MinIO |
| Clustering/embedding fails | Document exists but is unsearchable; flag `indexing_incomplete`, retry independently |
| FAISS index unavailable at query time | Fail clearly; never silently return stale/empty results |

---

## 23. Evaluation Methodology

This is the core of the research paper's Results section.

- **Retrieval quality:** compare box-clustering retrieval (query → box → priority-ranked file) against a per-document semantic search baseline, using Recall@k / Precision@k on a labeled query set built from MTSamples specialty labels.
- **Cluster quality:** cluster purity against ground-truth specialty labels; silhouette score; manual spot-checks of box contents.
- **Compute cost:** measure and directly compare embedding time, index size, and query latency for box-clustering vs. a full per-document baseline — this is the paper's central empirical claim.
- **Priority scoring validity:** sanity-check that priority-ranked results within a box match clinical intuition (recent, frequently-accessed, high-importance files surface first).

---

## 24. Performance Benchmarks (Target vs Actual)

| Metric | Target | Actual |
|---|---|---|
| Query latency (box match + rank) | < 500 ms | *TBD* |
| Recall@10 (box-clustering vs per-document baseline) | ≥ 90% of baseline recall | *TBD* |
| FAISS index size (box-level) | Orders of magnitude smaller than per-document index | *TBD* |
| Embedding compute time (full corpus, box approach vs baseline) | Meaningful reduction vs baseline | *TBD* |

---

## 25. Team Ownership Map

| Person | Primary Ownership |
|---|---|
| **Aashita** | ETL — cleaning, deduplication, error removal |
| **Aditi** | OCR — PaddleOCR text extraction for image-based reports |
| **Ankit** | MinIO + Neon warehouse; co-owns K-Means/box logic with Ansh |
| **Anant** | DuckDB metadata analytics; priority scoring formula and weights |
| **Arpit** | Document + box summary embeddings; cosine similarity math |
| **Ansh** | Clustering/box pipeline lead; box summaries; FAISS box index; query matching |

Weekly check-ins (per person) track: what was built, what broke, key decisions + alternatives rejected, measurable numbers, blockers, and next steps — logged in a shared tracker so the paper's Results section is built from real evidence.

---

## 26. Development Roadmap

### Phase 1 — Foundation
- [x] Architecture design finalized (box-clustering)
- [x] Technology stack selected and justified
- [ ] Neon schema implemented
- [ ] MinIO bucket structure implemented

### Phase 2 — Ingestion
- [ ] ETL pipeline (Aashita)
- [ ] OCR pipeline (Aditi)
- [ ] Storage integration (Ankit)

### Phase 3 — Clustering
- [ ] Document embeddings + cosine similarity (Arpit)
- [ ] K-Means box clustering (Ansh, Ankit)
- [ ] Box summary generation + embedding (Ansh, Ankit, Arpit)
- [ ] FAISS box index (Ansh, Ankit)

### Phase 4 — Analytics & Priority
- [ ] DuckDB analytics pipeline (Anant)
- [ ] Priority scoring formula + weights (Anant)

### Phase 5 — Retrieval & UI
- [ ] Search endpoint (query → box → priority rank)
- [ ] Streamlit UI

### Phase 6 — Evaluation & Paper
- [ ] Evaluation set construction
- [ ] Box-clustering vs per-document baseline benchmark
- [ ] First paper draft

---

## 27. Known Limitations

- RBAC and data masking are designed but not implemented.
- No formal compliance certification pursued.
- Single-tenant only; no multi-tenant isolation.
- Batch-oriented ingestion; no real-time streaming.
- Whether embeddings are computed for every document or a representative sample (Section 8.1) is not yet finalized and materially affects the compute-cost claim.
- Benchmarked numbers (Section 24) are targets, not yet measured results.

---

## 28. Risk Register

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Box-clustering retrieval quality falls meaningfully below per-document baseline | Medium | High | Benchmark early against baseline (Section 23); tune `k` |
| Poor `k` choice produces incoherent boxes | Medium | Medium | Manual spot-checks of box contents each week |
| Priority weights are arbitrary/unjustified | Medium | Medium | Require documented rationale in weekly check-ins |
| Full-corpus embedding cost undermines the compute-savings claim | Medium | High | Resolve the sample-vs-full-corpus question (8.1) explicitly and early |
| RBAC/masking missing before any demo with real-looking PII | Low (synthetic data) | High | Restrict to synthetic/de-identified data until implemented |

---

## 29. Glossary

- **Box:** A K-Means cluster of semantically similar documents, represented by one short summary and one embedding.
- **Box embedding:** The vector representation of a box's summary text — the only thing FAISS indexes.
- **Coarse filtering:** Narrowing a candidate set using cheap, structured criteria before applying expensive semantic search.
- **Cosine similarity:** A measure of the angle between two vectors, used for semantic similarity.
- **FAISS:** Facebook AI Similarity Search — library for efficient vector similarity search.
- **K-Means:** A clustering algorithm that partitions data into `k` groups around learned centroids.
- **Priority score:** `freshness + call_frequency + importance` — ranks files within a matched box.
- **PII:** Personally identifiable information.

---

## 30. Appendix: Configuration Reference

```yaml
embedding:
  model_name: "all-MiniLM-L6-v2"
  model_version: "v1"

clustering:
  algorithm: "k-means"
  k: null              # to be tuned empirically, Section 11.2

faiss:
  index_type: "flat"    # sufficient at box-level scale; revisit if box count grows large

priority:
  formula: "freshness + call_frequency + importance"
  weights:
    w1_freshness: null   # to be documented per Section 13
    w2_call_frequency: null
    w3_importance: null

storage:
  minio_bucket: "vista-raw-reports"
  neon_schema: "vista"
```

---

## 31. References

- FAISS: Johnson, J., Douze, M., & Jégou, H. — *Billion-scale similarity search with GPUs* (Facebook AI Research).
- MTSamples dataset — publicly available medical transcription sample dataset.
- Sentence-Transformers (`all-MiniLM-L6-v2`) — https://www.sbert.net
- PaddleOCR — https://github.com/PaddlePaddle/PaddleOCR
- MinIO documentation — https://min.io/docs
- Neon documentation — https://neon.tech/docs
- DuckDB documentation — https://duckdb.org/docs

---

*End of document.*
