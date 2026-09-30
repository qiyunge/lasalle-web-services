from __future__ import annotations

from lab_3.adapters.outbound.sqlite.unit_of_work import SqliteConnectionProvider
from lab_3.core.domain.value_objects import StudentId


class SqliteStudentRepository:
    def __init__(self, connections: SqliteConnectionProvider) -> None:
        self._connections = connections

    def exists(self, id: StudentId) -> bool:
        cursor = self._connections.execute(
            "SELECT 1 FROM STUDENTS WHERE id = ? LIMIT 1",
            (id.value,),
        )
        return cursor.fetchone() is not None
