from __future__ import annotations

from dataclasses import dataclass

from lab_3.core.domain.common import (
    Failure,
    Result,
    Success,
    ValidationError,
)


@dataclass(frozen=True, slots=True, init=False)
class Note:
    value: float

    @classmethod
    def create(cls, note: float) -> Result[Note, ValidationError]:
        if not note:
            return Failure(ValidationError(field="note", message="Note is required"))
        if note < 0 or note > 100:
            return Failure(
                ValidationError(field="note", message="Note must be between 0 and 100")
            )
        return Success(cls._create(note))

    @classmethod
    def _create(cls, note: float) -> Note:
        obj = object.__new__(cls)
        object.__setattr__(obj, "value", note)
        return obj
