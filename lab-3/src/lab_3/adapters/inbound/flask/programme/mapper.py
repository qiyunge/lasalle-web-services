    
from dataclasses import dataclass

from lab_3.core.domain.value_objects import ProgrammeName
from lab_3.core.domain.common import Failure, Success
from lab_3.core.application.ports.inbound.programmes.create import (
    CreateProgrammeCommand,
    CreateProgrammeResult,
)
from lab_3.core.domain.common.validation import ValidationErrors

from lab_3.adapters.inbound.flask.programme.response import CreateProgrammeResponse
from lab_3.core.application.ports.inbound.programmes.list import (
    ProgrammeListResult,
  
)
from lab_3.core.domain.common.validation import ValidationErrors
from lab_3.adapters.inbound.flask.common.error_mapper import HttpErrorResponse
#create programme request 
from .request import CreateProgrammeRequest
from lab_3.core.application.ports.inbound.programmes.create import ProgrammeNameAlreadyExists,ProgrammeCreationFailed


def to_programme_list_response(result: ProgrammeListResult) -> list[dict]:
    return [{"id": programme_item.id, "name": programme_item.name} for programme_item in result.programmes]

#create programme request




def to_create_programme_command(request: CreateProgrammeRequest) -> CreateProgrammeCommand:
    name_result = ProgrammeName.create(request.name)
    if isinstance(name_result, Failure):
        return Failure(ValidationErrors(name_result.error,))
    return Success(CreateProgrammeCommand(name=name_result.value))

def to_create_programme_response(
    result: CreateProgrammeResult,
) -> CreateProgrammeResponse:
    return CreateProgrammeResponse(
        id=result.id,
        name=result.name,
    )


def map_create_programme_error(
    error: ProgrammeCreationFailed,
) -> HttpErrorResponse:
    if isinstance(error, ProgrammeNameAlreadyExists):
        return HttpErrorResponse(
            body={
                "error": "programme_name_conflict",
                "message": f"Programme '{error.name}' already exists",
            },
            status_code=409,
        )

    raise RuntimeError(f"Unhandled create programme error: {error!r}")