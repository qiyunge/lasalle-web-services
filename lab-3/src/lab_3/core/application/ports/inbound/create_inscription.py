from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from lab_3.core.application.command import Command
from lab_3.core.domain.common import Result
from lab_3.core.domain.common.validation import ValidationErrors
from lab_3.core.domain.value_objects import CoursId, StudentId


@dataclass(frozen=True)
class CreateInscriptionResult:
    id: int
    student_id: int
    cours_id: int
    note: float | None


@dataclass(frozen=True)
class StudentNotFound:
    student_id: StudentId


@dataclass(frozen=True)
class CourseNotFound:
    cours_id: CoursId


@dataclass(frozen=True)
class InscriptionAlreadyExists:
    student_id: StudentId
    cours_id: CoursId


type InscriptionCreationFailed = (
        ValidationErrors | StudentNotFound | CourseNotFound | InscriptionAlreadyExists
    )


CreateInscriptionOutcome = Result[CreateInscriptionResult, InscriptionCreationFailed]


@dataclass(frozen=True)
class CreateInscriptionCommand(Command[CreateInscriptionOutcome]):
    student_id: StudentId
    cours_id: CoursId


class CreateInscritionUseCase(Protocol):
    def handle(self, command: CreateInscriptionCommand) -> CreateInscriptionOutcome: ...
