from __future__ import annotations
from dataclasses import dataclass

from lab_3.core.domain.common import Result, Success, Failure, ValidationErrors, ValidationError

@dataclass(frozen=True, slots=True, init=False)
class ProgrammeId:
    value: int

    @classmethod
    def create(cls, programme_id: int) -> Result[ProgrammeId, ValidationError]:
        if programme_id <= 0:
            return Failure(ValidationError(field="programme_id", message="Programme ID must be greater than 0"))
        return Success(cls._create(programme_id))  

    @classmethod
    def _create(cls, programme_id: int) -> ProgrammeId:
        obj = object.__new__(cls)
        object.__setattr__(obj, "value", programme_id)
        return obj

@dataclass(frozen=True, slots=True, init=False)
class ProgrammeName:
    value: str

    @classmethod
    def create(cls, programme_name: str) -> Result[ProgrammeName, ValidationError]:
        if not programme_name.strip():
            return Failure(ValidationError(field="programme_name", message="Programme name is required"))
        return Success(cls._create(programme_name.strip()))

    @classmethod
    def _create(cls, programme_name: str) -> ProgrammeName:
        obj = object.__new__(cls)
        object.__setattr__(obj, "value", programme_name)
        return obj
            