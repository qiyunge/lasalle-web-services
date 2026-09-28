from __future__ import annotations
from dataclasses import dataclass

from .request_validation import RequestValidationErrors

@dataclass(frozen=True)
class HttpErrorResponse:
    body:dict
    status_code: int

def map_request_errors(errors: RequestValidationErrors) -> HttpErrorResponse:
    return HttpErrorResponse(body={'errors': [{'field': error.field, 'message': error.message} for error in errors.errors]},
                         status_code=400)