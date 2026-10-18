"""Inscription storage. Reads and writes the inscription table only."""

import sqlite3
from typing import cast

from college.application.ports import Missing, PersistenceConflict
from college.domain.identifiers import CourseId, InscriptionId, StudentId
from college.domain.inscription import Inscription, InvalidInscription, NewInscription
from college.domain.result import Failure, Success


class SqliteInscriptionRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def find(
        self, student_id: StudentId, course_id: CourseId
    ) -> Success[Inscription] | Failure[Missing | InvalidInscription]:
        row = self.connection.execute(
            "SELECT id, note FROM inscription WHERE student_id = ? AND course_id = ?",
            (student_id.value, course_id.value),
        ).fetchone()
        if row is None:
            return Failure(Missing())
        # id is an INTEGER PRIMARY KEY, so SQLite always stores an integer.
        return Inscription.reconstitute(InscriptionId(row["id"]), student_id, course_id, row["note"])

    def add(self, inscription: NewInscription) -> Inscription:
        try:
            cursor = self.connection.execute(
                "INSERT INTO inscription (student_id, course_id, note) VALUES (?, ?, NULL)",
                (inscription.student_id.value, inscription.course_id.value),
            )
        except sqlite3.IntegrityError as error:
            raise PersistenceConflict from error
        return inscription.stored_as(InscriptionId(cast(int, cursor.lastrowid)))
