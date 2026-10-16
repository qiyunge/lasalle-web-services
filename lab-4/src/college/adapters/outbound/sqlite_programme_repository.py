"""Programme storage. Reads the programme table only."""

import sqlite3

from college.application.ports import Missing
from college.domain.programme import Programme
from college.domain.result import Failure, Success


class SqliteProgrammeRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def get(self, programme_id: int):
        row = self.connection.execute(
            "SELECT id FROM programme WHERE id = ?",
            (programme_id,),
        ).fetchone()
        if row is None:
            return Failure(Missing())
        return Success(Programme(row["id"]))
