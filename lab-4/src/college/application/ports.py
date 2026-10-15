"""Port interfaces. Implementations live in outbound adapters."""

from typing import Protocol


class PersistenceConflict(Exception):
    """A concurrent write violated a persistence uniqueness guarantee."""


class ProgrammePort(Protocol):
    def get(self, programme_id: int):
        """Return the programme or none when it is absent."""


class StudentPort(Protocol):
    def get(self, student_id: int):
        """Return the student or none when it is absent."""


class CoursePort(Protocol):
    def get(self, course_id: int):
        """Return the course or none when it is absent."""

    def list_all(self):
        """Return every stored course."""


class InscriptionPort(Protocol):
    def find(self, student_id: int, course_id: int):
        """Return the inscription for this student and course, if any."""

    def add(self, student_id: int, course_id: int):
        """Insert an inscription with no note, or raise PersistenceConflict."""


class UnitOfWorkPort(Protocol):
    def __enter__(self):
        """Begin a write transaction."""

    def __exit__(self, exc_type, exc, tb):
        """Commit on success and roll back on failure."""
