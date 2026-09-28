from lab_3.core.application.ports.inbound.create_inscription import CreateInscriptionCommand, CreateInscriptionResult

from  .request import CreateInscriptionRequest
from .response import CreateInscriptionResponse
from lab_3.adapters.inbound.flask.common.error_mapper import HttpErrorResponse
from lab_3.core.application.ports.inbound.create_inscription import StudentNotFound, CourseNotFound, InscriptionAlreadyExists, InscriptionCreationFailed

def to_create_inscription_command(request: CreateInscriptionRequest) -> CreateInscriptionCommand:
    return CreateInscriptionCommand(student_id=request.student_id, course_id=request.course_id)

def to_create_inscription_response(result: CreateInscriptionResult) -> CreateInscriptionResponse:
    return CreateInscriptionResponse(id=result.id, student_id=result.student_id, course_id=result.course_id, note=result.note)

def map_create_inscription_error(error) -> HttpErrorResponse:
    if isinstance(error, StudentNotFound):
        return HttpErrorResponse(body={'error': 'Student not found',"student_id": error.student_id}, status_code=404)
    elif isinstance(error, CourseNotFound):
        return HttpErrorResponse(body={'error': 'Course not found',"course_id": error.course_id}, status_code=404)
    elif isinstance(error, InscriptionAlreadyExists):
        return HttpErrorResponse(body={'error': 'Inscription already exists',"student_id": error.student_id, "course_id": error.course_id}, status_code=409)
    
    raise RuntimeError(f"Unhandled CreateInscription error: {error}")