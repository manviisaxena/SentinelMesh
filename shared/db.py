import os, time
import psycopg
from psycopg.rows import dict_row

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://sentinel:change-me-local@localhost:5432/sentinel")

def connect(retries=30):
    last = None
    for _ in range(retries):
        try:
            if os.getenv("DATABASE_URL"):
                return psycopg.connect(os.environ["DATABASE_URL"], row_factory=dict_row)
            return psycopg.connect(host=os.getenv("PGHOST", "localhost"),
                dbname=os.getenv("PGDATABASE", "sentinel"), user=os.getenv("PGUSER", "sentinel"),
                password=os.getenv("PGPASSWORD", "change-me-local"), row_factory=dict_row)
        except Exception as exc:
            last = exc
            time.sleep(2)
    raise RuntimeError(f"Database unavailable after {retries} attempts: {last}")

def init_db(statements):
    with connect() as conn:
        with conn.cursor() as cur:
            for statement in statements:
                cur.execute(statement)
        conn.commit()

def fetch_all(query, params=()):
    with connect() as conn, conn.cursor() as cur:
        cur.execute(query, params)
        return cur.fetchall()

def fetch_one(query, params=()):
    with connect() as conn, conn.cursor() as cur:
        cur.execute(query, params)
        return cur.fetchone()

def execute(query, params=(), returning=False):
    with connect() as conn, conn.cursor() as cur:
        cur.execute(query, params)
        row = cur.fetchone() if returning else None
        conn.commit()
        return row
