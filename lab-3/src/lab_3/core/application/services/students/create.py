import uuid

from lab_3.core.application.ports.inbound.students.create import CreateStudentCommand, CreateStudentResult, CreateStudentOutcome
from lab_3.core.application.ports.outbound import TransactionRestartRequired
from lab_3.core.application.ports.outbound.student_repository import StudentRepository
from lab_3.core.application.ports.outbound.programme_repository import ProgrammeRepository
from lab_3.core.application.ports.outbound.unit_of_work import UnitOfWork
from lab_3.core.domain.common import Failure, Success
from lab_3.core.application.ports.inbound.students.create import StudentEmailAlreadyExists, ProgrammeNotFound
from lab_3.core.domain.value_objects import StudentId
from lab_3.core.domain import Student
from lab_3.core.application.ports.outbound.student_repository import StudentSavePersistenceResult, StudentEmailConflictPersistenceError, StudentIdConflictPersistenceError


def _new_student(command: CreateStudentCommand) -> Student:
    value = uuid.uuid4().int % (2**63)
    id_result = StudentId.create(value if value > 0 else 1)
    if isinstance(id_result, Failure):
        raise RuntimeError("Generated student ID is invalid")  # noqa: TRY004

    return Student.create(id_result.outcome, command.name, command.email, command.programme_id)

_TRANSACTION_ATTEMPTS = 3

class CreateStudentHandler:
    def __init__(self, student_repository: StudentRepository, programme_repository: ProgrammeRepository, unit_of_work: UnitOfWork) -> None:
        self._student_repository = student_repository
        self._programme_repository = programme_repository
        self._unit_of_work = unit_of_work

    def handle(self, command: CreateStudentCommand) -> CreateStudentResult:
        student = _new_student(command)
        for attempt in range(_TRANSACTION_ATTEMPTS):
            try:
                result = self._create(student)
                if isinstance(result, Success):
                    return Success(CreateStudentOutcome(student.id, student.name, student.email, student.programme_id))

                match result.error:
                    case StudentIdConflictPersistenceError():
                        if attempt == _TRANSACTION_ATTEMPTS - 1:
                            raise RuntimeError("Failed to generate unique student ID")  # noqa: TRY004
                        student = _new_student(command)
                        continue
                    case StudentEmailConflictPersistenceError(email):
                        return Failure(StudentEmailAlreadyExists(email.value))
                    case _:
                        raise RuntimeError("Unexpected error")  # noqa: TRY004
            except TransactionRestartRequired as e:
                if attempt == _TRANSACTION_ATTEMPTS - 1:
                    raise
            except Exception as e:
                raise
              


    def _create(self, student: Student) -> CreateStudentResult:
        with self._unit_of_work as uow:
            result = self._student_repository.save(student)
            if isinstance(result, Failure):
                return Failure(result.error)

            uow.commit()

        return Success(None)