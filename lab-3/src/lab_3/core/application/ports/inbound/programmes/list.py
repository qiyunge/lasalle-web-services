from dataclasses import dataclass
from lab_3.core.application.query import Query
from typing import Protocol

@dataclass(frozen=True)
class ProgrammeItem:
    id: int
    name: str

@dataclass(frozen=True)
class ProgrammeListResult:
    programmes: tuple[ProgrammeItem, ...]

class ProgrammeListUseCase(Protocol):
    def handle(self) -> ProgrammeListResult: ...

class ProgrammeListQuery(Query[ProgrammeListResult]):
    pass    