from lab_3.adapters.inbound.flask.common.error_mapper import HttpErrorResponse
from lab_3.core.application.ports.inbound.create_inscription import (
    CourseNotFound,
    CreateInscriptionCommand,
    CreateInscriptionResult,
    InscriptionAlreadyExists,
    StudentNotFound,
)
from lab_3.core.application.ports.inbound.update_inscription import (
    UpdateInscriptionNoteCommand,
    UpdateInscriptionNoteResult,
    InscriptionNotFound,
)
from lab_3.core.application.ports.inbound.delete_inscription import (
    DeleteInscriptionCommand,
    DeleteInscriptionResult,
    InscriptionIdNotFound as DeleteInscriptionIdNotFound,
)
from lab_3.core.domain.common import Failure, Result, Success, collect_errors
from lab_3.core.domain.common.validation import ValidationErrors
from lab_3.core.domain.value_objects import CoursId, StudentId, InscriptionId, Note

from .request import CreateInscriptionRequest, UpdateInscriptionNoteRequest
from .response import CreateInscriptionResponse, UpdateInscriptionNoteResponse


def to_create_inscription_command(
    request: CreateInscriptionRequest
) -> Result[CreateInscriptionCommand, ValidationErrors]:
    student_id_result = StudentId.create(request.student_id)
    cours_id_result = CoursId.create(request.cours_id)
    errors = collect_errors(student_id_result, cours_id_result)
    if errors:
        return Failure(ValidationErrors(tuple(errors)))

    assert isinstance(student_id_result, Success) # for pyright
    assert isinstance(cours_id_result, Success)

    return Success(
        CreateInscriptionCommand(
            student_id=student_id_result.outcome,
            cours_id=cours_id_result.outcome,
        )
    )


def to_create_inscription_response(
    result: CreateInscriptionResult,
) -> CreateInscriptionResponse:
    return CreateInscriptionResponse(
        id=result.id,
        student_id=result.student_id,
        cours_id=result.cours_id,
        note=result.note,
    )


def map_create_inscription_error(error) -> HttpErrorResponse:
    if isinstance(error, StudentNotFound):
        return HttpErrorResponse(
            body={"error": "Student not found", "student_id": error.student_id.value},
            status_code=404,
        )
    if isinstance(error, CourseNotFound):
        return HttpErrorResponse(
            body={"error": "Course not found", "cours_id": error.cours_id.value},
            status_code=404,
        )
    if isinstance(error, InscriptionAlreadyExists):
        return HttpErrorResponse(
            body={
                "error": "Inscription already exists",
                "student_id": error.student_id.value,
                "cours_id": error.cours_id.value,
            },
            status_code=409,
        )
    raise RuntimeError(f"Unhandled CreateInscription error: {error}")

## Update inscription note mapper

def to_update_inscription_note_command(
    request: UpdateInscriptionNoteRequest,
) -> Result[UpdateInscriptionNoteCommand, ValidationErrors]:
    id_result = InscriptionId.create(request.id)
    note_result = (Success(None) if request.note is None else Note.create(request.note))
    errors = collect_errors(id_result, note_result)
    if errors:
        return Failure(ValidationErrors(tuple(tuple(errors))))

    assert isinstance(id_result, Success)
    assert isinstance(note_result, Success)
    return Success(UpdateInscriptionNoteCommand(id=id_result.outcome, note=note_result.outcome))

def map_update_inscription_note_error(error:InscriptionNotFound) -> HttpErrorResponse:
    return HttpErrorResponse(
        body={"error": "Inscription not found", "id": error.id.value},
        status_code=404,
    )

def to_update_inscription_note_response(
    result: UpdateInscriptionNoteResult,
) -> UpdateInscriptionNoteResponse:
    return UpdateInscriptionNoteResponse(
        id=result.id,
        note=result.note,
    )


## Delete inscription mapper

def to_delete_inscription_command(
    inscription_id: int,
) -> Result[DeleteInscriptionCommand, ValidationErrors]:
    id_result = InscriptionId.create(inscription_id)
    errors = collect_errors(id_result)
    if errors:
        return Failure(ValidationErrors(tuple(tuple(errors))))
    assert isinstance(id_result, Success)
    return Success(DeleteInscriptionCommand(id=id_result.outcome))

def map_delete_inscription_error(error: DeleteInscriptionIdNotFound) -> HttpErrorResponse:
    return HttpErrorResponse(
        body={"error": "Inscription not found", "id": error.id.value},
        status_code=404,
    )
