from __future__ import annotations
from dataclasses import dataclass

from lab_3.core.domain.common import Result, Success, Failure
from lab_3.core.domain.common.validation import ValidationError, ValidationErrors

@dataclass(frozen=True, slots=True, init=False)
class Student:
    id:int|None
    name: str
    email: str
    programme_id: int

    @classmethod
    def create(cls, 
               name:str,
               email:str,
               programme_id:int,
               id:int|None=None
    ) -> Result[Student, ValidationErrors]:
        errors:list[ValidationError] = []
        if not name.strip():
            errors.append(ValidationError(field="name", message="Name is required"))
        if not email.strip():
            errors.append(ValidationError(field="email", message="Email is required"))

        if programme_id <= 0:
            errors.append(ValidationError(field="programme_id", message="Programme ID must be greater than 0"))

        if id is not None and id <= 0:
            errors.append(ValidationError(field="id", message="Id must be greater than 0"))

        if errors:
            return Failure(ValidationErrors(errors))
        return Success(cls._create(id, name.strip(), email.strip(), programme_id))  

    @classmethod
    def _create(cls, id:int|None, name:str, email:str, programme_id:int) -> Student:
        obj = object.__new__(cls)
        obj.__setattr__("id", id)
        obj.__setattr__("name", name)
        obj.__setattr__("email", email)
        obj.__setattr__("programme_id", programme_id)
        return obj