from __future__ import annotations

from dataclasses import dataclass

from lab_3.core.domain.common import (
    Failure,
    Result,
    Success,
    ValidationError,
)


@dataclass(frozen=True, init=False)
class InscriptionId:
    value: int

    @classmethod
    def create(cls, inscription_id: int) -> Result[InscriptionId, ValidationError]:
        if inscription_id <= 0:
            return Failure(
                ValidationError(
                    field="inscription_id",
                    message="Inscription ID must be greater than 0",
                )
            )
        return Success(cls._create(inscription_id))

    @classmethod
    def _create(cls, inscription_id: int) -> InscriptionId:
        obj = object.__new__(cls)
        object.__setattr__(obj, "value", inscription_id)
        return obj
