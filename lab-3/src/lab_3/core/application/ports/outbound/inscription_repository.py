from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from lab_3.core.domain.common import Result, Success, Failure
from lab_3.core.domain.inscription import Inscription
from lab_3.core.domain.value_objects import StudentId, CoursId

@dataclass(frozen=True)
class InscriptionConflict:
    pass


SaveInscriptionError = (
    InscriptionConflict
   
)

class InscriptionRepository(Protocol):
    def exists(self, student_id:StudentId, cours_id:CoursId) -> bool:
        ...

    def save(self, inscription: Inscription) -> Result[Inscription, InscriptionConflict]:...

    
