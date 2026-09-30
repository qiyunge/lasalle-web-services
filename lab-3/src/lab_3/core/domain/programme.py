from __future__ import annotations

from dataclasses import dataclass

from lab_3.core.domain.common.build import build
from lab_3.core.domain.value_objects import ProgrammeId, ProgrammeName


@dataclass(slots=True, frozen=True, init=False)
class Programme:
    id: ProgrammeId
    name: ProgrammeName

    @classmethod
    def create(cls, id: ProgrammeId, name: ProgrammeName) -> Programme:
        return build(cls, id=id, name=name)

    @classmethod
    def restore(cls, id: ProgrammeId, name: ProgrammeName) -> Programme:
        return build(cls, id=id, name=name)
