from __future__ import annotations

from typing import Protocol
from lab_3.core.domain.common import Result

from lab_3.core.domain.value_objects import CoursId, CoursCode, CoursName
from lab_3.core.domain import Cours
from dataclasses import dataclass

@dataclass(frozen=True)
class GetCoursNotFoundPersistenceError:
    id: CoursId

@dataclass(frozen=True)
class CreateCoursCodeAlreadyExistsPersistenceError:
    code: CoursCode

@dataclass(frozen=True)
class CreateCoursIdConflictPersistenceError:
    code: CoursCode

@dataclass(frozen=True)
class ListCoursPersistenceError:
    pass
   
type CreateCoursPersistenceError = CreateCoursCodeAlreadyExistsPersistenceError | CreateCoursIdConflictPersistenceError
type GetCoursPersistenceError = GetCoursNotFoundPersistenceError
type ListCoursPersistenceError = ListCoursPersistenceError
type GetCoursPersistenceResult = Result[Cours, GetCoursPersistenceError]
type CreateCoursPersistenceResult = Result[Cours, CreateCoursPersistenceError]
type ListCoursPersistenceResult = Result[tuple[Cours, ...], ListCoursPersistenceError]

class CoursRepository(Protocol):
    def exists(self, id: CoursId) -> bool: ...
    def find_by_id(self, id: CoursId) -> GetCoursPersistenceResult: ...
    def find_all(self, offset: int, limit: int) -> tuple[Cours, ...]: ...
    def save(self, cours: Cours) -> CreateCoursPersistenceResult: ...
