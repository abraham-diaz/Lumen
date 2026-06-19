from backend.ingestion.embeddings import get_embedding
from backend.db.connection import get_connection

# Constante de Reciprocal Rank Fusion: suaviza el peso de las posiciones
# altas para que un primer puesto no aplaste por completo a los demás.
RRF_K = 60


def _vector_search(cur, query_embedding, project_name, candidates):
    cur.execute(
        "SELECT chunks.id, chunks.content, chunks.chunk_type, chunks.start_line, chunks.end_line "
        "FROM chunks "
        "JOIN files ON chunks.file_id = files.id "
        "JOIN projects ON files.project_id = projects.id "
        "WHERE projects.name = %s "
        "ORDER BY chunks.embedding <=> %s LIMIT %s",
        (project_name, str(query_embedding.tolist()), candidates),
    )
    return cur.fetchall()


def _text_search(cur, query, project_name, candidates):
    cur.execute(
        "SELECT chunks.id, chunks.content, chunks.chunk_type, chunks.start_line, chunks.end_line "
        "FROM chunks "
        "JOIN files ON chunks.file_id = files.id "
        "JOIN projects ON files.project_id = projects.id "
        "WHERE projects.name = %s "
        "AND chunks.content_tsv @@ plainto_tsquery('simple', %s) "
        "ORDER BY ts_rank(chunks.content_tsv, plainto_tsquery('simple', %s)) DESC "
        "LIMIT %s",
        (project_name, query, query, candidates),
    )
    return cur.fetchall()


def _reciprocal_rank_fusion(*rankings, top_k):
    """Combina varias listas ya ordenadas por relevancia en un único ranking.

    Cada chunk recibe 1 / (RRF_K + posición) por cada ranking en el que
    aparece; las puntuaciones se suman y se ordena de mayor a menor.
    """
    scores = {}
    rows_by_id = {}

    for ranking in rankings:
        for position, row in enumerate(ranking, start=1):
            chunk_id = row[0]
            scores[chunk_id] = scores.get(chunk_id, 0) + 1 / (RRF_K + position)
            rows_by_id[chunk_id] = row

    best_ids = sorted(scores, key=lambda cid: scores[cid], reverse=True)
    return [rows_by_id[cid][1:] for cid in best_ids[:top_k]]


def search(query, project_name, top_k=5, candidates=20):
    query_embedding = get_embedding(query)

    with get_connection() as conn:
        with conn.cursor() as cur:
            vector_results = _vector_search(cur, query_embedding, project_name, candidates)
            text_results = _text_search(cur, query, project_name, candidates)

    return _reciprocal_rank_fusion(vector_results, text_results, top_k=top_k)
