from __future__ import annotations

import sqlite3
from lab_3.adapters.outbound.sqlite.unit_of_work import SqliteConnectionProvider
from lab_3.core.domain.value_objects import StudentId
from lab_3.core.application.ports.outbound.student_repository import StudentSaveResult
from lab_3.core.domain.value_objects import StudentName, StudentEmail, ProgrammeId
from lab_3.core.domain.common import Failure, Success
from lab_3.core.domain import Student
from lab_3.core.application.ports.outbound.student_repository import StudentIdConflictError, StudentProgrammeNotFoundError, StudentEmailConflictError
class SqliteStudentRepository:
    def __init__(self, connections: SqliteConnectionProvider) -> None:
        self._connections = connections

    def exists(self, id: StudentId) -> bool:
        cursor = self._connections.execute(
            "SELECT 1 FROM STUDENTS WHERE id = ? LIMIT 1",
            (id.value,),
        )
        return cursor.fetchone() is not None

    def save(self, student: Student) -> StudentSaveResult:
        try:
            self._connections.execute(
                "INSERT INTO STUDENTS (id, name, email, programme_id) VALUES (?, ?, ?, ?)",
                (student.id.value, student.name.value, student.email.value, student.programme_id.value),
            )
            return Success(None)
        except sqlite3.IntegrityError as e:
            message = str(e)
            if "STUDENTS.id" in message:
                return Failure(StudentIdConflictError(student.id))
            elif "STUDENTS.email" in message:
                return Failure(StudentEmailConflictError(student.email))
            elif  "FOREIGN KEY constraint failed" in message:
                return Failure(StudentProgrammeNotFoundError(student.programme_id))
            else:
                raise   # noqa: TRY004
        except Exception as e:
            raise   # noqa: TRY004