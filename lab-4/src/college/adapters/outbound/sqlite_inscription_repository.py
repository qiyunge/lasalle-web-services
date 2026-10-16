"""Inscription storage. Reads and writes the inscription table only."""

import sqlite3

from college.application.ports import Missing, PersistenceConflict
from college.domain.inscription import Inscription
from college.domain.result import Failure


class SqliteInscriptionRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def find(self, student_id: int, course_id: int):
        row = self.connection.execute(
            """
            SELECT id, student_id, course_id, note
            FROM inscription
            WHERE student_id = ? AND course_id = ?
            """,
            (student_id, course_id),
        ).fetchone()
        if row is None:
            return Failure(Missing())
        return Inscription.create(
            row["id"], row["student_id"], row["course_id"], row["note"]
        )

    def add(self, student_id: int, course_id: int) -> Inscription:
        try:
            cursor = self.connection.execute(
                "INSERT INTO inscription (student_id, course_id, note) VALUES (?, ?, NULL)",
                (student_id, course_id),
            )
        except sqlite3.IntegrityError as error:
            raise PersistenceConflict from error
        return Inscription(cursor.lastrowid, student_id, course_id, None)
