from __future__ import annotations
from dataclasses import dataclass

from lab_3.core.domain.common import Result, Success, Failure
from lab_3.core.domain.common.validation import ValidationError, ValidationErrors
from lab_3.core.domain.value_objects import CoursId, CoursCode, CoursName

@dataclass(frozen=True, slots=True, init=False)
class Cours:
    id:CoursId|None
    code: CoursCode
    name: CoursName

    @classmethod
    def create(cls, 
               code:CoursCode,
               name:CoursName,
    ) -> Cours:
        
        obj = object.__new__(cls)
        obj.__setattr__("code", code)
        obj.__setattr__("name", name)
        return obj

    @classmethod
    def restore(cls, id:CoursId, code:CoursCode, name:CoursName) -> Cours:
        obj = object.__new__(cls)
        obj.__setattr__("id", id)
        obj.__setattr__("code", code)
        obj.__setattr__("name", name)
        return obj

    