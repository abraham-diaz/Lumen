# Lumen

RAG system for indexing and querying code from personal projects.

## Stack

- **FastAPI** — REST API
- **PostgreSQL + pgvector** — storage, semantic search and full-text search
- **sentence-transformers** (MiniLM-L6-v2) — embedding generation (384-dim)
- **llama-cpp-python + Gemma 2 2B (Q4_K_M, GGUF)** — local LLM for answer generation, runs in-process (no Ollama server)
- **tree-sitter** — smart chunking by function/class
- **GitPython** — clones a repo URL into a temporary folder for indexing

## Ingestion flow

`POST /index` receives a `project_name` and a `git_url`:

1. Clones the repo to a temporary folder (`tempfile.mkdtemp()`)
2. Registers the project, using the git URL as its persistent identifier
3. Walks the clone looking for `.py` files, chunking each one with tree-sitter
4. Embeds every chunk (MiniLM) and stores it in `chunks`, replacing any previous chunks for that file
5. Deletes the temporary clone — only chunks + embeddings persist, never the raw repo

Re-indexing the same project re-clones, re-chunks and replaces existing chunks (no duplicates).

## Query flow

`POST /query` receives a `query` and a `project_name`:

1. Embeds the question (MiniLM)
2. Hybrid search scoped to that project only:
   - vector similarity (pgvector, HNSW, cosine)
   - full-text search (Postgres `tsvector`/GIN, `ts_rank`)
   - both rankings merged via **Reciprocal Rank Fusion**
3. Top chunks become the context (with chunk type + line numbers) passed to Gemma, with an instruction to answer only from that context
4. Returns `{ "answer": "...", "sources": [...] }` — `sources` is the exact retrieved code, untouched by the model

## Database

Three tables: `projects` → `files` → `chunks`, CASCADE deletes down the hierarchy.

- `chunks.embedding` — `vector(384)`, HNSW index (`vector_cosine_ops`)
- `chunks.content_tsv` — generated `tsvector` column, GIN index

## Setup

```bash
docker compose up -d                  # PostgreSQL + pgvector, port 5433
pip install -r requirements.txt
python backend/db/schema.py           # creates tables + indexes
uvicorn main:app --reload
```

Requires `models/gemma-2-2b-it-q4_k_m.gguf` (not committed — gitignored).

## Not implemented yet

- **Watchdog** — automatic re-indexing on file change
- Listing / deleting indexed projects
- Skipping unchanged files on re-index (`files.file_hash` exists but is unused)

## Deployment

VPS: 4 vCores, 4GB RAM, 120GB NVMe.
