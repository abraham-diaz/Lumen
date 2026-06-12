from backend.db.connection import get_connection


def add_chunk(file_id, content, start_line, end_line, chunk_type, embedding= None):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO chunks (file_id, content, start_line, end_line, chunk_type, embedding) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id",
                (file_id, content, start_line, end_line, chunk_type, embedding)
            )
            result = cur.fetchone()
            if result is None:
                raise ValueError("Failed to insert chunk")
            chunk_id = result[0]
            conn.commit()
            return chunk_id
        
