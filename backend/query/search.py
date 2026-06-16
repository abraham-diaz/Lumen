from backend.ingestion.embeddings import get_embedding
from backend.db.connection import get_connection

# Constante de Reciprocal Rank Fusion: suaviza el peso de las posiciones
# altas para que un primer puesto no aplaste por completo a los demás.
RRF_K = 60


def _vector_search(cur, query_embedding, candidates):
    cur.execute(
        "SELECT id, content, chunk_type, start_line, end_line "
        "FROM chunks ORDER BY embedding <=> %s LIMIT %s",
        (str(query_embedding.tolist()), candidates),
    )
    return cur.fetchall()


def _text_search(cur, query, candidates):
    cur.execute(
        "SELECT id, content, chunk_type, start_line, end_line "
        "FROM chunks "
        "WHERE content_tsv @@ plainto_tsquery('simple', %s) "
        "ORDER BY ts_rank(content_tsv, plainto_tsquery('simple', %s)) DESC "
        "LIMIT %s",
        (query, query, candidates),
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


def search(query, top_k=5, candidates=20):
    query_embedding = get_embedding(query)

    with get_connection() as conn:
        with conn.cursor() as cur:
            vector_results = _vector_search(cur, query_embedding, candidates)
            text_results = _text_search(cur, query, candidates)

    return _reciprocal_rank_fusion(vector_results, text_results, top_k=top_k)
