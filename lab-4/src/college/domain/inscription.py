"""Inscription capability. Refers to a student and a course by identifier only."""

from dataclasses import dataclass

from college.domain.result import ConstructionError, Failure, Success, is_integer


@dataclass(frozen=True)
class InvalidInscription:
    """A stored inscription row that cannot be constructed. Carries no sentence."""

    id: object
    student_id: object
    course_id: object
    note: object


@dataclass(frozen=True)
class Inscription:
    """id is required. Identifier. Assigned when the inscription is created.

    student_id is required. Must reference an existing registered student.
    On self-enrollment this is the acting student.
    course_id is required. Must reference an existing course.
    note is not required. Absent when this slice creates the inscription.
    This slice never writes a note.

    Uniqueness: at most one inscription for a given (student_id, course_id).
    """

    id: int
    student_id: int
    course_id: int
    note: str | None = None

    def __post_init__(self) -> None:
        if not _valid(self.id, self.student_id, self.course_id, self.note):
            raise ConstructionError

    @classmethod
    def create(cls, id, student_id, course_id, note=None):
        if not _valid(id, student_id, course_id, note):
            return Failure(InvalidInscription(id, student_id, course_id, note))
        return Success(cls(id, student_id, course_id, note))


def _valid(id, student_id, course_id, note) -> bool:
    return (
        is_integer(id)
        and is_integer(student_id)
        and is_integer(course_id)
        and (note is None or isinstance(note, str))
    )
