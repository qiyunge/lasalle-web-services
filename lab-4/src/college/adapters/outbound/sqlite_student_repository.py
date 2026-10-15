"""Student storage. Reads the student table only."""

import sqlite3

from college.domain.student import Student


class SqliteStudentRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def get(self, student_id: int) -> Student | None:
        row = self.connection.execute(
            "SELECT id, name, email, programme_id FROM student WHERE id = ?",
            (student_id,),
        ).fetchone()
        if row is None:
            return None
        return Student(row["id"], row["name"], row["email"], row["programme_id"])
