from __future__ import annotations
from dataclasses import dataclass

from lab_3.core.domain.common import Result, Success, Failure, ValidationErrors, ValidationError

@dataclass(frozen=True, slots=True, init=False)
class CoursId:
    value: int

    @classmethod
    def create(cls, cours_id: int) -> Result[CoursId, ValidationError]:
        if cours_id <= 0:
            return Failure(ValidationError(field="cours_id", message="Cours ID must be greater than 0"))
        return Success(cls._create(cours_id))

    @classmethod
    def _create(cls, cours_id: int) -> CoursId:    
        obj = object.__new__(cls)
        object.__setattr__(obj, "value", cours_id)
        return obj

@dataclass(frozen=True, slots=True, init=False)
class CoursCode:
    value: str

    @classmethod
    def create(cls, cours_code: str) -> Result[CoursCode, ValidationError]:
        if not cours_code.strip():
            return Failure(ValidationError(field="cours_code", message="Cours code is required"))
        return Success(cls._create(cours_code.strip()))

    @classmethod
    def _create(cls, cours_code: str) -> CoursCode:
        obj = object.__new__(cls)
        object.__setattr__(obj, "value", cours_code)
        return obj

@dataclass(frozen=True, init=False)
class CoursName:
    value: str

    @classmethod
    def create(cls, cours_name: str) -> Result[CoursName, ValidationError]:
        if not cours_name.strip():
            return Failure(ValidationError(field="cours_name", message="Cours name is required"))
        return Success(cls._create(cours_name.strip()))

    @classmethod
    def _create(cls, cours_name: str) -> CoursName:
        obj = object.__new__(cls)
        object.__setattr__(obj, "value", cours_name)
        return obj