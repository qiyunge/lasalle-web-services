from lab_3.core.application.ports.inbound.cours.get import GetCoursCommand, GetCoursResult
from lab_3.core.application.ports.outbound.cours_repository import CoursRepository
from lab_3.core.application.ports.outbound.unit_of_work import UnitOfWork
from lab_3.core.domain.common import Success, Failure
from lab_3.core.application.ports.inbound.cours.get import GetCoursOutcome
from lab_3.core.application.ports.outbound.cours_repository import GetCoursNotFoundPersistenceError
from lab_3.core.application.ports.inbound.cours.get import GetCoursNotFoundError

class GetCoursHandler:
    def __init__(self, cours_repository: CoursRepository, unit_of_work: UnitOfWork) -> None:
        self._cours_repository = cours_repository
        self._unit_of_work = unit_of_work   


    def handle(self, command: GetCoursCommand) -> GetCoursResult:
        with self._unit_of_work as unit_of_work:
            result = self._cours_repository.find_by_id(command.cours_id)
            if isinstance(result, Success):
                return Success(GetCoursOutcome(result.outcome.id, result.outcome.code, result.outcome.name))
            if isinstance(result, Failure):
                match result.error:
                    case GetCoursNotFoundPersistenceError():
                        return Failure(GetCoursNotFoundError(command.cours_id))
                    case _:
                        raise RuntimeError("Unexpected error")  # noqa: TRY004
           
            return result