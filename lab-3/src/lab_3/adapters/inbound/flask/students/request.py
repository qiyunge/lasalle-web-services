from __future__ import annotations

from dataclasses import dataclass

from lab_3.adapters.inbound.flask.common.request_validation import (
    RequestValidationError,
    RequestValidationErrors,
)
from lab_3.core.domain.common import Failure, Result, Success

@dataclass(frozen=True)
class CreateStudentRequest:
    name: str
    email: str
    programme_id: int

def parse_create_student_request(data: object) -> Result[CreateStudentRequest, RequestValidationErrors]:
    if not isinstance(data, dict):
        return Failure(
            RequestValidationErrors(
                (
                    RequestValidationError(
                        field="body", message="JSON object is required"
                    ),
                )
            )
        ) 
    errors: list[RequestValidationError] = []
    name = data.get("name")
    email = data.get("email")
    programme_id = data.get("programme_id")

    if not isinstance(name, str):
        errors.append(
            RequestValidationError(
                field="name", message="Name must be a string"
            )
        )
    if not isinstance(email, str):
        errors.append(
            RequestValidationError(
                field="email", message="Email must be a string"
            )
        )
    if not isinstance(programme_id, int):
        errors.append(
            RequestValidationError(
                field="programme_id", message="Programme ID must be an integer"
            )
        )
    if errors:
        return Failure(RequestValidationErrors(tuple(errors)))
    return Success(CreateStudentRequest(name=name, email=email, programme_id=programme_id))