from __future__ import annotations
from dataclasses import dataclass

from lab_3.core.domain.common import Result, Success, Failure
from lab_3.core.domain.common.validation import ValidationError, ValidationErrors
from lab_3.core.domain.value_objects import StudentId, CoursId, InscriptionId, Note

@dataclass(frozen=True, slots=True, init=False)
class Inscription:
    id:InscriptionId|None
    student_id: StudentId
    cours_id: CoursId
    note: Note|None

    @classmethod
    def create(cls, 
               student_id:StudentId,
               cours_id:CoursId,
               note:Note|None=None
              
    ) -> Inscription:
        obj = object.__new__(cls)
        object.__setattr__(obj, "student_id", student_id)
        object.__setattr__(obj, "cours_id", cours_id)
        object.__setattr__(obj, "note", note)
        return obj

    @classmethod
    def restore(cls, 
                id:InscriptionId,
                student_id:StudentId,
                cours_id:CoursId,
                note:Note|None=None
    ) -> Inscription:
        obj = object.__new__(cls)
        object.__setattr__(obj, "id", id)
        object.__setattr__(obj, "student_id", student_id)
        object.__setattr__(obj, "cours_id", cours_id)
        object.__setattr__(obj, "note", note)
        return obj

    def assign_note(self, note:Note) -> Inscription:
        object.__setattr__(self, "note", note)
        return self 