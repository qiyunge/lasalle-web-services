"""Student capability. Refers to a programme by identifier only."""

from dataclasses import dataclass

from college.domain.email import Email
from college.domain.identifiers import ProgrammeId, StudentId
from college.domain.result import ConstructionError, Failure, Success
from college.domain.text import is_present


@dataclass(frozen=True)
class InvalidStudent:
    """A stored student that cannot be constructed. id is the stored value."""

    id: object


@dataclass(frozen=True)
class Student:
    """id is required. name is required and present. email is required.

    programme_id must reference an existing programme. Programme existence
    and email uniqueness span other records, so the self-enrollment
    service and storage check them, not this entity.

    This feature does not register students, so the only factory
    rebuilds a stored one.
    """

    id: StudentId
    name: str
    email: Email
    programme_id: ProgrammeId

    def __post_init__(self) -> None:
        if not (
            isinstance(self.id, StudentId)
            and isinstance(self.email, Email)
            and isinstance(self.programme_id, ProgrammeId)
            and is_present(self.name)
        ):
            raise ConstructionError

    @classmethod
    def reconstitute(
        cls, id: StudentId, name: object, email: Email, programme_id: ProgrammeId
    ) -> Success["Student"] | Failure[InvalidStudent]:
        """Value objects arrive validated. A raw one raises from the constructor."""
        if not is_present(name):
            return Failure(InvalidStudent(id.value))
        return Success(cls(id, name, email, programme_id))
