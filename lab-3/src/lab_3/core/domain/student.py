from __future__ import annotations

from dataclasses import dataclass

from lab_3.core.domain.common.build import build
from lab_3.core.domain.value_objects import (
    ProgrammeId,
    StudentEmail,
    StudentId,
    StudentName,
)


@dataclass(frozen=True, slots=True, init=False)
class Student:
    id: StudentId
    name: StudentName
    email: StudentEmail
    programme_id: ProgrammeId

    @classmethod
    def create(
        cls,
        id: StudentId,
        name: StudentName,
        email: StudentEmail,
        programme_id: ProgrammeId,
    ) -> Student:
        return build(cls, id=id, name=name, email=email, programme_id=programme_id)

    @classmethod
    def restore(
        cls,
        id: StudentId,
        name: StudentName,
        email: StudentEmail,
        programme_id: ProgrammeId,
    ) -> Student:
        return build(cls, id=id, name=name, email=email, programme_id=programme_id)
