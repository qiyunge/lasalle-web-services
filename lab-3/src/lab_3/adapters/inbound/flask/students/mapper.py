from typing import assert_never
from lab_3.adapters.inbound.flask.students.request import CreateStudentRequest
from lab_3.adapters.inbound.flask.students.response import CreateStudentResponse
from lab_3.core.application.ports.inbound.students.create import CreateStudentCommand, CreateStudentOutcome, CreateStudentError
from lab_3.core.domain.value_objects import StudentName, StudentEmail, ProgrammeId, StudentId   
from lab_3.core.domain.common import Failure, Success, ValidationErrors, collect_errors
from lab_3.adapters.inbound.flask.common.error_mapper import HttpErrorResponse
from lab_3.core.application.ports.inbound.students.create import StudentEmailAlreadyExists, ProgrammeNotFound
from lab_3.core.domain.common import Result
from lab_3.core.application.ports.inbound.students.get import GetStudentCommand
from lab_3.adapters.inbound.flask.students.response import GetStudentResponse
from lab_3.core.application.ports.inbound.students.get import GetStudentOutcome, GetStudentError, StudentNotFound as GetStudentNotFound
from lab_3.adapters.inbound.flask.students.request import GetStudentRequest
from lab_3.core.application.ports.inbound.students.delete import DeleteStudentCommand
from lab_3.adapters.inbound.flask.students.request import DeleteStudentRequest
from lab_3.core.application.ports.inbound.students.delete import  DeleteStudentError, StudentNotFound as DeleteStudentNotFound, StudentHasInscriptions as DeleteStudentHasInscriptions

def to_create_student_command(request: CreateStudentRequest) -> Result[CreateStudentCommand, ValidationErrors]:
    name_result = StudentName.create(request.name)
    email_result = StudentEmail.create(request.email)
    programme_id_result = ProgrammeId.create(request.programme_id)

    errors = collect_errors(name_result, email_result, programme_id_result)
    if errors:
        return Failure(ValidationErrors(tuple(errors)))

    assert isinstance(name_result, Success)
    assert isinstance(email_result, Success)
    assert isinstance(programme_id_result, Success)

    return Success(CreateStudentCommand(name=name_result.outcome, email=email_result.outcome, programme_id=programme_id_result.outcome))

def to_create_student_response(outcome: CreateStudentOutcome) -> CreateStudentResponse:
    return CreateStudentResponse(student_id=outcome.student_id.value, name=outcome.name.value, email=outcome.email.value, programme_id=outcome.programme_id.value)

def map_create_student_error(error: CreateStudentError) -> HttpErrorResponse:
    match error:
        case StudentEmailAlreadyExists(email):
            return HttpErrorResponse(
                body={"error": "Student email already exists", "email": email},
                status_code=409,
            )
        case ProgrammeNotFound(programme_id):
            return HttpErrorResponse(
                body={"error": "Programme not found", "programme_id": programme_id},
                status_code=404,
            )
        case _:
            assert_never(error)


def to_get_student_command(request: GetStudentRequest) -> Result[GetStudentCommand, ValidationErrors]:
    student_id_result = StudentId.create(request.student_id)
    errors = collect_errors(student_id_result)
    if errors:
        return Failure(ValidationErrors(tuple(errors)))

    assert isinstance(student_id_result, Success)
    return Success(GetStudentCommand(student_id=student_id_result.outcome))

def to_get_student_reponse(outcome: GetStudentOutcome) -> GetStudentResponse:
    return GetStudentResponse(student_id=outcome.student_id.value, name=outcome.name.value, email=outcome.email.value, programme_id=outcome.programme_id.value)

def map_get_student_error(error: GetStudentError) -> HttpErrorResponse:
    match error:
        case GetStudentNotFound(student_id):
            return HttpErrorResponse(
                body={"error": "Student not found", "student_id": student_id},
                status_code=404,
            )
        case _:
            assert_never(error)

##
def to_delete_student_command(request: DeleteStudentRequest) -> Result[DeleteStudentCommand, ValidationErrors]:
    student_id_result = StudentId.create(request.student_id)
    errors = collect_errors(student_id_result)
    if errors:
        return Failure(ValidationErrors(tuple(errors)))

    assert isinstance(student_id_result, Success)
    return Success(DeleteStudentCommand(student_id=student_id_result.outcome))

def map_delete_student_error(error: DeleteStudentError) -> HttpErrorResponse:
    match error:
        case DeleteStudentNotFound(student_id):
            return HttpErrorResponse(
                body={"error": "Student not found", "student_id": student_id.value},
                status_code=404,
            )
        case DeleteStudentHasInscriptions(student_id):
            return HttpErrorResponse(
                body={"error": "Student has inscriptions", "student_id": student_id.value},
                status_code=409,
            )
        case _:
            assert_never(error)

