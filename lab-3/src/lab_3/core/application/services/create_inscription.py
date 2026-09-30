from __future__ import annotations

import uuid

from lab_3.core.application.ports.inbound.create_inscription import (
    CourseNotFound,
    CreateInscriptionCommand,
    CreateInscriptionOutcome,
    CreateInscriptionResult,
    InscriptionAlreadyExists,
    StudentNotFound,
)
from lab_3.core.application.ports.outbound import (
    CoursRepository,
    InscriptionRepository,
    StudentRepository,
    TransactionRestartRequired,
    UnitOfWork,
)
from lab_3.core.application.ports.outbound.inscription_repository import (
    InscriptionIdConflict,
)
from lab_3.core.domain import Inscription
from lab_3.core.domain.common import Failure, Success
from lab_3.core.domain.value_objects import InscriptionId

_TRANSACTION_ATTEMPTS = 3


def _generate_inscription_id() -> int:
    value = uuid.uuid4().int % (2**63)
    return value if value > 0 else 1


def _new_inscription(command: CreateInscriptionCommand) -> Inscription:
    id_result = InscriptionId.create(_generate_inscription_id())
    if isinstance(id_result, Failure):
        raise RuntimeError("Generated inscription id is invalid") # noqa: TRY004
    return Inscription.create(
        id=id_result.value,
        student_id=command.student_id,
        cours_id=command.cours_id,
    )


class CreateInscriptionHandler:
    def __init__(
        self,
        inscription_repository: InscriptionRepository,
        student_repository: StudentRepository,
        cours_repository: CoursRepository,
        unit_of_work: UnitOfWork,
    ) -> None:
        self._inscription_repository = inscription_repository
        self._student_repository = student_repository
        self._cours_repository = cours_repository
        self._unit_of_work = unit_of_work

    def handle(
        self,
        command: CreateInscriptionCommand,
    ) -> CreateInscriptionOutcome:
        inscription = _new_inscription(command)

        for attempt in range(_TRANSACTION_ATTEMPTS):
            last_attempt = attempt == _TRANSACTION_ATTEMPTS - 1

            try:
                result = self._create(command, inscription)
            except TransactionRestartRequired:
                if last_attempt:
                    raise
                continue
            except InscriptionIdConflict:
                if last_attempt:
                    raise RuntimeError("Failed to allocate an inscription id") from None
                inscription = _new_inscription(command)
                continue

            if isinstance(result, Failure):
                return Failure(result.error)

            return result

        raise RuntimeError("Create inscription transaction was not completed")

    def _create(
        self,
        command: CreateInscriptionCommand,
        inscription: Inscription,
    ) -> CreateInscriptionOutcome:
        with self._unit_of_work as unit_of_work:
            if not self._student_repository.exists(command.student_id):
                return Failure(StudentNotFound(command.student_id))

            if not self._cours_repository.exists(command.cours_id):
                return Failure(CourseNotFound(command.cours_id))

            if self._inscription_repository.exists(
                command.student_id, command.cours_id
            ):
                return Failure(
                    InscriptionAlreadyExists(command.student_id, command.cours_id)
                )

            saved_result = self._inscription_repository.save(inscription)
            if isinstance(saved_result, Failure):
               return Failure(
                    InscriptionAlreadyExists(
                        command.student_id,
                        command.cours_id,
                    )
                )   
            unit_of_work.commit()
            inscription = saved_result.value

        inscription_id = inscription.id
        if inscription_id is None:
            raise RuntimeError("Inscription id is required")

        return Success(
            CreateInscriptionResult(
                id=inscription_id.value,
                student_id=inscription.student_id.value,
                cours_id=inscription.cours_id.value,
                note=(inscription.note.value if inscription.note is not None else None),
            )
        )
