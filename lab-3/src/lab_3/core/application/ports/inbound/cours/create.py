from dataclasses import dataclass
from lab_3.core.application.command import Command
from lab_3.core.domain.value_objects import CoursCode, CoursName, CoursId
from lab_3.core.domain.common import Result
from typing import Protocol

@dataclass(frozen=True)
class CreateCoursCommand(Command):
    cours_code: CoursCode
    cours_name: CoursName

@dataclass(frozen=True)
class CreateCoursOutcome:
    course_id: CoursId
    cours_code: CoursCode
    cours_name: CoursName

@dataclass(frozen=True)
class CreateCoursCodeAlreadyExistsError:
    cours_code: CoursCode



type CreateCoursError = CreateCoursCodeAlreadyExistsError 
type CreateCoursResult = Result[CreateCoursOutcome, CreateCoursError]


class CreateCoursUseCase(Protocol):
    
    def handle(self, command: CreateCoursCommand) -> CreateCoursResult:...
       