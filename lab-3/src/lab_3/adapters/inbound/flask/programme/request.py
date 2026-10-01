from dataclasses import dataclass

from lab_3.adapters.inbound.flask.common.request_validation import (
    RequestValidationError,
    RequestValidationErrors,
)
from lab_3.core.domain.common import Failure, Result, Success


@dataclass(frozen=True)
class CreateProgrammeRequest:
    name: str


def parse_create_programme_request(
    data: object,
) -> Result[CreateProgrammeRequest, RequestValidationErrors]:
    if not isinstance(data, dict):
        return Failure(
            RequestValidationErrors(
                (
                    RequestValidationError(
                        field="body",
                        message="JSON object is required",
                    ),
                )
            )
        )

    name: object = data.get("name")

    if not isinstance(name, str):
        return Failure(
            RequestValidationErrors(
                (
                    RequestValidationError(
                        field="name",
                        message="Programme name must be a string",
                    ),
                )
            )
        )

    return Success(CreateProgrammeRequest(name=name))