import psycopg

SQL = """
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS projects (
    id         SERIAL PRIMARY KEY,
    name       TEXT NOT NULL,
    path       TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS files (
    id         SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    path       TEXT NOT NULL,
    file_hash  TEXT,
    indexed_at TIMESTAMP DEFAULT NOW(),
    UNIQUE (project_id, path)
);

CREATE TABLE IF NOT EXISTS chunks (
    id          SERIAL PRIMARY KEY,
    file_id     INTEGER NOT NULL REFERENCES files(id) ON DELETE CASCADE,
    content     TEXT NOT NULL,
    start_line  INTEGER,
    end_line    INTEGER,
    chunk_type  TEXT,
    embedding   vector(384),
    content_tsv tsvector GENERATED ALWAYS AS (to_tsvector('simple', content)) STORED
);

CREATE INDEX IF NOT EXISTS chunks_embedding_idx
    ON chunks USING hnsw (embedding vector_cosine_ops);
"""

# CREATE TABLE IF NOT EXISTS no toca tablas que ya existen, así que para
# bases de datos creadas antes de añadir content_tsv hace falta esta migración.
MIGRATION_SQL = """
ALTER TABLE chunks
    ADD COLUMN IF NOT EXISTS content_tsv tsvector
    GENERATED ALWAYS AS (to_tsvector('simple', content)) STORED;

CREATE INDEX IF NOT EXISTS chunks_content_tsv_idx
    ON chunks USING GIN (content_tsv);

ALTER TABLE projects ADD COLUMN IF NOT EXISTS description TEXT;
"""

if __name__ == "__main__":
    from backend.db.connection import get_connection
    with get_connection() as conn:
        conn.execute(SQL)
        conn.execute(MIGRATION_SQL)
        conn.commit()
    print("Schema created successfully.")
