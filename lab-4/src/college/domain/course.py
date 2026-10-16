"""Course capability. Imports no other capability."""

from dataclasses import dataclass

from college.domain.result import ConstructionError, Failure, Success, is_integer, is_text


@dataclass(frozen=True)
class InvalidCourse:
    """A stored course row that cannot be constructed. Carries no sentence."""

    id: object


@dataclass(frozen=True)
class Course:
    """id is required. Identifier. The inscription references this identifier.

    course_code is required. Must be present. Unique among courses.
    name is required. Must be present. Not required to be unique.
    """

    id: int
    course_code: str
    name: str

    def __post_init__(self) -> None:
        if not _valid(self.id, self.course_code, self.name):
            raise ConstructionError

    @classmethod
    def create(cls, id, course_code, name):
        if not _valid(id, course_code, name):
            return Failure(InvalidCourse(id))
        return Success(cls(id, course_code, name))


def _valid(id, course_code, name) -> bool:
    return is_integer(id) and is_text(course_code) and is_text(name)
