import sqlite3

from lab_3.core.domain.value_objects import CoursId

class SqliteCoursRepository:
    def __init__(self, connection: sqlite3.Connection):
        self._connection = connection

    def exists(self, cours_id: CoursId) -> bool:
        cursor = self._connection.cursor()
        cursor.execute("SELECT 1 FROM COURS WHERE id = ? LIMIT 1", (id.value,))
        return cursor.fetchone() is not None
