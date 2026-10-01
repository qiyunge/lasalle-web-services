from typing import Protocol

from lab_3.core.domain.programme import Programme



class ProgrammeRepository(Protocol):
    def find_all(self) -> list[Programme]: ...