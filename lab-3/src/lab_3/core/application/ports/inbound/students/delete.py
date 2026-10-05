from dataclasses import dataclass
from lab_3.core.domain.value_objects import StudentId
from lab_3.core.domain.common import Result
from lab_3.core.application.command import Command
from typing import Protocol

@dataclass(frozen=True)
class DeleteStudentCommand(Command):
    student_id: StudentId

@dataclass(frozen=True)
class DeleteStudentOutcome:
    student_id: StudentId

@dataclass(frozen=True)
class StudentNotFound:
    student_id: StudentId

@dataclass(frozen=True)
class StudentHasInscriptions:
    student_id: StudentId
type DeleteStudentError = StudentNotFound | StudentHasInscriptions

type DeleteStudentResult = Result[DeleteStudentOutcome, DeleteStudentError]

class DeleteStudentUseCase(Protocol):
    def handle(self, command: DeleteStudentCommand) -> DeleteStudentResult:
        ...