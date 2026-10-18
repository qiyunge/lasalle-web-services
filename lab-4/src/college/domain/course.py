"""Course capability. Imports no other capability."""

from dataclasses import dataclass

from college.domain.identifiers import CourseId
from college.domain.result import ConstructionError, Failure, Success
from college.domain.text import is_present


@dataclass(frozen=True)
class InvalidCourse:
    """A stored course that cannot be constructed. id is the stored value."""

    id: object


@dataclass(frozen=True)
class Course:
    """id is required. course_code is required, present, and unique.

    name is required and present. Names may repeat. Code uniqueness spans
    courses and is guaranteed by storage. This feature does not create
    courses, so the only factory rebuilds a stored one.
    """

    id: CourseId
    course_code: str
    name: str

    def __post_init__(self) -> None:
        if not (
            isinstance(self.id, CourseId)
            and is_present(self.course_code)
            and is_present(self.name)
        ):
            raise ConstructionError

    @classmethod
    def reconstitute(
        cls, id: CourseId, course_code: object, name: object
    ) -> Success["Course"] | Failure[InvalidCourse]:
        if not (is_present(course_code) and is_present(name)):
            return Failure(InvalidCourse(id.value))
        return Success(cls(id, course_code, name))
