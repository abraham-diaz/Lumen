# Lumen

RAG system for indexing and querying code from personal projects.

## Stack

- **FastAPI** — REST API
- **PostgreSQL + pgvector** — storage and semantic search
- **sentence-transformers** (MiniLM-L6-v2) — embedding generation
- **Ollama + gemma2:2b** — local LLM for answer generation
- **tree-sitter** — smart chunking by function/class
- **GitPython** — ingestion from GitHub repos
- **Watchdog** — file watcher for automatic re-indexing

## Ingestion modes

- **Local** — point to a folder and index all code files
- **Watched** — watcher detects changes and re-indexes automatically
- **GitHub** — provide a repo URL, clone it, and process like a local repo

## Pipeline

```
Files → tree-sitter (chunk by function/class) → sentence-transformers (embeddings) → PostgreSQL + pgvector
```

## Query flow

```
Question → embedding → semantic search (pgvector) → top chunks as context → Ollama (gemma2:2b) → answer
```

## Setup

```bash
docker compose up -d
```

## Deployment

VPS: 4 vCores, 4GB RAM, 120GB NVMe.
