from lab_3.core.application.ports.inbound.delete_inscription import (
    DeleteInscriptionCommand,
    DeleteInscriptionOutcome,
    DeleteInscriptionResult,
    InscriptionIdNotFound,
)

from lab_3.core.application.ports.outbound import (
    InscriptionRepository,
    TransactionRestartRequired,
    UnitOfWork,
)
from lab_3.core.domain.common import Failure, Success

_TRANSACTION_ATTEMPTS = 3

class DeleteInscriptionHandler:
    def __init__(
        self,
        inscription_repository: InscriptionRepository,
        unit_of_work: UnitOfWork,
    ) -> None:
        self._inscription_repository = inscription_repository
        self._unit_of_work = unit_of_work

    def handle(self, command: DeleteInscriptionCommand) -> DeleteInscriptionOutcome:
        for attempt in range(_TRANSACTION_ATTEMPTS):
            try:
                return self._delete(command)
            except TransactionRestartRequired:
                if attempt == _TRANSACTION_ATTEMPTS - 1:
                    raise
        raise RuntimeError("Delete inscription transaction was not completed.")

    def _delete(self, command: DeleteInscriptionCommand) -> DeleteInscriptionOutcome:
        with self._unit_of_work as uow:
            deleted = self._inscription_repository.delete(command.id)
            if not deleted:
                return Failure(InscriptionIdNotFound(command.id))
            uow.commit()
            return Success(DeleteInscriptionResult(id=command.id.value))
     