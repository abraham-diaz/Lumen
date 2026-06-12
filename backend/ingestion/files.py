from backend.db.connection import get_connection

def add_file(project_id, file_path, file_hash=None):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO files (project_id, path, file_hash) VALUES (%s, %s, %s) RETURNING id",
                (project_id, file_path, file_hash)
            )
            result = cur.fetchone()
            if result is None:
                raise ValueError("Failed to insert file")
            file_id = result[0]
            conn.commit()
            return file_id
