<p align="center">
  <img src="timeline/schedule/hello.png" alt="VISTA" width="100%">
</p>

<h1 align="center">VISTA: Vector Intelligent Semantic Search Text Analysis</h1>

<p align="center">
  A semantic healthcare data warehouse platform that organizes and retrieves medical reports based on <b>meaning</b>, not just keywords — powered by transformer embeddings, cosine similarity, and an analytical vector framework.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Domain-AI%2FML%20%7C%20Big%20Data%20%7C%20Data%20Warehouse-3B5BDB" alt="Domain">
  <img src="https://img.shields.io/badge/Status-In%20Development-yellow" alt="Status">
  <img src="https://img.shields.io/badge/License-MIT-green" alt="License">
</p>

<p align="center">
  <a href="./DOCUMENTATION.md">
    <img src="https://img.shields.io/badge/📖_FULL_DOCUMENTATION-View_Now-2962FF?style=for-the-badge&labelColor=1a1a1a" alt="View Full Documentation">
  </a>
</p>

---

## 📊 Project Statistics

<p align="center">

| 📄 Medical Reports | 🏥 Medical Departments | 🧠 Embedding Size | ⚡ Average Search | 🎯 Semantic Accuracy |
|:---:|:---:|:---:|:---:|:---:|
| **5,000+** | **40+** | **768-D** | **< 2 sec** | **95%** |

</p>

> *Benchmarks above are targets/measured on the current dataset — update this table as you re-run evaluations at larger scale.*

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

---

## 💡 Proposed Solution

**VISTA** eliminates keyword barriers by understanding the underlying clinical meaning behind medical text. By deploying sentence-transformer models and a semantic data warehouse abstraction, VISTA translates unstructured medical records into high-dimensional vector space.

**The VISTA accelerated workflow:**

```
Doctor ──> Natural Language Query ──> Embedding Model ──> Vector Search ──> Top 5 Semantic Matches (< 2s)
```

- **Context-aware** — recognizes clinical synonyms instantly
- **Self-organizing** — automatically clusters medical reports by underlying pathology
- **Fast** — sub-2-second retrieval across large analytical data pipelines

---

## 🏗️ System Architecture & Workflow

<p align="center">
  <img src="architecture-diagram.svg" width="100%" alt="System Architecture">
</p>

**The 10-step data pipeline:**

1. **Medical Report Upload** — unstructured files (PDFs, images, raw text) enter the system
2. **OCR & Text Extraction** — normalizes scanned text and layouts
3. **Data Cleaning** — tokenizes and strips noise from medical records
4. **Embedding Generation** — Sentence Transformer converts notes into numerical vectors
5. **Cosine Similarity Matching** — measures the angular similarity between report vectors
6. **Semantic Clustering** — hierarchical clusters auto-categorize emerging medical themes
7. **Vector Database** — indexes and holds vector spaces for fast retrieval
8. **Metadata Storage** — relational engine maps clinical IDs, kept separate from vector stores
9. **Semantic Search API** — high-throughput backend handles incoming semantic queries
10. **Dashboard UI** — clean interface for clinicians to query and browse clustered trends

---

## 🧮 How Cosine Similarity Works

<p align="center">
  <img src="cosine-similarity-diagram.svg" width="90%" alt="Cosine Similarity Vector Space">
</p>

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

## ⚙️ Technology Stack

<p align="center">
  <img src="timeline/tech_stack.png" width="90%" alt="Tech Stack">
</p>

| Layer | Technology | Purpose |
|---|---|---|
| 🐍 **Programming** | Python | Core analytical engine & data processing |
| ⚡ **Backend API** | FastAPI | Async, high-performance API endpoint router |
| 🧠 **AI & Embedding** | Sentence Transformers | Translates tokens into high-dimensional space |
| 🗄️ **Vector Storage** | Qdrant | Dense vector indexing, storage, and similarity search |
| 📦 **Metadata DB** | PostgreSQL | Secure, relational storage for patient attributes |
| ☁️ **Object Store** | MinIO | Persistent unstructured report storage & backup |
| 📊 **Frontend UI** | Streamlit | Real-time diagnostic analytical dashboard |
| 🐳 **Deployment** | Docker | Containerized configuration and microservice scaling |

---

## 📂 Dataset & Project Structure

**Dataset highlights (MTSamples):**

- **5,000+** de-identified medical transcription reports
- **40+** distinct medical specialties (Cardiology, Neurology, Orthopedics, Radiology, Oncology, etc.)
- *Future scope:* transitioning to real-world ICU data via **MIMIC-III / MIMIC-IV** integration

<p align="center">
  <img src="timeline/folder_structure.png" width="90%" alt="Folder Structure">
</p>

```
VISTA
├── Backend/
│   ├── FastAPI/              # RESTful API routing core
│   ├── Data Ingestion/       # OCR engines and loaders
│   ├── Embeddings/           # Deep-learning vectorization steps
│   └── Similarity Engine/    # Clustering mathematics and query handlers
├── Database/
│   ├── PostgreSQL/           # Structured user & system metadata
│   └── Qdrant/               # Multi-dimensional vector space indexing
├── Frontend/
│   └── Streamlit/            # UI components and interactive graph renderers
├── Dataset/                  # Medical transcript source records
└── Timeline/                 # Graphics assets and development schedules
```

---

## 👥 Team Structure

```mermaid
flowchart TD
    A["👨‍💻 Ansh Gaur<br><b>Project Lead & Data Engineer</b>"]
    B["👩‍💻 Aashita Mishra<br><b>Data Ingestion Engineer</b>"]
    C["👩‍💻 Aditi Sharma<br><b>Data Processing Engineer</b>"]
    D["👨‍💻 Ankit Shukla<br><b>Database & Data Warehouse Engineer</b>"]
    E["👨‍💻 Arpit Umrao<br><b>Semantic Search & Vector AI Engineer</b>"]
    F["👨‍💼 Anant Dubey<br><b>Business Strategy & Product Engineer</b><br><i>(Tech + Business)</i>"]

    A --> B
    A --> C
    A --> D
    A --> E
    A --> F

    B --> G["Data Collection<br>Upload Pipeline<br>API Integration"]
    C --> H["OCR<br>Cleaning<br>Metadata Extraction"]
    D --> I["DuckDB<br>PostgreSQL<br>MinIO"]
    E --> J["Embeddings<br>Cosine Similarity<br>Semantic Search<br>FAISS"]
    F --> K["Business Strategy<br>ROI Analysis<br>Product Growth<br>Testing & Demo"]
```
<p align="center">
  <img src="timeline/schedule/ChatGPT Image Jul 20, 2026, 02_15_58 PM.png" alt="VISTA" width="100%">
</p>

---
## Timeline
<p align="center">
  <img src="<p align="center">
  <img src="timeline/schedule/ChatGPT Image Jul 20, 2026, 02_14_43 PM.png" alt="VISTA" width="100%">
</p>" alt="VISTA" width="100%">
</p>

## 🚀 Getting Started

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/<your-username>/VISTA.git
cd VISTA

# Create a virtual environment
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Start the vector database

```bash
docker run -p 6333:6333 qdrant/qdrant
```

### 3. Run the application

```bash
# Backend API
uvicorn app.main:app --reload

# Frontend dashboard
streamlit run dashboard/app.py
```

### 4. Environment variables (`.env`)

```env
VECTOR_DB_HOST=localhost
VECTOR_DB_PORT=6333
POSTGRES_URL=postgresql://user:password@localhost:5432/medicaldb
EMBEDDING_MODEL=all-MiniLM-L6-v2
```

---

## 📖 Full Documentation

Every layer of VISTA — the OCR/ingestion pipeline, the embedding model and why it was chosen, cosine similarity vs. Euclidean distance, how Qdrant's HNSW indexing gets sub-2-second search, the clustering methodology, the PII/metadata separation model, an evaluation methodology, and known limitations — is covered in full in **[`DOCUMENTATION.md`](./DOCUMENTATION.md)**.

<p align="center">
  <a href="./DOCUMENTATION.md">
    <img src="https://img.shields.io/badge/📖_Open_Full_Documentation-2962FF?style=for-the-badge&labelColor=1a1a1a" alt="Open Full Documentation">
  </a>
</p>

Quick summary of what's inside:

- **Data layer** — dataset details, the augmentation methodology used to scale-test the pipeline, PostgreSQL schema, MinIO object storage
- **NLP layer** — how sentence embeddings work, the `all-MiniLM-L6-v2` model, tokenization
- **Similarity & clustering engine** — the cosine similarity math, HNSW indexing internals, k-means vs. hierarchical clustering
- **API & dashboard** — FastAPI endpoint design, Streamlit UI
- **Security** — the PII/vector separation model in detail
- **Evaluation methodology** — concrete metrics (cluster purity vs. ground-truth specialty labels, silhouette score, precision@k)
- **Limitations, future scope, and a glossary**

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
