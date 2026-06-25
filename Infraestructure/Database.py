import os
from pathlib import Path
from typing import Any, Optional, Sequence

import psycopg2
from dotenv import load_dotenv
from psycopg2 import Error

from Infraestructure.exceptions import ConfigurationError

# Carga .env desde la raíz del repo aunque uvicorn se ejecute desde otro cwd
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(_PROJECT_ROOT / ".env", override=True)


def get_db_connection():
    """Conecta por DB_* (recomendado con Supabase) o por DATABASE_URL."""
    host = os.getenv("DB_HOST")
    password = os.getenv("DB_PASSWORD")
    if host and password:
        try:
            ct = os.getenv("DB_CONNECT_TIMEOUT_SEC", "3")
            try:
                connect_timeout = max(1, int(ct))
            except ValueError:
                connect_timeout = 3
            return psycopg2.connect(
                host=host,
                port=int(os.getenv("DB_PORT", "5432")),
                user=os.getenv("DB_USER", "postgres"),
                password=password,
                dbname=os.getenv("DB_NAME", "postgres"),
                sslmode=os.getenv("DB_SSLMODE", "require"),
                connect_timeout=connect_timeout,
            )
        except Error as e:
            print(f"Error: {e}")
            raise

    url = os.getenv("DATABASE_URL")
    if not url or not url.strip():
        raise ConfigurationError(
            "Define DB_HOST y DB_PASSWORD, o DATABASE_URL, en el entorno (.env)"
        )
    try:
        ct = os.getenv("DB_CONNECT_TIMEOUT_SEC", "3")
        try:
            connect_timeout = max(1, int(ct))
        except ValueError:
            connect_timeout = 3
        db = psycopg2.connect(url, connect_timeout=connect_timeout)
        return db
    except Error as e:
        print(f"Error: {e}")
        raise


def call_pg_function(
    cursor, function_name: str, parameters: Optional[Sequence[Any]] = None
) -> None:
    """Llama a una función en schema public con el nombre entre comillas (mayúsculas como en Supabase).

    psycopg2.callproc genera identificadores sin comillas y PostgreSQL los pasa a minúsculas,
    por eso no encuentra funciones creadas como \"CrearRestaurante\".
    """
    params = tuple(parameters) if parameters is not None else ()
    if len(params) == 0:
        cursor.execute(f'SELECT * FROM public."{function_name}"()')
    else:
        placeholders = ", ".join(["%s"] * len(params))
        cursor.execute(
            f'SELECT * FROM public."{function_name}"({placeholders})',
            params,
        )


def check_db_connection():
    connection = get_db_connection()
    cursor = None
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchall()
        print("La conexión a la base de datos está activa y funcionando correctamente.")
    except Error as e:
        print(f" Error al verificar la conexión: {e}")
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and not connection.closed:
            connection.close()
            print(" Conexión cerrada.")


def ping_db() -> bool:
    """SELECT 1 con conexión corta; para /health."""
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT 1")
        cur.fetchone()
        return True
    except Exception:
        return False
    finally:
        if cur is not None:
            cur.close()
        if conn is not None and not conn.closed:
            conn.close()


if os.getenv("CHECK_DB_ON_IMPORT") == "1":
    check_db_connection()
