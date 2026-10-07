from __future__ import annotations
from dataclasses import dataclass
from lab_3.core.application.command import Command
from lab_3.core.domain.value_objects import CoursId, CoursCode, CoursName
from lab_3.core.domain.common import Result, Success, Failure
from typing import Protocol

@dataclass(frozen=True)
class Pagination:
    page: int
    page_size: int
    
    @classmethod
    def create(cls: type[Pagination], page: int, page_size: int) -> Result[Pagination, ValueError]:
        if page < 1:
            return Failure(ValueError("Page must be greater than 0"))
        if page_size < 1:
            return Failure(ValueError("Page size must be greater than 0"))
        return Success(cls(page, page_size))

@dataclass(frozen=True)
class ListCoursCommand(Command):
    page: int
    page_size: int
   

@dataclass(frozen=True)
class CoursListItem:
    cours_id: CoursId
    cours_code: CoursCode
    cours_name: CoursName

@dataclass(frozen=True)
class ListCoursOutcome:
    items: tuple[CoursListItem, ...]
    page:int
    page_size:int

@dataclass(frozen=True)
class ListCoursError:
    pass

type ListCoursError = ListCoursError
type ListCoursResult = Result[ListCoursOutcome, ListCoursError]

class ListCoursHandler(Protocol):
    def handle(self, command: ListCoursCommand) -> ListCoursResult:
        pass