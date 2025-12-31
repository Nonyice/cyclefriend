import os
import psycopg2
from psycopg2.extras import RealDictCursor

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:Mypostgresdb81@localhost:5432/cycle_tracker"
)

def get_db_connection():
    try:
        conn = psycopg2.connect(
            DATABASE_URL,
            cursor_factory=RealDictCursor
        )
        return conn
    except psycopg2.OperationalError as e:
        print("❌ Database connection failed:", e)
        return None
