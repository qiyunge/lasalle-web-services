from __future__ import annotations

from dataclasses import dataclass

from lab_3.adapters.inbound.flask.common.request_validation import (
    RequestValidationError,
    RequestValidationErrors,
)
from lab_3.core.domain.common import Failure, Result, Success


@dataclass(frozen=True)
class CreateInscriptionRequest:
    student_id: int
    cours_id: int


def parse_create_inscription_request(
    data: object,
) -> Result[CreateInscriptionRequest, RequestValidationErrors]:
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
    student_id = data.get("student_id")
    cours_id = data.get("cours_id")

    if not isinstance(student_id, int):
        errors.append(
            RequestValidationError(
                field="student_id", message="Student ID must be an integer"
            )
        )
    if not isinstance(cours_id, int):
        errors.append(
            RequestValidationError(
                field="cours_id", message="Course ID must be an integer"
            )
        )

    if not isinstance(student_id, int) or not isinstance(cours_id, int):
        return Failure(RequestValidationErrors(tuple(errors)))
    return Success(CreateInscriptionRequest(student_id=student_id, cours_id=cours_id))
