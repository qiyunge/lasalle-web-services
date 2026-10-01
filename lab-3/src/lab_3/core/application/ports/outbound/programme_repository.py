from dataclasses import dataclass
from typing import Protocol

from lab_3.core.domain.programme import Programme
from lab_3.core.domain.value_objects import ProgrammeId, ProgrammeName

@dataclass(eq=False)
class ProgrammeIdConflictException(Exception):
    id: ProgrammeId
    def __post_init__(self):
        self.message = f"Programme with id {self.id} already exists"

@dataclass(eq=False)
class ProgrammeNameConflictException(Exception):
    name: ProgrammeName
    def __post_init__(self):
        self.message = f"Programme with name {self.name} already exists"

class ProgrammeRepository(Protocol):
    def find_all(self) -> list[Programme]: ...

    def save(self, programme: Programme) -> None: ...

