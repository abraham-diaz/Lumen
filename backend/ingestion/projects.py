from backend.db.connection import get_connection

def add_project(name, path):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO projects (name, path) VALUES (%s, %s) "
                "ON CONFLICT (path) DO NOTHING RETURNING id",
                (name, path)
            )
            result = cur.fetchone()
            if result is None:
                cur.execute("SELECT id FROM projects WHERE path = %s", (path,))
                result = cur.fetchone()
                if result is None:
                    raise RuntimeError("Unable to insert or locate project record")
            project_id = result[0]
            conn.commit()
            return project_id


def save_description(project_id: int, description: str):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE projects SET description = %s WHERE id = %s",
                (description, project_id)
            )
            conn.commit()
