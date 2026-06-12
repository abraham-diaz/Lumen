from backend.db.connection import get_connection

def add_file(project_id, file_path, file_hash=None):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO files (project_id, path, file_hash) " \
                "VALUES (%s, %s, %s) ON CONFLICT (project_id, path) DO NOTHING " \
                "RETURNING id",
                (project_id, file_path, file_hash)
            )
            result = cur.fetchone()
            if result is None:
                cur.execute(
                    "SELECT id FROM files WHERE project_id = %s AND path = %s",
                    (project_id, file_path)
                )
                result = cur.fetchone()
                if result is None:
                    raise RuntimeError("Unable to insert or locate file record")
            file_id = result[0]
            conn.commit()
            return file_id
