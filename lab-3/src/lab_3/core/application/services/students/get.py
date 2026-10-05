from lab_3.core.application.ports.outbound.student_repository import StudentRepository
from lab_3.core.application.ports.inbound.students.get import GetStudentCommand, GetStudentResult
from lab_3.core.domain.common import Failure, Success
from lab_3.core.application.ports.outbound.unit_of_work import UnitOfWork
from lab_3.core.application.ports.outbound import TransactionRestartRequired
from lab_3.core.application.ports.inbound.students.get import GetStudentOutcome, StudentNotFound as GetStudentNotFound

_TRANSACTION_ATTEMPTS = 3

class GetStudentHandler:
    def __init__(self, student_repository: StudentRepository,unit_of_work: UnitOfWork) -> None:
        self._student_repository = student_repository
        self._unit_of_work = unit_of_work
    
    def handle(self, command: GetStudentCommand) -> GetStudentResult:
        for attempt in range(_TRANSACTION_ATTEMPTS):
            try:
                result = self._get(command)
                return result
            except TransactionRestartRequired:
                if attempt == _TRANSACTION_ATTEMPTS - 1:
                    raise
            except Exception as e:
                raise

    def _get(self, command: GetStudentCommand) -> GetStudentResult:
        with self._unit_of_work as uow:
            persistence_result = self._student_repository.get(command.student_id)
            if isinstance(persistence_result, Failure):
                return Failure(GetStudentNotFound(command.student_id))
            return Success(GetStudentOutcome(persistence_result.outcome.id, persistence_result.outcome.name, persistence_result.outcome.email, persistence_result.outcome.programme_id))