"""Identifier value objects. Each type accepts or rejects one value."""

from dataclasses import dataclass
from typing import Self, TypeGuard

from college.domain.result import ConstructionError, Failure, Success


@dataclass(frozen=True)
class InvalidIdentifier:
    """A value that cannot identify anything. Carries no sentence."""

    value: object


def _is_integer(value: object) -> TypeGuard[int]:
    return isinstance(value, int) and not isinstance(value, bool)


@dataclass(frozen=True)
class _Identifier:
    """An integer identifier. A boolean is not an integer.

    Equality includes the type, so identifiers of different kinds with
    the same number are never equal.
    """

    value: int

    def __post_init__(self) -> None:
        if not _is_integer(self.value):
            raise ConstructionError

    @classmethod
    def create(cls, value: object) -> Success[Self] | Failure[InvalidIdentifier]:
        if not _is_integer(value):
            return Failure(InvalidIdentifier(value))
        return Success(cls(value))


@dataclass(frozen=True)
class StudentId(_Identifier):
    """Identifies a student."""


@dataclass(frozen=True)
class CourseId(_Identifier):
    """Identifies a course."""


@dataclass(frozen=True)
class ProgrammeId(_Identifier):
    """Identifies a programme."""


@dataclass(frozen=True)
class InscriptionId(_Identifier):
    """Identifies an inscription. Assigned when the inscription is stored."""
