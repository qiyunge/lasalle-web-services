from typing import assert_never

from lab_3.adapters.inbound.flask.common.error_mapper import HttpErrorResponse
from lab_3.adapters.inbound.flask.cours.request import (
    CreateCoursRequest,
    GetCoursRequest,
    ListCoursRequest,
)
from lab_3.adapters.inbound.flask.cours.response import (
    CoursListItemResponse,
    CreateCoursResponse,
    GetCoursResponse,
    ListCoursResponse,
)
from lab_3.core.application.ports.inbound.cours.create import (
    CreateCoursCodeAlreadyExistsError,
    CreateCoursCommand,
    CreateCoursError,
    CreateCoursOutcome,
)
from lab_3.core.application.ports.inbound.cours.get import (
    GetCoursCommand,
    GetCoursError,
    GetCoursNotFoundError,
    GetCoursOutcome,
)
from lab_3.core.application.ports.inbound.cours.list import (
    CoursListItem,
    ListCoursCommand,
    ListCoursOutcome,
    Pagination,
)
from lab_3.core.domain.common import Failure, Result, Success, ValidationErrors, collect_errors
from lab_3.core.domain.common.validation import ValidationError
from lab_3.core.domain.value_objects import CoursCode, CoursId, CoursName


def to_create_cours_command(
    request: CreateCoursRequest,
) -> Result[CreateCoursCommand, ValidationErrors]:
    cours_code_result = CoursCode.create(request.cours_code)
    cours_name_result = CoursName.create(request.cours_name)
    errors = collect_errors(cours_code_result, cours_name_result)
    if errors:
        return Failure(ValidationErrors(tuple(errors)))

    assert isinstance(cours_code_result, Success)
    assert isinstance(cours_name_result, Success)
    return Success(
        CreateCoursCommand(
            cours_code=cours_code_result.outcome,
            cours_name=cours_name_result.outcome,
        )
    )


def to_create_cours_response(outcome: CreateCoursOutcome) -> CreateCoursResponse:
    return CreateCoursResponse(
        cours_id=outcome.course_id.value,
        cours_code=outcome.cours_code.value,
        cours_name=outcome.cours_name.value,
    )


def map_create_cours_error(error: CreateCoursError) -> HttpErrorResponse:
    match error:
        case CreateCoursCodeAlreadyExistsError(cours_code):
            return HttpErrorResponse(
                body={
                    "error": "Cours code already exists",
                    "cours_code": cours_code.value,
                },
                status_code=409,
            )
        case _:
            assert_never(error)


def to_get_cours_command(
    request: GetCoursRequest,
) -> Result[GetCoursCommand, ValidationErrors]:
    cours_id_result = CoursId.create(request.cours_id)
    errors = collect_errors(cours_id_result)
    if errors:
        return Failure(ValidationErrors(tuple(errors)))

    assert isinstance(cours_id_result, Success)
    return Success(GetCoursCommand(cours_id=cours_id_result.outcome))


def to_get_cours_response(outcome: GetCoursOutcome) -> GetCoursResponse:
    return GetCoursResponse(
        cours_id=outcome.cours_id.value,
        cours_code=outcome.cours_code.value,
        cours_name=outcome.cours_name.value,
    )


def map_get_cours_error(error: GetCoursError) -> HttpErrorResponse:
    match error:
        case GetCoursNotFoundError(cours_id):
            return HttpErrorResponse(
                body={"error": "Cours not found", "cours_id": cours_id.value},
                status_code=404,
            )
        case _:
            assert_never(error)


def to_list_cours_command(
    request: ListCoursRequest,
) -> Result[ListCoursCommand, ValidationErrors]:
    pagination_result = Pagination.create(request.page, request.page_size)
    if isinstance(pagination_result, Failure):
        message = str(pagination_result.error)
        field = "page_size" if message.startswith("Page size") else "page"
        return Failure(
            ValidationErrors((ValidationError(field=field, message=message),))
        )
    pagination = pagination_result.outcome
    return Success(
        ListCoursCommand(page=pagination.page, page_size=pagination.page_size)
    )


def to_list_cours_response(outcome: ListCoursOutcome) -> ListCoursResponse:
    return ListCoursResponse(
        items=tuple(_to_list_item(item) for item in outcome.items),
        page=outcome.page,
        page_size=outcome.page_size,
    )


def _to_list_item(item: CoursListItem) -> CoursListItemResponse:
    return CoursListItemResponse(
        cours_id=item.id.value,
        cours_code=item.code.value,
        cours_name=item.name.value,
    )
