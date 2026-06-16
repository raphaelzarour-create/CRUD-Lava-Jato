from __future__ import annotations

import os

import pymysql
from pymysql.cursors import DictCursor


DB_HOST = os.getenv("LAVA_JATO_DB_HOST", "127.0.0.1")
DB_PORT = int(os.getenv("LAVA_JATO_DB_PORT", "3306"))
DB_USER = os.getenv("LAVA_JATO_DB_USER", "root")
DB_PASSWORD = os.getenv("LAVA_JATO_DB_PASSWORD", "")
DB_NAME = os.getenv("LAVA_JATO_DB_NAME", "lava_jato")

DatabaseError = pymysql.MySQLError
IntegrityError = pymysql.err.IntegrityError


class Database:
    def __init__(self) -> None:
        self.conn = pymysql.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            charset="utf8mb4",
            cursorclass=DictCursor,
            autocommit=False,
        )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        if exc_type:
            self.conn.rollback()
        else:
            self.conn.commit()
        self.conn.close()

    def execute(self, sql: str, params: tuple | list | None = None):
        cursor = self.conn.cursor()
        cursor.execute(sql.replace("?", "%s"), params)
        return cursor

    def executemany(self, sql: str, params: list[tuple] | tuple[tuple, ...]):
        cursor = self.conn.cursor()
        cursor.executemany(sql.replace("?", "%s"), params)
        return cursor


def get_connection() -> Database:
    return Database()


def row_to_dict(row: dict | None) -> dict | None:
    if row is None:
        return None
    return dict(row)


def rows_to_dicts(rows: list[dict]) -> list[dict]:
    return [dict(row) for row in rows]
