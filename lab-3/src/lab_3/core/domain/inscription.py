from __future__ import annotations

from dataclasses import dataclass

from lab_3.core.domain.common.build import build, set_attributes
from lab_3.core.domain.value_objects import CoursId, InscriptionId, Note, StudentId


@dataclass(frozen=True, slots=True, init=False)
class Inscription:
    id: InscriptionId | None
    student_id: StudentId
    cours_id: CoursId
    note: Note | None

    @classmethod
    def create(
        cls,
        id: InscriptionId,
        student_id: StudentId,
        cours_id: CoursId,
        note: Note | None = None,
    ) -> Inscription:
        return build(cls, id=id, student_id=student_id, cours_id=cours_id, note=note)

    @classmethod
    def restore(
        cls,
        id: InscriptionId,
        student_id: StudentId,
        cours_id: CoursId,
        note: Note | None = None,
    ) -> Inscription:
        return build(cls, id=id, student_id=student_id, cours_id=cours_id, note=note)

    def assign_note(self, note: Note) -> Inscription:
        return set_attributes(self, note=note)
