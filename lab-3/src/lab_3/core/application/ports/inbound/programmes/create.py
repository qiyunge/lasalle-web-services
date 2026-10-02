from dataclasses import dataclass

from lab_3.core.application.command import Command
from lab_3.core.domain.value_objects import ProgrammeName
from lab_3.core.domain.common import Result

@dataclass(frozen=True)
class CreateProgrammeOutcome:
    id: int
    name: str


@dataclass(frozen=True)
class CreateProgrammeCommand(Command[CreateProgrammeOutcome]):
    name: ProgrammeName

@dataclass(frozen=True)
class ProgrammeNameAlreadyExists:
    name: ProgrammeName

@dataclass(frozen=True)
class ProgrammeNameConflictException(Exception):
    pass

type ProgrammeCreationError = (
     ProgrammeNameAlreadyExists
)

CreateProgrammeResult = Result[CreateProgrammeOutcome, ProgrammeCreationError] 