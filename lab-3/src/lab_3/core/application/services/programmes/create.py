import uuid

from lab_3.core.application.ports.inbound.programmes.create import (
    CreateProgrammeCommand,
    CreateProgrammeResult,  
    CreateProgrammeOutcome,
    ProgrammeNameAlreadyExists,
)
from lab_3.core.application.ports.outbound.programme_repository import (
    ProgrammeIdConflictException,
    ProgrammeNameConflictException,
    ProgrammeRepository,
)
from lab_3.core.application.ports.outbound.unit_of_work import (
    TransactionRestartRequired,
    UnitOfWork,
)
from lab_3.core.domain.common import Failure, Success
from lab_3.core.domain.programme import Programme
from lab_3.core.domain.value_objects import ProgrammeId

_TRANSACTION_ATTEMPTS = 3


def _new_programme(command: CreateProgrammeCommand) -> Programme:
    value = uuid.uuid4().int % (2**63)
    id_result = ProgrammeId.create(value if value > 0 else 1)

    if isinstance(id_result, Failure):
        raise RuntimeError("Generated programme ID is invalid")  # noqa: TRY004

    return Programme.create(
        id=id_result.value,
        name=command.name,
    )


class CreateProgrammeHandler:
    def __init__(
        self,
        programme_repository: ProgrammeRepository,
        unit_of_work: UnitOfWork,
    ) -> None:
        self._programme_repository = programme_repository
        self._unit_of_work = unit_of_work

    def handle(
        self,
        command: CreateProgrammeCommand,
    ) -> CreateProgrammeOutcome:
        programme = _new_programme(command)

        for attempt in range(_TRANSACTION_ATTEMPTS):
            try:
                return self._create(programme)
            except TransactionRestartRequired:
                if attempt == _TRANSACTION_ATTEMPTS - 1:
                    raise
            except ProgrammeIdConflictException:
                if attempt == _TRANSACTION_ATTEMPTS - 1:
                    raise
                programme = _new_programme(command)
            except ProgrammeNameConflictException as e:
                return Failure(ProgrammeNameAlreadyExists(e.name))

        raise RuntimeError("Create programme transaction was not completed")

    def _create(self, programme: Programme) -> CreateProgrammeResult:
        with self._unit_of_work as uow:
            self._programme_repository.save(programme)
            uow.commit()

        return Success(CreateProgrammeResult(
            id=programme.id.value,
            name=programme.name.value,
        ))