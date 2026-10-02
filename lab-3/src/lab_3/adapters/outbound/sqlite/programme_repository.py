import sqlite3
from .unit_of_work import SqliteConnectionProvider

from lab_3.core.domain.common import Result, Success, Failure
from lab_3.core.domain.programme import Programme
from lab_3.core.domain.value_objects import ProgrammeId, ProgrammeName
from lab_3.core.application.ports.outbound.programme_repository import ProgrammeIdConflictException, ProgrammeNameConflictException

class SqliteProgrammeRepository:
    def __init__(self, connections: SqliteConnectionProvider) -> None:
        self._connections = connections

    def find_all(self) -> list[Programme]:
        cursor = self._connections.execute("SELECT id, name FROM PROGRAMMES")
        
        rows = cursor.fetchall()

        programmes = []
        for row in rows:
            id_result = ProgrammeId.create(row["id"])
            name_result = ProgrammeName.create(row["name"])

            assert isinstance(id_result, Success) and isinstance(name_result, Success)

            programme = Programme.restore(id=id_result.outcome, name=name_result.outcome)
            programmes.append(programme)
        
        return programmes

    def save(self, programme: Programme) -> None:
        try:
            cursor = self._connections.execute("INSERT INTO PROGRAMMES (id, name) VALUES (?, ?)", (programme.id.value, programme.name.value))
        except sqlite3.IntegrityError as e:
            if e.sqlite_error_code == sqlite3.SQLITE_CONSTRAINT_UNIQUE:
                raise ProgrammeNameConflictException(programme.name) from e 
            elif e.sqlite_error_code in (sqlite3.SQLITE_CONSTRAINT_PRIMARYKEY, sqlite3.SQLITE_CONSTRAINT_ROWID,):
                raise ProgrammeIdConflictException(programme.id) from e
            else:
                raise
