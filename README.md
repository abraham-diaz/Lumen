# Lumen

RAG system for indexing and querying code from personal projects.

## Stack

- **FastAPI** — REST API + frontend estático
- **PostgreSQL + pgvector** — almacenamiento, búsqueda semántica y full-text
- **sentence-transformers** (MiniLM-L6-v2) — embeddings 384-dim
- **llama-cpp-python + Gemma 2 2B (Q4_K_M, GGUF)** — LLM local, corre in-process
- **tree-sitter** — chunking por función/clase
- **GitPython** — clona repos remotos para indexarlos

## Ingestion flow

`POST /index` recibe `project_name` y `git_url`:

1. Clona el repo en un directorio temporal
2. Registra el proyecto usando la URL como identificador único
3. Recorre el clon buscando `.py`, chunkea con tree-sitter
4. Embeds cada chunk (MiniLM) y lo guarda en `chunks`, reemplazando los anteriores
5. Genera una descripción del proyecto con el LLM y la guarda en `projects.description`
6. Borra el clon temporal — solo persisten chunks + embeddings

Re-indexar el mismo proyecto re-clona, re-chunkea y reemplaza (sin duplicados).

## Query flow

`POST /query` recibe `query` y `project_name`:

1. Embeds la pregunta (MiniLM)
2. Búsqueda híbrida limitada a ese proyecto:
   - Similitud vectorial (pgvector, HNSW, cosine)
   - Full-text (Postgres `tsvector`/GIN, `ts_rank`)
   - Rankings fusionados con **Reciprocal Rank Fusion**
3. Los top chunks se pasan como contexto a Gemma con instrucción de responder solo desde ese contexto
4. Devuelve `{ "answer": "...", "sources": [...] }`

## Other endpoints

- `GET /projects` — lista proyectos indexados con su descripción generada por el LLM

## Database

Tres tablas: `projects` → `files` → `chunks`, CASCADE deletes.

- `chunks.embedding` — `vector(384)`, HNSW index (`vector_cosine_ops`)
- `chunks.content_tsv` — columna `tsvector` generada, GIN index
- `projects.description` — descripción generada automáticamente al indexar

## Deploy con Docker

```bash
docker-compose up --build -d
```

Levanta PostgreSQL + pgvector y la API. En el primer arranque ejecuta automáticamente la migración del schema.

Requiere `models/gemma-2-2b-it-q4_k_m.gguf` montado en `./models/` (no está en git).

Variables de entorno (con defaults para dev local):

| Variable | Default | Docker |
|---|---|---|
| `DB_HOST` | `localhost` | `db` |
| `DB_PORT` | `5433` | `5432` |
| `DB_NAME` | `lumen` | `lumen` |
| `DB_USER` | `lumen` | `lumen` |
| `DB_PASSWORD` | `lumen_password` | `lumen_password` |

## Dev local

```bash
docker-compose up -d db         # solo PostgreSQL
pip install -r requirements.txt
python -m backend.db.schema     # crea tablas + indexes
uvicorn main:app --reload
```

## CI/CD

GitHub Actions despliega automáticamente en cada push a `main` via SSH.

Secrets necesarios: `SSH_HOST`, `SSH_USER`, `SSH_KEY`, `DEPLOY_PATH`.

## Not implemented yet

- **Watchdog** — re-indexado automático al cambiar ficheros
- Borrado de proyectos indexados
- Saltar ficheros sin cambios en re-index (`files.file_hash` existe pero no se usa)
