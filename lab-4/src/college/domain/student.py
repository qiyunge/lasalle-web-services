"""Student capability. Imports no other capability."""

from dataclasses import dataclass


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

    def has_identity(self) -> bool:
        return _present(self.name) and _present(self.email)


def _present(value) -> bool:
    return isinstance(value, str) and value != ""
