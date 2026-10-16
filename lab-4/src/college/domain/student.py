"""Student capability. Imports no other capability."""

from dataclasses import dataclass

from college.domain.result import ConstructionError, Failure, Success, is_integer, is_text


@dataclass(frozen=True)
class InvalidStudent:
    """A stored student row that cannot be constructed. Carries no sentence."""

    id: object


@dataclass(frozen=True)
class Student:
    """id is required. Identifier.

    name is required. Must be present.
    email is required. Must be present. Unique among students.
    programme_id is required. Must reference an existing programme.

    A text value is present when it is a non-empty string. Uniqueness
    compares the stored value exactly.
    """

    id: int
    name: str
    email: str
    programme_id: int

    def __post_init__(self) -> None:
        if not _valid(self.id, self.name, self.email, self.programme_id):
            raise ConstructionError

    @classmethod
    def create(cls, id, name, email, programme_id):
        if not _valid(id, name, email, programme_id):
            return Failure(InvalidStudent(id))
        return Success(cls(id, name, email, programme_id))


def _valid(id, name, email, programme_id) -> bool:
    return is_integer(id) and is_integer(programme_id) and is_text(name) and is_text(email)
