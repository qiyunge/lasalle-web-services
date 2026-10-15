"""Course capability. Imports no other capability."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Course:
    """id is required. Identifier. The inscription references this identifier.

    course_code is required. Must be present. Unique among courses.
    name is required. Must be present. Not required to be unique.
    """

    id: int
    course_code: str
    name: str

    def is_complete(self) -> bool:
        return _present(self.course_code) and _present(self.name)


def _present(value) -> bool:
    return isinstance(value, str) and value != ""
