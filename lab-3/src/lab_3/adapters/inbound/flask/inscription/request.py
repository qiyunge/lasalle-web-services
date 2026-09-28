from __future__ import annotations

from dataclasses import dataclass
from lab_3.core.domain.common import Result, Success, Failure

from lab_3.adapters.inbound.flask.common.request_validation import RequestValidationErrors, RequestValidationError

@dataclass(frozen=True)
class CreateInscriptionRequest:
    student_id: int
    course_id: int

def parse_create_inscription_request(data: dict ) -> Result[CreateInscriptionRequest, RequestValidationErrors]:
    errors: list[RequestValidationError] = []
    student_id = data.get('student_id')
    course_id = data.get('course_id')

    if not isinstance(student_id, int):
        errors.append(RequestValidationError(field='student_id', message='Student ID must be an integer'))
    if not isinstance(course_id, int):
        errors.append(RequestValidationError(field='course_id', message='Course ID must be an integer'))

    if errors:
        return Failure(RequestValidationErrors(tuple(errors)))
    return Success(CreateInscriptionRequest(student_id=student_id, course_id=course_id))