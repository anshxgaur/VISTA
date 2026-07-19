# 🩺 Vector-Based Intelligent Medical Data Lake

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

| Name | Role | Branch & Section |
|---|---|---|
| Ansh Gaur | Team Leader | CS DS 3 C |
| Ankit Shukla | Member | CS DS 3 C |
| Anant Dubey | Member | CS DS 3 C |
| Aditi Shukla | Member | CS DS 3 B |
| Aashita Mishra | Member | CS DS 3 B |
| Arpit Umrao | Member | CS DS 3 A |

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
