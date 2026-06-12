from backend.db.connection import get_connection

def add_project (name,path):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO projects (name, path) VALUES (%s, %s) RETURNING id",
                (name, path)
            )
            result = cur.fetchone()
            if result is None:
                raise ValueError("Failed to insert project")
            project_id = result[0]
            conn.commit()
            return project_id

