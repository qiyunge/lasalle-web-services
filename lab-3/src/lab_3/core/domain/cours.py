from __future__ import annotations

from dataclasses import dataclass

from lab_3.core.domain.common.build import build
from lab_3.core.domain.value_objects import CoursCode, CoursId, CoursName


@dataclass(frozen=True, slots=True, init=False)
class Cours:
    id: CoursId
    code: CoursCode
    name: CoursName

    @classmethod
    def create(
        cls,
        id: CoursId,
        code: CoursCode,
        name: CoursName,
    ) -> Cours:
        return build(cls, id=id, code=code, name=name)

    @classmethod
    def restore(cls, id: CoursId, code: CoursCode, name: CoursName) -> Cours:
        return build(cls, id=id, code=code, name=name)
