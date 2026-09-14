from pathlib import Path
import os

import psycopg
from dotenv import load_dotenv
from psycopg import Connection


BASE_DIR = Path(__file__).resolve().parent
SCHEMA_PATH = BASE_DIR / "schema.sql"

load_dotenv(BASE_DIR.parent / ".env")


def get_database_url() -> str:
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL is required to connect to PostgreSQL.")
    return database_url


def get_connection() -> Connection:
    return psycopg.connect(get_database_url())


def init_database() -> None:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(SCHEMA_PATH.read_text(encoding="utf-8"))
