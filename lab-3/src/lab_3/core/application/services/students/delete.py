from lab_3.core.application.ports.inbound.students.delete import DeleteStudentCommand, DeleteStudentResult
from lab_3.core.application.ports.outbound.student_repository import StudentRepository
from lab_3.core.application.ports.outbound.unit_of_work import UnitOfWork
from lab_3.core.application.ports.outbound import TransactionRestartRequired
from lab_3.core.domain.common import Failure, Success
from lab_3.core.application.ports.inbound.students.delete import DeleteStudentError, StudentNotFound as DeleteStudentNotFound, StudentHasInscriptions as DeleteStudentHasInscriptions
from lab_3.core.application.ports.inbound.students.delete import DeleteStudentOutcome
from lab_3.core.application.ports.outbound.student_repository import StudentReferencedPersistenceError, StudentNotFoundPersistenceError
_TRANSACTION_ATTEMPTS = 3

class DeleteStudentHandler:
    def __init__(self, student_repository: StudentRepository, unit_of_work: UnitOfWork) -> None:
        self._student_repository = student_repository
        self._unit_of_work = unit_of_work

    def handle(self, command: DeleteStudentCommand) -> DeleteStudentResult:
        for attempt in range(_TRANSACTION_ATTEMPTS):
            try:
                return self._delete(command)
            except TransactionRestartRequired:
                if attempt == _TRANSACTION_ATTEMPTS - 1:
                    raise
        raise RuntimeError("Delete student transaction was not completed.")

    def _delete(self, command: DeleteStudentCommand) -> DeleteStudentResult:
        with self._unit_of_work as uow:
            
            deleted = self._student_repository.delete(command.student_id)
            if isinstance(deleted, Failure):
                match deleted.error:
                    case StudentReferencedPersistenceError(id):
                        return Failure(DeleteStudentHasInscriptions(id))
                    case StudentNotFoundPersistenceError(id):
                        return Failure(DeleteStudentNotFound(id))
                    case _:
                        raise RuntimeError("Unhandled delete student persistence result")
                return deleted
            uow.commit()
            return Success(DeleteStudentOutcome(student_id=command.student_id))