from __future__ import annotations

from typing import Protocol

from dataclasses import dataclass
from lab_3.core.domain.value_objects import StudentId, StudentEmail, ProgrammeId, StudentName
from lab_3.core.domain.common import Result
from lab_3.core.domain import Student

@dataclass(frozen=True)
class StudentEmailConflictPersistenceError:
    email: StudentEmail

@dataclass(frozen=True)
class StudentIdConflictPersistenceError:
    id: StudentId

@dataclass(frozen=True)
class StudentProgrammeNotFoundPersistenceError:
    programme_id: ProgrammeId

type StudentSaveError = StudentEmailConflictPersistenceError | StudentIdConflictPersistenceError | StudentProgrammeNotFoundPersistenceError
type StudentSavePersistenceResult = Result[None, StudentSaveError]

## delete
@dataclass(frozen=True)
class StudentNotFoundPersistenceError:
    id: StudentId
@dataclass(frozen=True)
class StudentReferencedPersistenceError:
    id: StudentId

type DeleteStudentError = StudentNotFoundPersistenceError | StudentReferencedPersistenceError
type DeleteStudentPersistenceResult = Result[None, DeleteStudentError]


## get  

type GetStudentError = StudentNotFoundPersistenceError | StudentReferencedPersistenceError
type GetStudentPersistenceResult = Result[Student, GetStudentError]

class StudentRepository(Protocol):
    def exists(self, id: StudentId) -> bool: ...

    def save(self, student: Student) -> StudentSavePersistenceResult: ...

    def delete(self, id: StudentId) -> DeleteStudentPersistenceResult: ...

    def get(self, id: StudentId) -> GetStudentPersistenceResult: ...
