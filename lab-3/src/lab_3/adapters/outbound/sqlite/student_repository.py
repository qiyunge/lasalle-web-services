from __future__ import annotations

import sqlite3
from lab_3.adapters.outbound.sqlite.unit_of_work import SqliteConnectionProvider
from lab_3.core.domain.value_objects import StudentId
from lab_3.core.application.ports.outbound.student_repository import StudentSavePersistenceResult, DeleteStudentPersistenceResult, GetStudentPersistenceResult
from lab_3.core.domain.value_objects import StudentName, StudentEmail, ProgrammeId
from lab_3.core.domain.common import Failure, Success, collect_errors
from lab_3.core.domain import Student
from lab_3.core.application.ports.outbound.student_repository import (
    StudentIdConflictPersistenceError, 
    StudentProgrammeNotFoundPersistenceError, 
    StudentEmailConflictPersistenceError, 
    StudentNotFoundPersistenceError,
    StudentReferencedPersistenceError,
)
class SqliteStudentRepository:
    def __init__(self, connections: SqliteConnectionProvider) -> None:
        self._connections = connections

    def exists(self, id: StudentId) -> bool:
        cursor = self._connections.execute(
            "SELECT 1 FROM STUDENTS WHERE id = ? LIMIT 1",
            (id.value,),
        )
        return cursor.fetchone() is not None

    def save(self, student: Student) -> StudentSavePersistenceResult:
        try:
            self._connections.execute(
                "INSERT INTO STUDENTS (id, name, email, programme_id) VALUES (?, ?, ?, ?)",
                (student.id.value, student.name.value, student.email.value, student.programme_id.value),
            )
            return Success(None)
        except sqlite3.IntegrityError as e:
            message = str(e)
            if "STUDENTS.id" in message:
                return Failure(StudentIdConflictPersistenceError(student.id))
            elif "STUDENTS.email" in message:
                return Failure(StudentEmailConflictPersistenceError(student.email))
            elif  "FOREIGN KEY constraint failed" in message:
                return Failure(StudentProgrammeNotFoundPersistenceError(student.programme_id))
            else:
                raise   # noqa: TRY004
        except Exception as e:
            raise   # noqa: TRY004

    def delete(self, id: StudentId) -> DeleteStudentPersistenceResult:
        try:
            self._connections.execute(
                "DELETE FROM STUDENTS WHERE id = ?",
                (id.value,),
            )
            return Success(None)
        except sqlite3.IntegrityError as e:
            message = str(e)
            if "STUDENTS.id" in message:
                return Failure(StudentNotFoundPersistenceError(id))
            elif "FOREIGN KEY constraint failed" in message:
                return Failure(StudentReferencedPersistenceError(id))
            else:
                raise   # noqa: TRY004
        except Exception as e:
            raise   # noqa: TRY004

    def get(self, id: StudentId) -> GetStudentPersistenceResult:
        try:
            cursor = self._connections.execute(
                "SELECT id, name, email, programme_id FROM STUDENTS WHERE id = ?",
                (id.value,),
            )
            result = cursor.fetchone()
            if result is None:
                return Failure(StudentNotFoundPersistenceError(id))
            
            student_id_result = StudentId.create(result["id"])
            student_name_result = StudentName.create(result["name"])
            student_email_result = StudentEmail.create(result["email"])
            programme_id_result = ProgrammeId.create(result["programme_id"])
            errors = collect_errors(student_id_result, student_name_result, student_email_result, programme_id_result)
            if errors:
                raise RuntimeError("Invalid student data in persistence")
            
            return Success(Student.restore(student_id_result.outcome, student_name_result.outcome, student_email_result.outcome, programme_id_result.outcome))
        except Exception as e:
            raise   # noqa: TRY004