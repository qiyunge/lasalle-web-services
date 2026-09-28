import sqlite3

from lab_3.core.domain.value_objects import CoursId
from lab_3.adapters.outbound.sqlite.connection import SqliteConnectionFactory

class SqliteCoursRepository:
    def __init__(self, connection_factory: SqliteConnectionFactory):
        self._connection_factory = connection_factory

    def exists(self, cours_id: CoursId) -> bool:
        connection = self._connection_factory.create_connection()
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT 1 FROM COURS WHERE id = ? LIMIT 1", (cours_id.value,))
            return cursor.fetchone() is not None
        finally:
            connection.close()
