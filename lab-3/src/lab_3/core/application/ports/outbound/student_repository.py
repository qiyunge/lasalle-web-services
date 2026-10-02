from __future__ import annotations

from typing import Protocol

from dataclasses import dataclass
from lab_3.core.domain.value_objects import StudentId, StudentName, StudentEmail, ProgrammeId
from lab_3.core.domain.common import Result
from lab_3.core.domain import Student
@dataclass(frozen=True)
class StudentEmailConflictError:
    email: StudentEmail

@dataclass(frozen=True)
class StudentIdConflictError:
    id: StudentId

@dataclass(frozen=True)
class StudentProgrammeNotFoundError:
    programme_id: ProgrammeId

type StudentSaveError = StudentEmailConflictError | StudentIdConflictError | StudentProgrammeNotFoundError
type StudentSaveResult = Result[None, StudentSaveError]


class StudentRepository(Protocol):
    def exists(self, id: StudentId) -> bool: ...

    def save(self, student: Student) -> StudentSaveResult: ...
