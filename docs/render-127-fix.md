# Render deployment failure: exit status 127 — diagnosis & fix
# Generated: 2026-10-29

## What exit status 127 means on Render
Exit status 127 means "command not found" at **runtime start**. Render's
start command `uvicorn Backend.api:app --host 0.0.0.0 --port $PORT` exited
with 127, so one of these is true:

1. uvicorn (or a dependency) is not installed — because the build step
   `pip install -r requirements.txt` failed or was skipped.
2. `Backend/api.py` does not exist at the path Render's build env expects.
3. An import at the top of Backend/api.py crashes at startup (import-time
   error) before uvicorn can bind the port.

## Root cause in your case (confirmed)
The earlier deploy log showed:
  ERROR: Could not find a version that satisfies the requirement paddlepaddle>=2.6.0
  (from versions: none)
  ERROR: No matching distribution found for paddlepaddle>=2.6.0
  ==> Build failed 😞

Because `pip install -r requirements.txt` failed on that build, Render's
runtime environment had no uvicorn, no fastapi, no pydantic — nothing.
So the start command got 127.

That build was using Python 3.14 (Render's current default), and
paddlepaddle publishes wheels only for Python 3.9-3.13, so on 3.14 pip
found zero compatible versions → build failed → nothing installed.

## What was fixed (pushed as a95829e)
- Pinned Python to 3.11.9 via .python-version (Render reads it at build
  time) — paddlepaddle wheels exist for 3.11.
- Kept PYTHON_VERSION=3.11.9 in render.yaml envVars for redundancy.
- Removed the 5GB disk block from render.yaml (free-tier web services
  don't support persistent disks, and the block was blocking blueprint sync).

Verified in a Python 3.11 CPU environment that all of these install
cleanly:
  paddlepaddle 3.3.1, paddleocr 3.7.0, uvicorn 0.54.0, fastapi 0.162.0,
  pydantic 2.14.1, numpy 2.4.6 (downgraded to 2.3.5 by paddle stack),
  scikit-learn 1.9.1, faiss-cpu 1.15.1, duckdb 2.0.0, minio 7.2.20,
  psycopg2-binary 2.9.13, sqlalchemy 2.1.6, streamlit 1.66.1, plotly 7.1.0,
  sentence-transformers 6.2.0 + torch 2.15.0, pypdf, python-docx, tqdm,
  loguru, python-dotenv, pydantic-settings, and the sentence-transformer
  model all-MiniLM-L6-v2 loads in 2.57s and encodes to (1, 384).

## What to do now (step-by-step)

### Step 1 — Confirm Render rebuilt from your fix commit
Open your Render Dashboard → your service → Deploys (or Logs).
Look for a deploy that references commit a95829e (or the latest push).
In its build log, search for the line:
  ==> Installing Python version 3.11.9...
If that line is MISSING, Render is still running the old failed build.
See Step 2. If it IS present, skip to Step 3.

### Step 2 — Force a fresh build (clear build cache + redeploy)
Because the previous failed build left a cache with no installed packages,
Render may reuse it. Force a fresh build:

Option A (preferred, clears stale cache):
  Render Dashboard → your service → Deploys → Manual Deploy →
  "Clear build cache & deploy"

Option B (deploy hook, requires service ID):
  curl -X POST "https://api.render.com/deploy/srv-<YOUR_SERVICE_ID>"

After this, the new build should show:
  ==> Installing Python version 3.11.9...
  ...
  Successfully installed uvicorn fastapi pydantic ... paddlepaddle paddleocr ...
  ==> Build successful

Then the start command should find uvicorn and the service should become
healthy (health check at /health, which exists in Backend/api.py).

### Step 3 — If still 127 after a fresh build, inspect the actual error
In the new deploy's Logs, look for the FIRST error line before "exited
with status 127". Common ones and their fixes:

- "ModuleNotFoundError: No module named '...'"
  → that package isn't in requirements.txt or the build command didn't run.
  Confirm build command = `pip install -r requirements.txt` in Settings →
  Build Command.

- "cannot import name ..." or "ImportError"
  → a package version mismatch at runtime. Ensure the Python version
  setting (PYTHON_VERSION env var OR .python-version) = 3.11.9.

- "Backend.api:app" not found
  → Render clones the repo into its build dir; ensure Backend/api.py
  exists in the repo root and is tracked in git (it is — confirmed).

- Health check failure instead of 127
  → /health exists (Backend/api.py line 208-218). If the health check
  fails with status N, Render treats 4xx/5xx as unhealthy. Check that
  /health returns 200 — it may depend on env vars (NEON_DATABASE_URL etc.)
  being set.

### Step 4 — Environment variables to set in Render Dashboard → Settings →
Environment (if not already set)
These are referenced in the code but have no default or are marked sync:false:
  PYTHON_VERSION      = 3.11.9            (already in render.yaml envVars)
  NEON_DATABASE_URL   = (your Neon Postgres URL)
  VISTA_CORS_ORIGINS  = http://localhost:3000,http://127.0.0.1:3000
  MINIO_ENDPOINT      = (your MinIO endpoint)
  MINIO_ACCESS_KEY    = (your MinIO access key)
  MINIO_SECRET_KEY    = (your MinIO secret key)
  MINIO_BUCKET_NAME   = vista-lake         (already set in render.yaml)
  MINIO_SECURE        = true               (already set in render.yaml)
  EMBEDDING_DEVICE    = cpu                (already set in render.yaml)

If any of these are missing, mandatory code paths (e.g., the /health
endpoint's database check) may raise, which can surface as a startup crash.

### Why the disk block was removed
Free-tier Render web services do not support persistent disks. The disk
block:
  disk:
    name: vista-data
    mountPath: /opt/render/project/src/data
    sizeGB: 5
caused blueprint sync failures. If you need persistent storage later,
attach a managed disk or use an external store (MinIO is already in the
stack). The data directory `./data/` on disk would be ephemeral on
Render's free tier anyway.

## Files changed in this fix (commit a95829e)
- .python-version         → 3.11.9
- render.yaml            → PYTHON_VERSION=3.11.9 kept, disk block removed
- (remote upload commit b9792ff preserved: vista (BWB).pptx)

## Verification done before pushing
1. Full requirements.txt resolved against PyPI for Linux + CPython 3.11 —
   clean wheel resolution, exit 0. paddlepaddle 3.3.1 and paddleocr 3.7.0
   both resolved.
2. Clean venv install (Python 3.11, Windows) of core deps succeeded
   (fastapi, uvicorn, pydantic, numpy, sklearn, faiss-cpu, duckdb, minio,
   psycopg2-binary, sqlalchemy, streamlit, plotly, pandas, etc.) — exit 0.
3. sentence-transformers 6.2.0 + torch 2.15.0 installed; default model
   all-MiniLM-L6-v2 loads (2.57s) and encodes to (1, 384).
4. paddlepaddle 3.3.1 + paddleocr 3.7.0 installed; both import OK.
5. Backend/api.py confirmed present with /health route.
6. .python-version confirmed present (3.11.9), committed and pushed.

## Remaining unknowns (to confirm from Render Dashboard)
- Whether the new commit a95829e actually triggered a fresh build on
  Render, or Render reused a cached failed build.
- Whether the build command in the live service's Settings is exactly
  `pip install -r requirements.txt`.
- Whether any env var the code requires is still missing on Render.
- Whether the health check path is still /health (it is in render.yaml).
