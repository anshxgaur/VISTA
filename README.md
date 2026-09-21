<h1 align="center">VISTA: Vector Intelligent Semantic Search Text Analysis</h1>

<p align="center">
  A semantic healthcare data warehouse platform that organizes and retrieves medical reports based on <b>meaning</b>, not just keywords — powered by box-clustering, transformer embeddings, cosine similarity, and priority-based ranking.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Domain-AI%2FML%20%7C%20Big%20Data%20%7C%20Data%20Warehouse-3B5BDB" alt="Domain">
  <img src="https://img.shields.io/badge/Status-In%20Development-yellow" alt="Status">
  <img src="https://img.shields.io/badge/License-MIT-green" alt="License">
</p>

<p align="center">
  <a href="info/DOCUMENTATION.md">
    <img src="https://img.shields.io/badge/📖_FULL_DOCUMENTATION-View_Now-2962FF?style=for-the-badge&labelColor=1a1a1a" alt="View Full Documentation">
  </a>
</p>

---

## 📊 Project Statistics & Targets

<p align="center">

| 📄 Medical Reports | 🏥 Medical Departments | 🧠 Embedding Size | ⚡ Average Search | 🎯 Semantic Accuracy Target |
|:---:|:---:|:---:|:---:|:---:|
| **5,000+** | **40+** | **384-D** | **< 2 sec** | **95%** |

</p>

---

## 📌 Problem Statement

Hospitals generate millions of medical reports every year — discharge summaries, lab results, radiology notes, prescriptions, and clinical observations. Traditional hospital storage relies on fragmented folder structures and rigid keyword-based search, making it difficult to retrieve semantically related reports when terminology differs across departments (e.g. *"heart attack"* vs. *"myocardial infarction"*).

**The traditional hospital search bottleneck:**

```
Doctor ──> [ Keyword Query ] ──> Fails on synonyms, takes several minutes
             ├── Fragmented PDFs & Bills
             ├── Multi-departmental Notes
             └── Disconnected Legacy Storage
```

This leads to:
- 🔁 Duplicated documentation and fragmented patient files
- ⏱️ Delayed diagnosis and slower historical case reviews
- 📉 Inefficient clinical search causing operational drag
- 📈 Compounding administrative burden as clinical data lakes expand

Additionally, embedding **every single document** individually is computationally expensive at scale — VISTA's core research question is whether **grouping documents into semantic "boxes" first** can match the retrieval quality of full per-document embedding search, at a fraction of the compute cost.

---

## 💡 Proposed Solution

**VISTA** eliminates keyword barriers by understanding the underlying clinical meaning behind medical text — and instead of embedding every raw file, it clusters documents into semantic **boxes** (e.g. "blood reports," "radiology notes") and embeds only a short summary per box. A query first matches to the closest box, then a **priority score** (freshness + call frequency + importance) pinpoints the exact file within it.

**The VISTA accelerated workflow:**

```
Doctor ──> Natural Language Query ──> Query Embedding ──> FAISS Box Match ──> Priority-Ranked File (< 2s)
```

- **Context-aware** — recognizes clinical synonyms instantly
- **Self-organizing** — automatically clusters medical reports by underlying pathology into labeled boxes
- **Compute-efficient** — searches across box summary embeddings, not every individual document
- **Priority-aware** — surfaces the most relevant file within a box using freshness, access frequency, and importance

---

## 🏗️ System Architecture & Workflow

<p align="center">
  <img src="info/architecture.png" width="100%" alt="VISTA Box-Clustering Semantic Search Architecture">
</p>

**The end-to-end pipeline:**

1. **Raw Medical Reports** (PDFs, images, text) enter the system
2. **ETL Pipeline** — cleans files, deduplicates, removes errors
3. **OCR Processing** — PaddleOCR extracts text from image-based/scanned reports
4. **Storage** — raw files → **MinIO**; structured metadata → **Neon (PostgreSQL)** warehouse, linked by a stable `document_id`
5. **Metadata Analytics** — DuckDB analyzes freshness and call-frequency signals
6. **Document Embeddings** — Sentence Transformer (`all-MiniLM-L6-v2`) vectorizes cleaned text
7. **Cosine Similarity Computation** — pairwise document similarity, normalized and verified
8. **K-Means Clustering** — groups documents into semantic "boxes"
9. **Box Summary Generation + Embedding** — a short summary is generated per box and embedded
10. **FAISS Index** — indexes box summary embeddings only, not every document
11. **Priority Scoring Layer** — `priority_score = freshness + call_frequency + importance`
12. **User NLP Query** → embedded → matched to nearest box via FAISS → **File Selection Within Matched Box** using the priority score → **Ranked Result Returned to User**

---

## 🧮 How Cosine Similarity Works

Instead of raw coordinate distance — which biases toward document length — cosine similarity calculates the geometric angle (θ) between two high-dimensional text vectors:

$$\cos(\theta) = \frac{A \cdot B}{\Vert A \Vert \Vert B \Vert}$$

| Score Range | Meaning |
|:---:|---|
| **1.0** | Near-identical clinical meaning |
| **0.8+** | Highly related medical context |
| **0.5** | Moderately related context |
| **0.0** | Completely unrelated records |
| **-1.0** | Semantically opposite concepts |

---

## 🛠️ Phase-1 ETL, OCR & Storage Pipeline

### 1. Storage Layout in MinIO (`vista-lake`)
```bash
bash manage_vista.sh up          # start MinIO + create vista-lake bucket
```

Layered layout in `s3://vista-lake/`:
- `raw/` — original phase-one files, uploaded unchanged (18,826 objects)
- `clean/` — the full RESULT corpus: 10 clean parquets, `ocr_text/*.txt`, `_manifest.json`
- `summaries/` — per-source profiles + `phase1_summary.md` + `phase1_clean_summary.md`
- `reports/` — pipeline run reports

### 2. Running Phase-1 Ingestion & OCR
```bash
# 1. ETL: raw -> clean -> summaries -> MinIO
python project/code/run_phase1.py

# 2. PaddleOCR over the report PDFs (resumable; cached in RESULT/clean_data/ocr_text/)
cd project/code && python -m ocr_reports

# 3. Assemble the RESULT folder for phase 2
python project/code/build_result.py

# 4. Sync the finished RESULT corpus back into the MinIO clean layer
python project/code/sync_result_to_minio.py
```

### 3. RESULT Folder (Input for Embeddings & Clustering)
`RESULT/clean_data/` contains every cleaned source produced by the pipeline:
- `*.parquet` — one typed, deduplicated dataset per source
- `ocr_text/*.txt` — full PaddleOCR text per parsed report PDF/DOCX
- `_manifest.json` — per-source cleaning + OCR statistics
- `phase1_clean_summary.md` — human-readable roll-up

### 4. OCR Engine Details
`project/code/vista_ocr` uses **PaddleOCR (PP-OCRv5/v6 models)** for images and scanned PDFs; digital PDFs use the embedded text layer via PyMuPDF.

---

## ⚡ Embeddings, Clustering & Search Pipeline

### 1. Embeddings & Cosine Similarity Math
```bash
# Vectorize reports into 384-D dense vectors and compute similarity matrix:
python Backend/Embeddings/pipeline.py --sample-size 50
```

### 2. Verify Output Correctness
```bash
python tests/verify_output.py
```

### 3. Frontend Search Dashboard
```bash
streamlit run Frontend/Streamlit/app.py
```

---

## 📂 Repository Structure

```text
VISTA
├── Backend/
│   ├── Embeddings/           # Sentence Transformer + cosine similarity math
│   ├── Clustering/           # K-Means box logic, box summaries, FAISS index
│   ├── ETL/                  # Cleaning, deduplication, error removal
│   └── OCR/                  # Document parsing and extraction
├── project/code/
│   ├── vista_ocr/            # Integrated PaddleOCR extraction engine
│   ├── vista_pipeline/       # Layered ETL pipeline (ASTRA-style, MinIO-backed)
│   ├── run_phase1.py         # Phase-1 ETL orchestrator (ingest -> clean -> summarize)
│   ├── ocr_reports.py        # Resumable PaddleOCR runner for report PDFs
│   └── build_result.py       # Assembles RESULT/clean_data/
├── Database/
│   ├── MinIO/                # Raw file object storage
│   ├── Neon/                 # Structured metadata warehouse
│   └── DuckDB/               # Metadata analytics + priority scoring
├── Frontend/
│   └── Streamlit/            # UI components and diagnostic dashboard
├── info/
│   ├── architecture.png      # System architecture diagram
│   └── DOCUMENTATION.md      # Comprehensive technical documentation
├── docs/                     # Academic synopses, presentation slide decks, and reports
├── RESULT/clean_data/        # Clean corpus for embedding and vector search
└── tests/                    # Unit and integration test suites
```

---

## 🎯 Accuracy Targets & Evaluation Benchmarks

1. **Semantic Retrieval Accuracy Target: `95%`** (Top-3 Retrieval Accuracy).
2. **Specialty Separability Ratio Target: `> 2.0x` (Achieved: `4.63x`)**.
3. **Retrieval Latency Target: `< 2.0 seconds`**.

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
