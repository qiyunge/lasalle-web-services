from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol

from lab_3.core.domain.common.validation import ValidationErrors
from lab_3.core.domain.common import Result


@dataclass(frozen=True)
class CreateInscriptionCommand:
    student_id: int
    course_id: int

@dataclass(frozen=True)
class CreateInscriptionResult:
    id:int
    student_id: int
    course_id: int
    note: float|None    

@dataclass(frozen=True)
class StudentNotFound:
    student_id: int

@dataclass(frozen=True)
class CourseNotFound:
    course_id: int

@dataclass(frozen=True)
class InscriptionAlreadyExists:
    student_id: int
    course_id: int

@dataclass(frozen=True)
class InscriptionCreationFailed:
    errors: ValidationErrors | StudentNotFound | CourseNotFound | InscriptionAlreadyExists

class CreateInscritionUseCase(Protocol):
    def handle(self, command: CreateInscriptionCommand) -> Result[CreateInscriptionResult, InscriptionCreationFailed]:
        ...