from __future__ import annotations

from dataclasses import dataclass

from lab_3.core.domain.common.validation import ValidationErrors

from .request_validation import RequestValidationErrors


@dataclass(frozen=True)
class HttpErrorResponse:
    body: dict
    status_code: int


def map_request_errors(errors: RequestValidationErrors) -> HttpErrorResponse:
    return _validation_response(errors.errors)


def map_validation_errors(errors: ValidationErrors) -> HttpErrorResponse:
    return _validation_response(errors.errors)


def _validation_response(errors: tuple) -> HttpErrorResponse:
    return HttpErrorResponse(
        body={
            "errors": [
                {"field": error.field, "message": error.message} for error in errors
            ]
        },
        status_code=400,
    )
