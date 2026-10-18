"""Programme storage. Reads the programme table only."""

import sqlite3

from college.application.ports import Missing
from college.domain.identifiers import ProgrammeId
from college.domain.programme import InvalidProgramme, Programme
from college.domain.result import Failure, Success


class SqliteProgrammeRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def get(
        self, programme_id: ProgrammeId
    ) -> Success[Programme] | Failure[Missing | InvalidProgramme]:
        row = self.connection.execute(
            "SELECT id, name FROM programme WHERE id = ?",
            (programme_id.value,),
        ).fetchone()
        if row is None:
            return Failure(Missing())
        return Programme.reconstitute(programme_id, row["name"])
