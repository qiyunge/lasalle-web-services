"""Student storage. Reads the student table only."""

import sqlite3

from college.application.ports import Missing
from college.domain.email import Email
from college.domain.identifiers import ProgrammeId, StudentId
from college.domain.result import Failure, Success
from college.domain.student import InvalidStudent, Student


class SqliteStudentRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def get(self, student_id: StudentId) -> Success[Student] | Failure[Missing | InvalidStudent]:
        row = self.connection.execute(
            "SELECT id, name, email, programme_id FROM student WHERE id = ?",
            (student_id.value,),
        ).fetchone()
        if row is None:
            return Failure(Missing())
        email = Email.create(row["email"])
        programme_id = ProgrammeId.create(row["programme_id"])
        if not (isinstance(email, Success) and isinstance(programme_id, Success)):
            return Failure(InvalidStudent(student_id.value))
        return Student.reconstitute(student_id, row["name"], email.value, programme_id.value)
