"""Port interfaces. Implementations live in outbound adapters."""

from dataclasses import dataclass
from typing import Protocol


class PersistenceConflict(Exception):
    """A concurrent write violated a persistence uniqueness guarantee."""


@dataclass(frozen=True)
class Missing:
    """No stored row. This is not an invalid record."""


@dataclass(frozen=True)
class CourseList:
    """Valid courses and invalid-row diagnostics from one read.

    Course fields stay on the Course entities. This value does not copy them.
    """

    courses: tuple
    invalid: tuple


class ProgrammePort(Protocol):
    def get(self, programme_id: int):
        """Return Success(Programme) or Failure(Missing)."""


class StudentPort(Protocol):
    def get(self, student_id: int):
        """Return Success(Student), Failure(Missing), or Failure(InvalidStudent)."""


class CoursePort(Protocol):
    def get(self, course_id: int):
        """Return Success(Course), Failure(Missing), or Failure(InvalidCourse)."""

    def list_all(self):
        """Return CourseList: valid courses and InvalidCourse diagnostics."""


class InscriptionPort(Protocol):
    def find(self, student_id: int, course_id: int):
        """Return Success(Inscription), Failure(Missing), or Failure(InvalidInscription)."""

    def add(self, student_id: int, course_id: int):
        """Insert an inscription with no note, or raise PersistenceConflict."""


class UnitOfWorkPort(Protocol):
    def __enter__(self):
        """Begin a write transaction."""

    def __exit__(self, exc_type, exc, tb):
        """Commit on success and roll back on failure."""

    def rollback(self):
        """Request rollback even when the block returns without raising."""
