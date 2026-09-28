from __future__ import annotations

import sqlite3

from lab_3.core.domain.value_objects import StudentId


class SqliteStudentRepository:
    def __init__(self, connection: sqlite3.Connection):
        self._connection = connection

    def exists(self, student_id: StudentId) -> bool:
        cursor = self._connection.cursor()
        cursor.execute("SELECT 1 FROM STUDENTS WHERE student_id = ? LIMIT 1", (student_id.value,))
        return cursor.fetchone() is not None