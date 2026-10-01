from lab_3.core.application.ports.inbound.programmes.list import (
    ProgrammeListResult,
    ProgrammeItem,
)
from lab_3.core.application.ports.outbound.programme_repository import (
    ProgrammeRepository,
)
from lab_3.core.application.ports.outbound.unit_of_work import UnitOfWork
from lab_3.core.application.ports.inbound.programmes.list import ProgrammeListQuery


class ProgrammeListHandler:
    def __init__(self, programme_repository: ProgrammeRepository, unit_of_work: UnitOfWork) -> None:
        self._programme_repository = programme_repository
        self._unit_of_work = unit_of_work

    def handle(self, query: ProgrammeListQuery) -> ProgrammeListResult:
        with self._unit_of_work as uow:
            programmes = self._programme_repository.find_all()
            return  ProgrammeListResult(programmes=tuple(ProgrammeItem(id=programme.id.value, name=programme.name.value) for programme in programmes))