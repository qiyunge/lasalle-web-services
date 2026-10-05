from dataclasses import dataclass
from lab_3.core.domain.value_objects import StudentId, StudentName, StudentEmail, ProgrammeId
from lab_3.core.domain.common import Result
from lab_3.core.application.command import Command
from typing import Protocol

@dataclass(frozen=True)
class GetStudentCommand(Command):
    student_id: StudentId

@dataclass(frozen=True)
class GetStudentOutcome:
    student_id: StudentId
    name: StudentName
    email: StudentEmail
    programme_id: ProgrammeId

@dataclass(frozen=True)
class StudentNotFound:
    student_id: StudentId

type GetStudentError = StudentNotFound
type GetStudentResult = Result[GetStudentOutcome, GetStudentError]


class GetStudentUseCase(Protocol):
    def handle(self, command: GetStudentCommand) -> GetStudentResult: ...