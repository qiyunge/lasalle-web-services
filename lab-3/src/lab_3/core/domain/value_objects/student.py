from __future__ import annotations
from dataclasses import dataclass

from lab_3.core.domain.common import Result, Success, Failure, ValidationErrors, ValidationError

@dataclass(frozen=True, slots=True, init=False)
class StudentId:
    value: int

    @classmethod
    def create(cls, student_id: int) -> Result[StudentId, ValidationError]:
        if student_id <= 0:
            return Failure(ValidationError(field="student_id", message="Student ID must be greater than 0"))
        return Success(cls._create(student_id))

    @classmethod
    def _create(cls, student_id: int) -> StudentId:
        obj = object.__new__(cls)
        object.__setattr__(obj, "value", student_id)
        return obj

@dataclass(frozen=True, slots=True, init=False)
class StudentName:
    value: str

    @classmethod
    def create(cls, student_name: str) -> Result[StudentName, ValidationError]:
        if not student_name.strip():
            return Failure(ValidationError(field="student_name", message="Student name is required"))
        return Success(cls._create(student_name.strip()))

    @classmethod
    def _create(cls, student_name: str) -> StudentName:
        obj = object.__new__(cls)   
        object.__setattr__(obj, "value", student_name)
        return obj

@dataclass(frozen=True, slots=True, init=False)
class StudentEmail:
    value: str

    @classmethod
    def create(cls, student_email: str) -> Result[StudentEmail, ValidationError]:
        if not student_email.strip():
            return Failure(ValidationError(field="student_email", message="Student email is required"))
        return Success(cls._create(student_email.strip()))  

    @classmethod
    def _create(cls, student_email: str) -> StudentEmail:
        obj = object.__new__(cls)
        object.__setattr__(obj, "value", student_email)
        return obj
