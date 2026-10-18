"""Inscription capability. Refers to a student and a course by identifier only."""

from dataclasses import dataclass
from typing import TypeGuard

from college.domain.identifiers import CourseId, InscriptionId, StudentId
from college.domain.result import ConstructionError, Failure, Success


@dataclass(frozen=True)
class InvalidInscription:
    """A stored inscription that cannot be constructed. Fields are the stored values."""

    id: object
    student_id: object
    course_id: object
    note: object


def _is_note(value: object) -> TypeGuard[str | None]:
    return value is None or isinstance(value, str)


@dataclass(frozen=True)
class Inscription:
    """One student's enrollment in one course.

    note is optional. The feature states no grade range. At most one
    inscription exists for a student and a course; storage guarantees it
    across concurrent writes.
    """

    id: InscriptionId
    student_id: StudentId
    course_id: CourseId
    note: str | None = None

    def __post_init__(self) -> None:
        if not (
            isinstance(self.id, InscriptionId)
            and isinstance(self.student_id, StudentId)
            and isinstance(self.course_id, CourseId)
            and _is_note(self.note)
        ):
            raise ConstructionError

    @classmethod
    def reconstitute(
        cls, id: InscriptionId, student_id: StudentId, course_id: CourseId, note: object
    ) -> Success["Inscription"] | Failure[InvalidInscription]:
        if not _is_note(note):
            return Failure(InvalidInscription(id.value, student_id.value, course_id.value, note))
        return Success(cls(id, student_id, course_id, note))


@dataclass(frozen=True)
class NewInscription:
    """An enrollment the domain has decided and storage has not yet assigned an id.

    It has no note, so a new inscription never carries a grade.
    """

    student_id: StudentId
    course_id: CourseId

    def __post_init__(self) -> None:
        if not (isinstance(self.student_id, StudentId) and isinstance(self.course_id, CourseId)):
            raise ConstructionError

    def stored_as(self, id: InscriptionId) -> Inscription:
        return Inscription(id, self.student_id, self.course_id, None)
