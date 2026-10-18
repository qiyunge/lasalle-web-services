"""SQLite connection, schema, and transaction boundary. Decides no enrollment."""

import sqlite3

SCHEMA = """
CREATE TABLE IF NOT EXISTS programme (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS student (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    programme_id INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS course (
    id INTEGER PRIMARY KEY,
    course_code TEXT NOT NULL,
    name TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS inscription (
    id INTEGER PRIMARY KEY,
    student_id INTEGER NOT NULL,
    course_id INTEGER NOT NULL,
    note TEXT,
    UNIQUE (student_id, course_id)
);
"""


def open_connection(database: str) -> sqlite3.Connection:
    connection = sqlite3.connect(database, timeout=5.0, isolation_level=None)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_schema(connection: sqlite3.Connection) -> None:
    connection.executescript(SCHEMA)


class SqliteUnitOfWork:
    """One BEGIN IMMEDIATE transaction per block."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection
        self._rollback = False

    def rollback(self) -> None:
        self._rollback = True

    def __enter__(self) -> "SqliteUnitOfWork":
        self._rollback = False
        self.connection.execute("BEGIN IMMEDIATE")
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        if exc_type is None and not self._rollback:
            self.connection.commit()
        else:
            self.connection.rollback()
        return False
