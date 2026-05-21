"""
Módulo de conexión a PostgreSQL.
Proyecto Final - Base de Datos I
"""
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host":     os.getenv("DB_HOST", "localhost"),
    "port":     int(os.getenv("DB_PORT", "5432")),
    "dbname":   os.getenv("DB_NAME", "tarjetas_circulacion"),
    "user":     os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "postgres"),
}


def get_connection():
    """Crea y devuelve una nueva conexión a PostgreSQL."""
    return psycopg2.connect(**DB_CONFIG)


def query_all(sql, params=None):
    """Ejecuta SELECT y devuelve una lista de dicts."""
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, params or ())
            rows = cur.fetchall()
            return [dict(r) for r in rows]
    finally:
        conn.close()


def query_one(sql, params=None):
    """Ejecuta SELECT y devuelve un único dict (o None)."""
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, params or ())
            row = cur.fetchone()
            return dict(row) if row else None
    finally:
        conn.close()


def execute(sql, params=None, returning=False):
    """Ejecuta INSERT/UPDATE/DELETE. Si returning=True devuelve la fila."""
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, params or ())
            result = None
            if returning:
                row = cur.fetchone()
                result = dict(row) if row else None
        conn.commit()
        return result
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def execute_many(operations):
    """
    Ejecuta varias operaciones en una sola transacción.
    operations es lista de tuplas (sql, params).
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            for sql, params in operations:
                cur.execute(sql, params or ())
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
