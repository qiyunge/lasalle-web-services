from __future__ import annotations

from dataclasses import dataclass
from lab_3.core.application.command import Command
from lab_3.core.domain.common import Result
from typing import Protocol
from lab_3.core.domain.value_objects import StudentName, StudentEmail, ProgrammeId, StudentId
@dataclass(frozen=True)
class CreateStudentCommand(Command):
    name: StudentName
    email: StudentEmail
    programme_id: ProgrammeId

@dataclass(frozen=True)
class CreateStudentOutcome:
    student_id: StudentId
    name: StudentName
    email: StudentEmail
    programme_id: ProgrammeId

@dataclass(frozen=True)
class StudentEmailAlreadyExists:
    email: StudentEmail

@dataclass(frozen=True)
class ProgrammeNotFound:
    programme_id: ProgrammeId

type CreateStudentError = (
    StudentEmailAlreadyExists | ProgrammeNotFound
)

type CreateStudentResult = Result[CreateStudentOutcome, CreateStudentError]

class CreateStudentUseCase(Protocol):
    def handle(self, command: CreateStudentCommand) -> CreateStudentResult:...