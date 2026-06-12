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
    id         SERIAL PRIMARY KEY,
    file_id    INTEGER NOT NULL REFERENCES files(id) ON DELETE CASCADE,
    content    TEXT NOT NULL,
    start_line INTEGER,
    end_line   INTEGER,
    chunk_type TEXT,
    embedding  vector(384)
);

CREATE INDEX IF NOT EXISTS chunks_embedding_idx
    ON chunks USING hnsw (embedding vector_cosine_ops);
"""

if __name__ == "__main__":
    with psycopg.connect(
        host="localhost",
        port=5433,
        dbname="lumen",
        user="lumen",
        password="lumen_password",
    ) as conn:
        conn.execute(SQL)
        conn.commit()
    print("Schema created successfully.")
