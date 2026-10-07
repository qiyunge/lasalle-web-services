from __future__ import annotations

from dataclasses import dataclass

from lab_3.adapters.inbound.flask.common.request_validation import (
    RequestValidationError,
    RequestValidationErrors,
)
from lab_3.core.domain.common import Failure, Result, Success


@dataclass(frozen=True)
class CreateCoursRequest:
    cours_code: str
    cours_name: str


def parse_create_cours_request(
    data: object,
) -> Result[CreateCoursRequest, RequestValidationErrors]:
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
    cours_code = data.get("cours_code")
    cours_name = data.get("cours_name")

    if not isinstance(cours_code, str):
        errors.append(
            RequestValidationError(
                field="cours_code", message="Cours code must be a string"
            )
        )
    if not isinstance(cours_name, str):
        errors.append(
            RequestValidationError(
                field="cours_name", message="Cours name must be a string"
            )
        )
    if not isinstance(cours_code, str) or not isinstance(cours_name, str):
        return Failure(RequestValidationErrors(tuple(errors)))
    return Success(CreateCoursRequest(cours_code=cours_code, cours_name=cours_name))


@dataclass(frozen=True)
class GetCoursRequest:
    cours_id: int


@dataclass(frozen=True)
class ListCoursRequest:
    page: int
    page_size: int


def parse_list_cours_request(
    page: object,
    page_size: object,
) -> Result[ListCoursRequest, RequestValidationErrors]:
    errors: list[RequestValidationError] = []
    parsed_page = _query_int(page)
    parsed_page_size = _query_int(page_size)

    if parsed_page is None:
        errors.append(
            RequestValidationError(field="page", message="Page must be an integer")
        )
    if parsed_page_size is None:
        errors.append(
            RequestValidationError(
                field="page_size", message="Page size must be an integer"
            )
        )
    if parsed_page is None or parsed_page_size is None:
        return Failure(RequestValidationErrors(tuple(errors)))
    return Success(ListCoursRequest(page=parsed_page, page_size=parsed_page_size))


def _query_int(value: object) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        text = value.strip()
        if text.lstrip("-").isdigit():
            return int(text)
    return None


def parse_get_cours_request(
    cours_id: int,
) -> Result[GetCoursRequest, RequestValidationErrors]:
    if not isinstance(cours_id, int):
        return Failure(
            RequestValidationErrors(
                (
                    RequestValidationError(
                        field="cours_id", message="Cours ID must be an integer"
                    ),
                )
            )
        )
    return Success(GetCoursRequest(cours_id=cours_id))
