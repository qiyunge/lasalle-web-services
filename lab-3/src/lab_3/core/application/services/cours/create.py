from lab_3.core.application.ports.inbound.cours.create import CreateCoursCommand, CreateCoursResult, CreateCoursOutcome
from lab_3.core.application.ports.outbound.cours_repository import CoursRepository
from lab_3.core.application.ports.outbound.unit_of_work import UnitOfWork
from lab_3.core.application.ports.outbound import TransactionRestartRequired
from lab_3.core.application.ports.inbound.cours.create import CreateCoursCodeAlreadyExistsError
from lab_3.core.domain.value_objects import CoursId
from lab_3.core.domain import Cours
from lab_3.core.domain.common import Failure, Success
from lab_3.core.application.ports.outbound.cours_repository import CreateCoursCodeAlreadyExistsPersistenceError, CreateCoursIdConflictPersistenceError
from lab_3.core.application.ports.outbound.cours_repository import CreateCoursPersistenceResult
import uuid

def _new_cours(command: CreateCoursCommand) -> Cours:
    value = uuid.uuid4().int % (2**63)
    id_result = CoursId.create(value if value > 0 else 1)
    if isinstance(id_result, Failure):
        raise RuntimeError("Generated cours ID is invalid")  # noqa: TRY004

    return Cours.create(id_result.outcome, command.cours_code, command.cours_name)

_TRANSACTION_ATTEMPTS = 3

class CreateCoursHandler:
    def __init__(self, cours_repository: CoursRepository, unit_of_work: UnitOfWork) -> None:
        self._cours_repository = cours_repository
        self._unit_of_work = unit_of_work
    def handle(self, command: CreateCoursCommand) -> CreateCoursResult:

        cours = _new_cours(command)
        for attempt in range(_TRANSACTION_ATTEMPTS):
            try:
                result = self._create(cours)
            except TransactionRestartRequired as e:
                if attempt == _TRANSACTION_ATTEMPTS - 1:
                    raise
                continue
            if isinstance(result, Failure):
               
                match result.error:
                    case CreateCoursIdConflictPersistenceError():
                        if attempt == _TRANSACTION_ATTEMPTS - 1:
                            raise RuntimeError("Failed to generate unique cours ID")  # noqa: TRY004
                        cours = _new_cours(command)
                        continue
                    case CreateCoursCodeAlreadyExistsPersistenceError():
                        return Failure(CreateCoursCodeAlreadyExistsError(command.cours_code))
                    
                    case _:
                        raise RuntimeError("Unexpected error")  # noqa: TRY004
            return Success(CreateCoursOutcome(cours.id, cours.code, cours.name))    
            raise RuntimeError("Create cours transaction was not completed")

    def _create(self, cours: Cours) -> CreateCoursPersistenceResult:
        with self._unit_of_work as unit_of_work:
            result = self._cours_repository.save(cours)
            if isinstance(result, Failure):
                return result
            unit_of_work.commit()
            return result