import os
import psycopg

def get_connection():
    return psycopg.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "5433")),
        dbname=os.getenv("DB_NAME", "lumen"),
        user=os.getenv("DB_USER", "lumen"),
        password=os.getenv("DB_PASSWORD", "lumen_password"),
    )

