import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os

# Configuración de conexión
DB_NAME = "sakila"
DB_USER = "postgres"
DB_PASSWORD = "password"
DB_HOST = "localhost"
DB_PORT = "5432"

# Ruta a los archivos SQL
SQL_FILES = [
    "postgres-sakila-schema.sql",
    "create-feedback-table.sql",  # Esquema para feedback
    "postgres-sakila-insert-data.sql",  # Usamos el de INSERTS estándar
]

def database_exists(conn, dbname):
    with conn.cursor() as cur:
        cur.execute("SELECT 1 FROM pg_database WHERE datname = %s;", (dbname,))
        return cur.fetchone() is not None

def create_database():
    conn = psycopg2.connect(
        dbname="postgres", user=DB_USER, password=DB_PASSWORD,
        host=DB_HOST, port=DB_PORT
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    with conn.cursor() as cur:
        if database_exists(conn, DB_NAME):
            print(f"La base de datos '{DB_NAME}' ya existe.")
        else:
            cur.execute(f"CREATE DATABASE {DB_NAME};")
            print(f"Base de datos '{DB_NAME}' creada.")
    conn.close()

def execute_sql_scripts():
    conn = psycopg2.connect(
        dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD,
        host=DB_HOST, port=DB_PORT
    )
    conn.autocommit = True
    with conn.cursor() as cur:
        for file in SQL_FILES:
            print(f"Ejecutando script: {file}")
            with open(file, "r", encoding="utf-8") as f:
                sql = f.read()
                cur.execute(sql)
    conn.close()
    print("Esquema y datos cargados correctamente.")

def create_indexes():
    index_statements = [
        "CREATE INDEX IF NOT EXISTS idx_film_title ON film(title);",
        "CREATE INDEX IF NOT EXISTS idx_film_description ON film(description);",
        "CREATE INDEX IF NOT EXISTS idx_film_language_id ON film(language_id);",
        "CREATE INDEX IF NOT EXISTS idx_film_rating ON film(rating);",
        "CREATE INDEX IF NOT EXISTS idx_film_release_year ON film(release_year);",
        "CREATE INDEX IF NOT EXISTS idx_film_fulltext ON film USING GIN (to_tsvector('english', title || ' ' || description));"
    ]
    conn = psycopg2.connect(
        dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD,
        host=DB_HOST, port=DB_PORT
    )
    conn.autocommit = True
    with conn.cursor() as cur:
        print("Creando índices en tabla 'film'...")
        for stmt in index_statements:
            cur.execute(stmt)
    conn.close()
    print("Índices creados correctamente.")

if __name__ == "__main__":
    create_database()
    execute_sql_scripts()
    create_indexes()
