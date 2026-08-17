# 📘 VISTA Documentation

# Vector Intelligent Semantic Search Text Analysis

Welcome to the complete technical documentation of VISTA.

While the README provides a quick overview of the project, this document explains every component of the system in detail.

---

# Table of Contents

1. Introduction
2. System Architecture
3. Complete Pipeline
4. Data Ingestion
5. OCR Layer
6. Text Cleaning
7. AI Embeddings
8. Dual Storage Architecture
9. Semantic Search
10. Clustering
11. Backend API
12. Frontend Dashboard
13. Deployment
14. Security
15. Future Improvements

---

# Introduction

Traditional hospital systems search medical reports using exact keywords.

For example,

Searching for

```
Heart Attack
```

may not return reports containing

```
Myocardial Infarction
```

even though both describe the same medical condition.

VISTA solves this problem using semantic search.

Instead of comparing words, VISTA compares the meaning of reports using AI-generated embeddings.

---

# System Architecture

```
                Medical Reports
          (PDF / Image / Text Files)
                       │
                       ▼
                OCR (Optional)
                       │
                       ▼
                Text Cleaning
                       │
                       ▼
            Sentence Transformer
                       │
                       ▼
              Generate Embeddings
                       │
        ┌──────────────┴──────────────┐
        ▼                             ▼
 Qdrant Vector Database        PostgreSQL Database
        │                             │
        └──────────────┬──────────────┘
                       ▼
             Semantic Search Engine
                       │
                       ▼
             Automatic Clustering
                       │
                       ▼
                  FastAPI Backend
                       │
                       ▼
               Streamlit Dashboard
```

---

# Complete Pipeline

Every uploaded report follows the same workflow.

## Step 1 — Report Upload

VISTA accepts:

- PDF documents
- Medical images
- Plain text files

Each uploaded report is validated before processing begins.

---

## Step 2 — OCR

If the uploaded report is an image or scanned PDF, OCR extracts readable text.

This allows scanned reports to be processed just like normal text files.

---

## Step 3 — Text Cleaning

Before AI processing begins, VISTA cleans the text.

Cleaning includes:

- Removing extra spaces
- Removing empty lines
- Fixing formatting
- Removing OCR artifacts
- Standardizing text

This improves embedding quality.

---

## Step 4 — Embedding Generation

The cleaned report is passed into a Sentence Transformer model.

Example model:

```
all-MiniLM-L6-v2
```

The model converts the report into a numerical vector called an embedding.

Reports discussing similar medical conditions generate similar embeddings even when different words are used.

---

# Dual Storage Architecture

VISTA separates semantic information from structured information.

```
                 Report
                   │
        ┌──────────┴──────────┐
        ▼                     ▼

   Embeddings            Metadata

        ▼                     ▼

     Qdrant             PostgreSQL
```

## Why Qdrant?

Qdrant is optimized for storing vectors and performing fast similarity searches.

---

## Why PostgreSQL?

PostgreSQL stores structured data such as:

- Patient ID
- Department
- Report Type
- Upload Date
- Metadata

Separating these databases improves scalability and security.

---

# Semantic Search

When users search,

```
Chest Pain
```

the query is converted into an embedding.

Instead of matching words, VISTA compares vector similarity using cosine similarity.

```
User Query
      │
      ▼
Generate Embedding
      │
      ▼
Search Qdrant
      │
      ▼
Return Most Similar Reports
```

This enables finding reports with similar meaning even if the wording differs.

---

# Clustering

VISTA automatically groups reports with similar meanings.

Benefits include:

- Organizing thousands of reports
- Discovering related medical cases
- Simplifying navigation
- Finding patterns in data

Clustering is independent of user searches and helps users browse semantically related reports.

---

# Backend API

FastAPI serves as the communication layer.

Responsibilities include:

- Report upload
- Embedding generation
- Search requests
- Database interaction
- Returning search results

---

# Frontend Dashboard

The Streamlit dashboard provides:

- Report Upload
- Semantic Search
- Cluster Browser
- Search Results
- Report Viewer

This creates a simple interface for users without requiring technical knowledge.

---

# Deployment

VISTA is designed using Docker containers.

Services include:

- FastAPI
- PostgreSQL
- Qdrant
- MinIO
- Streamlit

Docker ensures the application runs consistently across different environments.

---

# Security

VISTA separates patient metadata from vector embeddings.

This design:

- Improves privacy
- Reduces risk of exposing sensitive information
- Makes the system easier to scale

Future versions can also include authentication, authorization, and audit logging.

---

# Future Improvements

Potential enhancements include:

- Clinical BERT embeddings
- RAG-based medical assistant
- Multi-hospital semantic search
- Medical image embeddings
- Real-time streaming pipelines
- Advanced analytics dashboards

---

# Conclusion

VISTA combines Natural Language Processing, Vector Databases, Semantic Search, Clustering, and Modern Backend Technologies to build an intelligent medical report retrieval system.

Instead of searching for exact keywords, users can search by meaning, making information retrieval faster, smarter, and more accurate.
