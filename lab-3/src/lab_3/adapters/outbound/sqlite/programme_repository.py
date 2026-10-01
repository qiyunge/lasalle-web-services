from .unit_of_work import SqliteConnectionProvider

from lab_3.core.domain.common import Result, Success, Failure
from lab_3.core.domain.programme import Programme
from lab_3.core.domain.value_objects import ProgrammeId, ProgrammeName

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

            programme = Programme.restore(id=id_result.value, name=name_result.value)
            programmes.append(programme)
        
        return programmes