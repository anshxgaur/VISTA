# VISTA — What Everyone Is Building

This is a simple, no-jargon explanation of the project so everyone knows what they're doing, what the other person is doing, and why it all connects.

## The Big Picture

<p align="center">
  <img src="data/architecture.png" width="100%" alt="VISTA Architecture">
</p>

We're building a smart search system for medical reports. A doctor types something like "blood reports," and instead of the system searching through every single file one by one (slow and expensive), we first sort all files into labeled **boxes** (like "Blood Reports," "X-Ray Reports," "Prescriptions"). The system finds the right **box** first, then picks the best file inside that box based on how recent it is, how often it's been opened, and how important it is.

Think of it like a warehouse: instead of searching every item on every shelf, you first find the right shelf, then pick the item you need from that shelf.

---

## Aashita — Cleaning the Files (ETL)

<p align="center">
  <img src="info/aashita.png" width="80%" alt="Aashita's work">
</p>

**What you're doing in simple words:**
Files come in messy — some are duplicated, some are broken/corrupted. Your job is to clean this mess up before anyone else touches it. You check every file, remove duplicates, throw out broken files, and hand over a clean batch.

**Why it matters:** If dirty data goes in, everything after you (OCR, storage, clustering) breaks or gives wrong results. You're the first filter.

**Technology you need:**
- **Python** — to write the cleaning scripts
- **Hashing (like MD5)** — to detect duplicate files by comparing their fingerprint, not just filename

---

## Aditi — Reading Text From Images (OCR)

<p align="center">
  <img src="info/aditi.png" width="80%" alt="Aditi's work">
</p>

**What you're doing in simple words:**
Some reports are scanned images or photos, not typed text — a computer can't "read" a picture. You use a tool called OCR (Optical Character Recognition) to convert those images into actual readable text. Clean text files just pass through untouched; scanned files go through OCR.

**Why it matters:** Without this step, scanned reports are basically invisible to the rest of the system — they'd never show up in search.

**Technology you need:**
- **PaddleOCR** — the tool that reads text out of images
- **Python** — to build the pipeline that decides "is this a text file or an image file?"

---

## Ankit — Storing Everything (Storage & Warehouse)

<p align="center">
  <img src="info/ankit.png" width="80%" alt="Ankit's work">
</p>

**What you're doing in simple words:**
Once files are cleaned and readable, they need a home. You store the actual raw files in one place (MinIO) and store organized information *about* each file (like specialty, date, ID) in a separate structured database (Neon). Every file gets one unique ID that connects its raw copy to its info row.

**Why it matters:** You're the "filing cabinet." Without consistent IDs linking storage to metadata, nobody downstream can reliably find the right file.

**Technology you need:**
- **MinIO** — stores the actual raw files (like a cloud drive)
- **Neon (PostgreSQL)** — stores structured info about each file, like a spreadsheet database

*(You also co-own the clustering/box-building step with Ansh — see below.)*

---

## Anant — Scoring How Important Each File Is (Analytics & Priority)

<p align="center">
  <img src="info/anant.png" width="80%" alt="Anant's work">
</p>

**What you're doing in simple words:**
Not every file is equally important. A report opened 50 times this week matters more right now than one nobody's touched in a year. You calculate a **priority score** for every file using three things: how fresh it is, how often it's accessed, and how important its category is. This score is what breaks the tie when multiple files are in the same box.

**Why it matters:** Without your score, the system can find the right *box* but has no way to pick the *best file* inside it.

**Technology you need:**
- **DuckDB** — fast tool for analyzing data (like calculating averages/counts quickly)
- **Python** — to combine freshness + frequency + importance into one formula

---

## Arpit — Turning Text Into Numbers (Embeddings & Math)

<p align="center">
  <img src="info/arpit.png" width="80%" alt="Arpit's work">
</p>

**What you're doing in simple words:**
Computers can't compare meaning in plain text directly — so you convert each cleaned document into a list of numbers (a "vector") that captures its meaning. Two documents about similar topics get similar numbers. You also calculate how similar any two documents are, which is the math that Ansh and Ankit's clustering step depends on.

**Why it matters:** You're the translator between human language and math the computer can compare. If your numbers are wrong, the boxes will be wrong too.

**Technology you need:**
- **Sentence Transformers (`all-MiniLM-L6-v2`)** — the model that turns text into number-vectors
- **Cosine similarity (math concept)** — measures how "close" two vectors are in meaning

---

## Ansh — Building the Boxes & Search (Clustering)

<p align="center">
  <img src="info/ansh.png" width="80%" alt="Ansh's work">
</p>

**What you're doing in simple words:**
Using Arpit's number-vectors, you group similar documents together into "boxes" (like automatically sorting mail into folders — "Blood Reports," "X-Rays," etc.). For each box, you write a short summary describing what's in it, and turn that summary into a vector too. When a doctor types a search, the system compares the query to these box-summaries (not every single document) to instantly find the right box.

**Why it matters:** This is the core trick that makes the whole system fast — searching a handful of boxes instead of thousands of documents.

**Technology you need:**
- **K-Means (clustering algorithm)** — automatically groups similar documents into boxes
- **FAISS** — a fast search tool that finds the closest matching box to a query
- **Sentence Transformers** — same embedding model, used on box summaries and search queries

---

## How It All Connects (Simple Flow)

```
Aashita cleans files
        ↓
Aditi extracts text from images
        ↓
Ankit stores files + info
        ↓
Arpit turns text into numbers
        ↓
Ansh + Ankit group similar files into boxes
        ↓
Anant scores how important each file is
        ↓
Doctor searches → system finds the right box → returns the best file
```

Every person's output is the next person's input — so keeping formats consistent (especially `document_id`) is the most important thing to agree on as a team.
