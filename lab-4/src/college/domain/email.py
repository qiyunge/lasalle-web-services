"""Student email value object."""

from dataclasses import dataclass
from typing import Self

from college.domain.result import ConstructionError, Failure, Success
from college.domain.text import is_present


@dataclass(frozen=True)
class InvalidEmail:
    """A value that cannot be a student email. Carries no sentence."""

    value: object


@dataclass(frozen=True)
class Email:
    """Required and present. Compared exactly as stored.

    The specification states no address format, so none is checked.
    Uniqueness spans students and is guaranteed by storage, not here.
    """

    value: str

    def __post_init__(self) -> None:
        if not is_present(self.value):
            raise ConstructionError

    @classmethod
    def create(cls, value: object) -> Success[Self] | Failure[InvalidEmail]:
        if not is_present(value):
            return Failure(InvalidEmail(value))
        return Success(cls(value))
