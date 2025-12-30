import psycopg2
import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:password@localhost:5432/cycle_tracker"
)

def get_db():
    try:
        return psycopg2.connect(DATABASE_URL)
    except Exception as e:
        print("❌ Database connection failed:", e)
        return None
