from backend.db.connection import get_connection
from backend.query.llm import llm


def describe_project(project_id: int) -> str:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT DISTINCT ON (f.id) c.content
                FROM chunks c JOIN files f ON c.file_id = f.id
                WHERE f.project_id = %s
                ORDER BY f.id, c.start_line
                LIMIT 8
            """, (project_id,))
            rows = cur.fetchall()

    context = "\n\n".join(r[0] for r in rows)
    prompt = f"""<start_of_turn>user
Basándote en estos fragmentos de código, describe en 2-3 frases qué hace este proyecto: su propósito y tecnologías clave. Solo la descripción, sin introducción.

{context}<end_of_turn>
<start_of_turn>model
"""
    response = llm(prompt, max_tokens=150, stop=["<end_of_turn>"], stream=False)
    return response["choices"][0]["text"].strip()
