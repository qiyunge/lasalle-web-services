from __future__ import annotations

import sqlite3
from contextvars import ContextVar, Token
from typing import Self

from lab_3.adapters.outbound.sqlite.connection import SqliteConnectionFactory
from lab_3.core.application.ports.outbound.unit_of_work import (
    TransactionRestartRequired,
)

_current: ContextVar[sqlite3.Connection | None] = ContextVar(
    "sqlite_connection", default=None
)
_token: ContextVar[Token[sqlite3.Connection | None] | None] = ContextVar(
    "sqlite_connection_token",
    default=None,
)
_LOCK_ERRORS = (sqlite3.SQLITE_BUSY, sqlite3.SQLITE_LOCKED)


def _require_connection() -> sqlite3.Connection:
    connection = _current.get()
    if connection is None:
        raise RuntimeError("No active unit of work")
    return connection


def _reraise_lock(error: sqlite3.OperationalError) -> None:
    if getattr(error, "sqlite_errorcode", None) in _LOCK_ERRORS:
        raise TransactionRestartRequired from error
    raise error


class SqliteConnectionProvider:
    def current(self) -> sqlite3.Connection:
        return _require_connection()

    def execute(self, sql: str, parameters: tuple[object, ...] = ()) -> sqlite3.Cursor:
        cursor = self.current().cursor()
        try:
            cursor.execute(sql, parameters)
        except sqlite3.OperationalError as error:
            _reraise_lock(error)
        return cursor


class SqliteUnitOfWork:
    def __init__(self, connection_factory: SqliteConnectionFactory) -> None:
        self._connection_factory = connection_factory

    def __enter__(self) -> Self:
        if _current.get() is not None:
            raise RuntimeError("Nested unit of work is not supported")

        connection = self._connection_factory.create_connection()
        connection.isolation_level = None
        try:
            connection.execute("BEGIN")
        except sqlite3.OperationalError as error:
            connection.close()
            _reraise_lock(error)
        except Exception:
            connection.close()
            raise
        _token.set(_current.set(connection))
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        connection = _current.get()
        token = _token.get()
        try:
            if connection is not None and connection.in_transaction:
                connection.rollback()
        finally:
            if token is not None:
                _current.reset(token)
                _token.set(None)
            if connection is not None:
                connection.close()

    def commit(self) -> None:
        connection = _require_connection()
        if not connection.in_transaction:
            raise RuntimeError("No active transaction")
        try:
            connection.commit()
        except sqlite3.OperationalError as error:
            _reraise_lock(error)
