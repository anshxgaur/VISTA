<p align="center">
  <img src="timeline/schedule/hello.png" alt="VISTA " width="100%">
</p>

### Using Cosine Similarity Clustering

A semantic healthcare data platform that organizes and retrieves medical reports based on **meaning**, not just keywords — using vector embeddings, cosine similarity, and a vector database.

![Domain](https://img.shields.io/badge/Domain-AI%2FML%20%7C%20Big%20Data-3B5BDB)
![Status](https://img.shields.io/badge/Status-In%20Development-yellow)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 📌 Problem Statement

Hospitals generate millions of medical reports every year — discharge summaries, lab results, radiology notes, and more. Traditional folder structures and keyword-based search make it difficult for clinicians to find semantically related reports, especially when terminology differs across departments (e.g., *"heart attack"* vs. *"myocardial infarction"*).

This leads to:
- 🔁 Duplicated documentation
- ⏱️ Delayed diagnosis and slower case reviews
- 📉 Inefficient clinical search
- 📈 Increasing administrative burden as data grows

## 💡 Proposed Solution

We built a platform that **understands the meaning** of medical text using transformer-based embeddings and **cosine similarity**, automatically clustering and retrieving reports that are semantically related — even when they don't share the same keywords.

---

## 🏗️ System Architecture

![System Architecture](architecture-diagram.svg)

**Pipeline flow:**

1. **Data Ingestion** – Medical reports (PDF, scanned image, or text) enter the system.
2. **OCR / Text Extraction** – Scanned documents are converted into raw text.
3. **Embedding Generation** – A Sentence Transformer model converts each report into a high-dimensional vector.
4. **Cosine Similarity Matching** – The new vector is compared against existing vectors in the database.
5. **Vector Database Storage** – Vectors are indexed and stored in Qdrant/Milvus for fast retrieval.
6. **Cluster Assignment** – The report is grouped into an existing cluster, or a new cluster is created.
7. **Semantic Search** – A FastAPI backend exposes a natural-language search API over the vector index.
8. **Dashboard** – A Streamlit/React interface lets clinicians search and browse clustered reports.
9. **Metadata Storage** – PostgreSQL securely stores structured metadata alongside each vector.

---

## 🧮 How Cosine Similarity Works

![Cosine Similarity Explained](cosine-similarity-diagram.svg)

Cosine similarity measures the **angle** between two vectors rather than their raw distance — meaning two reports can be recognized as similar even if they're written very differently in wording or length.

```
cos(θ) = (A · B) / (‖A‖ ‖B‖)
```

| Score | Meaning |
|-------|---------|
| ≈ 1.0 | Reports mean nearly the same thing |
| ≈ 0.0 | Reports are unrelated |
| ≈ -1.0 | Reports are semantically opposite |

---

## ⚙️ Tech Stack

| Layer | Technology |
|---|---|
| **Backend API** | Python, FastAPI |
| **Embeddings** | Sentence Transformers |
| **Vector Database** | Qdrant / Milvus |
| **Metadata Storage** | PostgreSQL |
| **Frontend / Dashboard** | Streamlit / React |
| **Deployment** | Docker |

---

## 📂 Dataset

This project uses the **[MTSamples — Medical Transcriptions dataset](https://www.kaggle.com/datasets/tboyle10/medicaltranscriptions)**, a publicly available collection of ~5,000 de-identified medical transcription reports across 40 specialties (Cardiology, Neurology, Orthopedics, Radiology, etc.), scraped from mtsamples.com.

> For future scale-up, the project can be extended to real ICU clinical data via **[MIMIC-III / MIMIC-IV](https://physionet.org/)** (requires PhysioNet credentialing and a data use agreement).

---

## ✨ Key Features

- 🔍 **Semantic search** — find reports by meaning, not exact keyword match
- 🧩 **Self-organizing clustering** — new clusters form automatically as new medical themes emerge
- ⚡ **Fast retrieval** — optimized vector indexing for millions of records
- 🔐 **Secure metadata management** — structured data kept separate from vector index
- 📊 **Interactive dashboard** — clinicians can query and browse results visually

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- Docker (for running the vector database)
- pip / virtualenv

### Installation

```bash
# Clone the repository
git clone https://github.com/<your-username>/vector-medical-data-lake.git
cd vector-medical-data-lake

# Create a virtual environment
python -m venv venv
source venv/bin/activate      # on Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the vector database (Qdrant)
docker run -p 6333:6333 qdrant/qdrant

# Run the backend
uvicorn app.main:app --reload

# Run the dashboard
streamlit run dashboard/app.py
```

### Environment Variables

Create a `.env` file in the project root:

```env
VECTOR_DB_HOST=localhost
VECTOR_DB_PORT=6333
POSTGRES_URL=postgresql://user:password@localhost:5432/medicaldb
EMBEDDING_MODEL=all-MiniLM-L6-v2
```

---

## 📁 Project Structure

```
vector-medical-data-lake/
├── app/
│   ├── main.py                # FastAPI entry point
│   ├── ingestion/              # OCR & text extraction
│   ├── embeddings/             # Embedding generation logic
│   ├── similarity/             # Cosine similarity & clustering
│   └── db/                     # Vector DB & PostgreSQL connectors
├── dashboard/
│   └── app.py                  # Streamlit/React dashboard
├── data/
│   └── mtsamples.csv           # Dataset
├── architecture-diagram.svg    # System architecture diagram (used in README)
├── cosine-similarity-diagram.svg  # Cosine similarity diagram (used in README)
├── requirements.txt
├── docker-compose.yml
└── README.md
```

---

## 🔮 Future Scope

- 🔗 **RAG (Retrieval-Augmented Generation)** integration for AI-generated report summaries
- 🖼️ **Multimodal embeddings** to include medical imaging (X-rays, scans) alongside text
- 🌐 **Federated hospital search** across multiple institutions without centralizing sensitive data
- 🤖 **AI-assisted diagnosis suggestions** based on clustered historical cases

---

## 👥 Team

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
---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.






</p>

---

# 📊 Project Statistics

<p align="center">

| 📄 Medical Reports | 🏥 Medical Departments | 🧠 Embedding Size | ⚡ Average Search | 🎯 Semantic Accuracy |
|:-----------------:|:---------------------:|:----------------:|:----------------:|:--------------------:|
| **5000+** | **40+** | **768-D** | **<2 sec** | **95%** |

</p>

---

# 🔄 Project Workflow

<p align="center">
<img src="timeline/workflow.png" width="100%">
</p>

> **Workflow**

```
Medical Reports
        │
        ▼
Data Ingestion
        │
        ▼
Data Cleaning
        │
        ▼
Embedding Generation
        │
        ▼
Cosine Similarity
        │
        ▼
Semantic Clustering
        │
        ▼
Vector Database
        │
        ▼
Semantic Search
        │
        ▼
Dashboard
```

---

# ⚖️ Traditional Search vs VISTA

<p align="center">
<img src="timeline/before_after.png" width="100%">
</p>

## ❌ Traditional Hospital Search

```
Doctor

├── Database
├── PDFs
├── Reports
├── Bills
└── Notes

❌ Search takes several minutes
```

---

## ✅ Search using VISTA

```
Doctor

↓

Natural Language Query

↓

Embedding Generation

↓

Semantic Search

↓

Top 5 Relevant Reports

✅ Search takes less than 2 seconds
```

---

# 📌 Problem Statement

Hospitals generate millions of medical reports every year — discharge summaries, lab results, radiology notes, prescriptions, and clinical observations.

Traditional hospital storage relies on folder structures and keyword-based search, making it difficult to retrieve semantically related reports when different medical terminology is used (e.g., **Heart Attack** vs **Myocardial Infarction**).

This leads to

- 🔁 Duplicate records
- ⏱️ Slow report retrieval
- 📉 Inefficient diagnosis support
- 📈 Increasing storage complexity
- 💰 Higher operational cost

---

# 💡 Proposed Solution

VISTA understands the **meaning** behind medical reports rather than matching exact keywords.

Using transformer embeddings, cosine similarity, and semantic clustering, the platform automatically groups related reports and enables natural-language search over millions of medical records.

---

# 🏗️ System Architecture

<p align="center">
<img src="architecture-diagram.svg" width="100%">
</p>

### Pipeline

1. Medical Report Upload
2. OCR & Text Extraction
3. Data Cleaning
4. Embedding Generation
5. Cosine Similarity
6. Semantic Clustering
7. Vector Database
8. Metadata Storage
9. Semantic Search API
10. Dashboard Visualization

---

# 🧮 How Cosine Similarity Works

<p align="center">
<img src="cosine-similarity-diagram.svg" width="90%">
</p>

Cosine Similarity measures the **angle** between vectors instead of raw distance.

Two reports discussing the same disease will produce vectors pointing in similar directions even if they use different wording.

```
cos(θ)= (A · B)/(||A|| ||B||)
```

| Score | Meaning |
|--------|---------|
| 1.0 | Almost identical meaning |
| 0.8+ | Highly related |
| 0.5 | Moderately related |
| 0 | Unrelated |
| -1 | Opposite meaning |

---

# ⚙️ Technology Stack

<p align="center">
<img src="timeline/tech_stack.png" width="90%">
</p>

## Technologies Used

| Layer | Technology |
|-------|------------|
| 🐍 Programming | Python |
| ⚡ Backend | FastAPI |
| 🧠 AI Model | Sentence Transformers |
| 📐 Similarity | Cosine Similarity |
| 🗄️ Vector Database | Qdrant |
| 📦 Metadata Database | PostgreSQL |
| 📊 Dashboard | Streamlit |
| 🐳 Deployment | Docker |
| ☁️ Storage | MinIO |
| 📚 Dataset | MTSamples |

---

# 📂 Dataset

This project uses the **Medical Transcriptions (MTSamples)** dataset.

### Dataset Highlights

- 📄 5000+ Medical Reports
- 🏥 40+ Medical Specialties
- 🩺 Cardiology
- 🧠 Neurology
- 🦴 Orthopedics
- 🩻 Radiology
- 💊 General Medicine
- 🧬 Oncology

Future versions can be extended using MIMIC-III and MIMIC-IV datasets.

---

# ✨ Key Features

- 🔍 Semantic Search
- 🧠 Transformer Embeddings
- 📐 Cosine Similarity Matching
- 🗂️ Automatic Semantic Clustering
- ⚡ Fast Vector Search
- 🔒 Secure Metadata Storage
- 📊 Interactive Dashboard
- 📈 Highly Scalable Architecture
- ☁️ Cloud Ready
- 🏥 Hospital Data Lake

---

# 🚀 Getting Started

## Prerequisites

- Python 3.10+
- Docker
- PostgreSQL
- Qdrant
- Git

---

## Installation

```bash
git clone https://github.com/<your-username>/VISTA.git

cd VISTA

python -m venv venv

source venv/bin/activate

# Windows
venv\Scripts\activate

pip install -r requirements.txt

docker run -p 6333:6333 qdrant/qdrant

uvicorn app.main:app --reload

streamlit run dashboard/app.py
```

---

## Environment Variables

```env
VECTOR_DB_HOST=localhost

VECTOR_DB_PORT=6333

POSTGRES_URL=postgresql://user:password@localhost:5432/medicaldb

EMBEDDING_MODEL=all-MiniLM-L6-v2
```

---

# 📁 Project Structure

<p align="center">
<img src="timeline/folder_structure.png" width="90%">
</p>

```text
VISTA
│
├── Backend
│   ├── FastAPI
│   ├── API
│   ├── Embeddings
│   ├── Semantic Search
│   ├── Similarity Engine
│   └── Data Ingestion
│
├── Database
│   ├── PostgreSQL
│   ├── Qdrant
│   └── Metadata
│
├── Frontend
│   ├── Dashboard
│   └── Streamlit
│
├── Dataset
│
├── Documentation
│
├── Timeline
│
└── README.md
```

---

# 📅 Development Roadmap

<p align="center">
<img src="timeline/schedule/roadmap.png" width="100%">
</p>

---

# 🔮 Future Scope

- 🤖 AI Diagnosis Assistance
- 📑 Automatic Report Summarization
- 🩻 Multimodal Embeddings
- 🌐 Federated Hospital Search
- ☁️ Cloud-native Deployment
- 📈 Predictive Analytics
- 🧬 Clinical Decision Support
- 🔗 Retrieval-Augmented Generation (RAG)

---


---



<div align="center">

## Made with ❤️ by Team VISTA

**Vector Intelligent Semantic Technology for Healthcare Analytics**

</div>
