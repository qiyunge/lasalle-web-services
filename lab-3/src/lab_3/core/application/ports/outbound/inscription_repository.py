from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from lab_3.core.domain.common import Result
from lab_3.core.domain.inscription import Inscription
from lab_3.core.domain.value_objects import CoursId, InscriptionId, StudentId


# contract for the exception
@dataclass(frozen=True, eq=False)
class InscriptionIdConflict(Exception):
    id: InscriptionId

    def __post_init__(self):
        super().__init__(f"Inscription ID conflict: {self.id.value}")


# contract for the failure result
@dataclass(frozen=True)
class InscriptionDuplicate:
    student_id: StudentId
    cours_id: CoursId


SaveInscriptionError = InscriptionDuplicate


class InscriptionRepository(Protocol):
    def exists(self, student_id: StudentId, cours_id: CoursId) -> bool: ...

    def save(
        self, inscription: Inscription
    ) -> Result[Inscription, SaveInscriptionError]: ...
