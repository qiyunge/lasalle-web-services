"""Programme storage. Reads the programme table only."""

import sqlite3

from college.domain.programme import Programme


class SqliteProgrammeRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def get(self, programme_id: int) -> Programme | None:
        row = self.connection.execute(
            "SELECT id FROM programme WHERE id = ?",
            (programme_id,),
        ).fetchone()
        if row is None:
            return None
        return Programme(row["id"])
