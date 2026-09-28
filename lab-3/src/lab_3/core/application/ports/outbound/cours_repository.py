from __future__ import annotations

from typing import Protocol

from lab_3.core.domain.cours import Cours
from lab_3.core.domain.value_objects import CoursId

class CoursRepository(Protocol):
    def exists(self, id:CoursId) -> bool:
        ...

   