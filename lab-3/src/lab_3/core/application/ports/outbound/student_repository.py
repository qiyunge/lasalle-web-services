from __future__ import annotations

from typing import Protocol

from lab_3.core.domain.student import Student
from lab_3.core.domain.value_objects import StudentId

class StudentRepository(Protocol):
    def exists(self, id:StudentId) -> bool:
        ...
