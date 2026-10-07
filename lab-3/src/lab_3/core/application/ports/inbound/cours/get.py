from dataclasses import dataclass
from lab_3.core.application.command import Command
from lab_3.core.domain.value_objects import CoursId, CoursCode, CoursName
from lab_3.core.domain.common import Result
from typing import Protocol

@dataclass(frozen=True)
class GetCoursCommand(Command):
    cours_id: CoursId

@dataclass(frozen=True)
class GetCoursOutcome:
    cours_id: CoursId
    cours_code: CoursCode
    cours_name: CoursName

@dataclass(frozen=True)
class GetCoursNotFoundError:
    cours_id: CoursId

type GetCoursError = GetCoursNotFoundError
type GetCoursResult = Result[GetCoursOutcome, GetCoursError]

class GetCoursHandler(Protocol):
    def handle(self, command: GetCoursCommand) -> GetCoursResult:
        pass