from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import pymysql
from pymysql.cursors import DictCursor


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATABASE_DIR = PROJECT_ROOT / "database"
SCHEMA_PATH = DATABASE_DIR / "schema.sql"

DB_HOST = os.getenv("LAVA_JATO_DB_HOST", "127.0.0.1")
DB_PORT = int(os.getenv("LAVA_JATO_DB_PORT", "3306"))
DB_USER = os.getenv("LAVA_JATO_DB_USER", "root")
DB_PASSWORD = os.getenv("LAVA_JATO_DB_PASSWORD", "")
DB_NAME = os.getenv("LAVA_JATO_DB_NAME", "lava_jato")
DB_CHARSET = "utf8mb4"

DatabaseError = pymysql.MySQLError
IntegrityError = pymysql.err.IntegrityError


class DatabaseConnection:
    def __init__(self) -> None:
        self._conn = pymysql.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            charset=DB_CHARSET,
            cursorclass=DictCursor,
            autocommit=False,
        )

    def __enter__(self) -> "DatabaseConnection":
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        if exc_type is None:
            self._conn.commit()
        else:
            self._conn.rollback()
        self._conn.close()

    def execute(self, query: str, params: tuple | list | None = None):
        cursor = self._conn.cursor()
        cursor.execute(_convert_placeholders(query), params)
        return cursor

    def executemany(self, query: str, params: list[tuple] | tuple[tuple, ...]):
        cursor = self._conn.cursor()
        cursor.executemany(_convert_placeholders(query), params)
        return cursor


def _admin_connection():
    return pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        charset=DB_CHARSET,
        cursorclass=DictCursor,
        autocommit=True,
    )


def _convert_placeholders(query: str) -> str:
    return query.replace("?", "%s")


def _schema_statements(schema: str) -> list[str]:
    return [statement.strip() for statement in schema.split(";") if statement.strip()]


def _quoted_database_name() -> str:
    return f"`{DB_NAME.replace('`', '``')}`"


def create_database_if_needed() -> None:
    try:
        with _admin_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    f"CREATE DATABASE IF NOT EXISTS {_quoted_database_name()} "
                    f"CHARACTER SET {DB_CHARSET} COLLATE utf8mb4_unicode_ci"
                )
    except pymysql.MySQLError as exc:
        raise RuntimeError(
            "Nao foi possivel conectar ao MySQL/MariaDB do XAMPP. "
            "Abra o XAMPP Control Panel, inicie o MySQL e confira host, porta, "
            "usuario e senha no README."
        ) from exc


def get_connection() -> DatabaseConnection:
    create_database_if_needed()
    return DatabaseConnection()


def initialize_database() -> None:
    if not SCHEMA_PATH.exists():
        raise FileNotFoundError(f"Arquivo de schema nao encontrado: {SCHEMA_PATH}")

    create_database_if_needed()
    with get_connection() as conn:
        for statement in _schema_statements(SCHEMA_PATH.read_text(encoding="utf-8")):
            conn.execute(statement)


def reset_database() -> None:
    try:
        with _admin_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(f"DROP DATABASE IF EXISTS {_quoted_database_name()}")
    except pymysql.MySQLError as exc:
        raise RuntimeError(
            "Nao foi possivel recriar o banco no MySQL/MariaDB do XAMPP. "
            "Verifique se o MySQL esta iniciado."
        ) from exc
    initialize_database()


def row_to_dict(row: dict[str, Any] | None) -> dict | None:
    if row is None:
        return None
    return dict(row)


def rows_to_dicts(rows: list[dict[str, Any]]) -> list[dict]:
    return [dict(row) for row in rows]
