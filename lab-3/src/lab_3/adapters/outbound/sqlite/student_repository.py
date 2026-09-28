from __future__ import annotations

import sqlite3

from lab_3.core.domain.value_objects import StudentId
from lab_3.adapters.outbound.sqlite.connection import SqliteConnectionFactory

class SqliteStudentRepository:
    def __init__(self, connection_factory: SqliteConnectionFactory):
        self._connection_factory = connection_factory

    def exists(self, student_id: StudentId) -> bool:
        connection = self._connection_factory.create_connection()
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT 1 FROM STUDENTS WHERE id = ? LIMIT 1", (student_id.value,))
            return cursor.fetchone() is not None
        finally:
            connection.close()
        