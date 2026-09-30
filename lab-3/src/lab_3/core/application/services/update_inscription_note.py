from __future__ import annotations

from lab_3.core.application.ports.inbound.update_inscription import (
    UpdateInscriptionNoteCommand, 
    UpdateInscriptionNoteResult,
    UpdateInscriptionNoteOutcome,
    InscriptionNotFound
)

from lab_3.core.application.ports.outbound import (
    InscriptionRepository,
    TransactionRestartRequired,
    UnitOfWork,
)

from lab_3.core.domain.common import  Success, Failure

_TRANSACTION_ATTEMPTS = 3

class UpdateInscriptionNoteHandler:
    def __init__(self, inscription_repository: InscriptionRepository, unit_of_work: UnitOfWork) -> None:
        self._inscription_repository = inscription_repository
        self._unit_of_work = unit_of_work

    def handle(self, command: UpdateInscriptionNoteCommand) -> UpdateInscriptionNoteOutcome:
        for attempt in range(_TRANSACTION_ATTEMPTS):

            try:
                return self._update_inscription_note(command)
            except TransactionRestartRequired:
                if attempt == _TRANSACTION_ATTEMPTS - 1:
                    raise
        raise RuntimeError("Update inscription transaction was not completed.")

    def _update_inscription_note(self, command: UpdateInscriptionNoteCommand) -> UpdateInscriptionNoteOutcome:
        with self._unit_of_work as uow:
                   
            found = self._inscription_repository.update_note(command.id, command.note)
            if not found:
                return Failure(InscriptionNotFound(command.id))
            
            uow.commit()
        return Success(UpdateInscriptionNoteResult(
            command.id.value, command.note.value if command.note is not None else None))
