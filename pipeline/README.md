
# ⚙️ VISTA Pipeline

VISTA processes every medical report through a series of intelligent steps before making it searchable. Instead of searching for exact keywords, VISTA understands the meaning of medical text using AI embeddings.

## Pipeline Overview

```text
                     Medical Report
            (Text / PDF / Image Upload)
                           │
                           ▼
                  OCR (If Required)
        Convert scanned images into text
                           │
                           ▼
                    Text Cleaning
      Remove noise, extra spaces, formatting,
          and prepare text for AI models
                           │
                           ▼
               Generate AI Embeddings
     Convert the report into a numerical vector
          that represents its semantic meaning
                           │
                           ▼
                    Store the Data
        ┌───────────────────────────────┐
        │                               │
        ▼                               ▼
 Qdrant Vector Database        PostgreSQL Database
 Store AI Embeddings           Store Patient Metadata
        │                               │
        └──────────────┬────────────────┘
                       ▼
             Semantic Similarity Search
        Find reports based on meaning,
           not exact keyword matching
                       │
                       ▼
              Automatic Clustering
      Group similar reports together
         without manual categorization
                       │
                       ▼
                 FastAPI Backend
      Provides REST APIs for the system
                       │
                       ▼
             Streamlit Dashboard
   Interactive interface for searching,
      filtering and viewing reports
```

## Pipeline Explanation

### 1. Report Upload

Users upload medical reports in different formats such as PDF, images, or plain text.

---

### 2. OCR (Optical Character Recognition)

If the uploaded report is an image or scanned PDF, OCR extracts readable text from it.

---

### 3. Text Cleaning

The extracted text is cleaned by removing unnecessary spaces, formatting issues, and OCR errors before processing.

---

### 4. AI Embedding Generation

The cleaned report is converted into an embedding using a Sentence Transformer model. This embedding captures the meaning of the report instead of just the words.

---

### 5. Data Storage

VISTA stores information in two different databases.

- **Qdrant** stores the vector embeddings.
- **PostgreSQL** stores report metadata and structured information.

Keeping them separate improves organization and scalability.

---

### 6. Semantic Search

When a user searches, the query is converted into an embedding and compared with stored vectors to retrieve the most relevant reports.

---

### 7. Clustering

Reports with similar meanings are automatically grouped together, making large datasets easier to explore.

---

### 8. Backend API

FastAPI manages all communication between the frontend and the databases.

---

### 9. Dashboard

A Streamlit dashboard allows users to upload reports, search semantically, browse clusters, and visualize results.

---

## 📘 Learn More

Want to understand how every component works internally, including embeddings, vector databases, clustering, architecture, and deployment?

<p align="center">

<a href="./DOCUMENTATION.md">

<img src="https://img.shields.io/badge/📘%20Full%20Documentation-Read%20Here-blue?style=for-the-badge">

</a>

</p>
