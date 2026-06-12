# Lumen — Claude Code context

## Project goal

RAG system in pure Python for indexing and querying code from personal projects. No frontend — REST API only.

## Development style

- User builds the code themselves, Claude guides with minimal code examples
- Explain decisions before writing code
- No unnecessary abstractions or premature generalization

## Structure

```
Lumen/
├── docker-compose.yml
├── main.py
└── backend/
    ├── api/
    ├── db/
    ├── ingestion/
    └── query/
```

## Stack

- Python + FastAPI
- PostgreSQL 17 + pgvector (via Docker)
- sentence-transformers MiniLM-L6-v2 (384-dim embeddings)
- Ollama + gemma2:2b (local LLM)
- tree-sitter (chunking)
- GitPython, Watchdog

## Database

Three tables: `projects` → `files` → `chunks`

- `embedding vector(384)` in chunks
- HNSW index with `vector_cosine_ops`
- CASCADE deletes down the hierarchy

## Local services

- PostgreSQL: `localhost:5432`, db=`lumen`, user=`lumen`, password=`lumen_password`
