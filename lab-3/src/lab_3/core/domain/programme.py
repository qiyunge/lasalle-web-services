from __future__ import annotations

from dataclasses import dataclass

from lab_3.core.domain.common import Result, Success, Failure
from lab_3.core.domain.common.validation import ValidationError, ValidationErrors
from lab_3.core.domain.value_objects import ProgrammeId, ProgrammeName

@dataclass(slots=True, frozen=True, init=False)
class Programme:
    id:ProgrammeId|None
    name: ProgrammeName

    @classmethod
    def create(cls, 
                name:ProgrammeName,
                id:ProgrammeId|None=None
    ) -> Programme:
        obj = object.__new__(cls)
        obj.__setattr__("id", id)
        obj.__setattr__("name", name)
        return obj

    @classmethod
    def restore(cls, id:ProgrammeId, name:ProgrammeName) -> Programme:
        obj = object.__new__(cls)
        obj.__setattr__("id", id)
        obj.__setattr__("name", name)
        return obj

    def change_name(self, name:ProgrammeName) -> Programme:
        object.__setattr__(self, "name", name)
        return self
