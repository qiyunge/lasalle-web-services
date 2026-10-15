"""Inscription capability. Refers to a student and a course by identifier only."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Inscription:
    """id is required. Identifier. Assigned when the inscription is created.

    student_id is required. Must reference an existing registered student.
    On self-enrollment this is the acting student.
    course_id is required. Must reference an existing course.
    note is not required. Absent when this slice creates the inscription.
    This slice never writes a note.

    Uniqueness: at most one inscription for a given (student_id, course_id).
    """

    id: int
    student_id: int
    course_id: int
    note: str | None = None
