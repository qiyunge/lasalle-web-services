"""Outbound ports. Contracts use domain types only; adapters implement them."""

from dataclasses import dataclass
from typing import Protocol, Self

from college.domain.course import Course, InvalidCourse
from college.domain.identifiers import CourseId, ProgrammeId, StudentId
from college.domain.inscription import Inscription, InvalidInscription, NewInscription
from college.domain.programme import InvalidProgramme, Programme
from college.domain.result import Failure, Success
from college.domain.student import InvalidStudent, Student


class PersistenceConflict(Exception):
    """A concurrent write violated a storage uniqueness guarantee."""


@dataclass(frozen=True)
class Missing:
    """No stored record. This is not an invalid record."""


@dataclass(frozen=True)
class CourseList:
    """Valid courses and invalid-record diagnostics from one read."""

    courses: tuple[Course, ...]
    invalid: tuple[InvalidCourse, ...]


class ProgrammePort(Protocol):
    def get(
        self, programme_id: ProgrammeId
    ) -> Success[Programme] | Failure[Missing | InvalidProgramme]: ...


class StudentPort(Protocol):
    def get(self, student_id: StudentId) -> Success[Student] | Failure[Missing | InvalidStudent]: ...


class CoursePort(Protocol):
    def get(self, course_id: CourseId) -> Success[Course] | Failure[Missing | InvalidCourse]: ...

    def list_all(self) -> CourseList: ...


class InscriptionPort(Protocol):
    def find(
        self, student_id: StudentId, course_id: CourseId
    ) -> Success[Inscription] | Failure[Missing | InvalidInscription]: ...

    def add(self, inscription: NewInscription) -> Inscription:
        """Store the inscription and return it with its identifier, or raise PersistenceConflict."""
        ...


class UnitOfWorkPort(Protocol):
    def __enter__(self) -> Self:
        """Begin one write transaction."""
        ...

    def __exit__(self, exc_type, exc, tb) -> bool:
        """Commit when the block completes, roll back when it raises or rollback was requested."""
        ...

    def rollback(self) -> None:
        """Request rollback even when the block returns without raising."""
        ...


@dataclass(frozen=True)
class EnrollmentPorts:
    """The outbound capabilities one enrollment needs, sharing one transaction."""

    programmes: ProgrammePort
    students: StudentPort
    courses: CoursePort
    inscriptions: InscriptionPort
    unit_of_work: UnitOfWorkPort
