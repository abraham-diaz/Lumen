from backend.ingestion.embeddings import get_embedding
from backend.db.connection import get_connection

def search (query, top_k=5):
    # Get the embedding for the query
    query_embedding = get_embedding(query)
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT content, chunk_type, start_line, end_line FROM chunks ORDER BY embedding <=> %s LIMIT %s",
                (str(query_embedding.tolist()), top_k)
            )
            return cur.fetchall()

