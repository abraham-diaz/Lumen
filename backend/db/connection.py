import psycopg

def get_connection():
    return psycopg.connect(
        host="localhost",
        port=5433,
        dbname="lumen",
        user="lumen",
        password="lumen_password",
    )

