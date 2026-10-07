from lab_3.core.application.ports.outbound.cours_repository import CoursRepository
from lab_3.core.application.ports.outbound.unit_of_work import UnitOfWork
from lab_3.core.domain.common import Success, Failure
from lab_3.core.application.ports.inbound.cours.list import ListCoursCommand, ListCoursResult
from lab_3.core.application.ports.inbound.cours.list import ListCoursOutcome


class ListCoursHandler:
    def __init__(self, cours_repository: CoursRepository, unit_of_work: UnitOfWork) -> None:
        self._cours_repository = cours_repository
        self._unit_of_work = unit_of_work   


    def handle(self, command: ListCoursCommand) -> ListCoursResult:
        

        with self._unit_of_work as unit_of_work:
            result = self._cours_repository.find_all(command.page, command.page_size)
            return Success(ListCoursOutcome(result, command.page, command.page_size))