"""Self-enrollment domain service.

Eligibility spans the student, programme, course, and inscription
capabilities, so the decision lives here rather than in one entity.
The caller loads the facts. This module decides.
"""

from enum import Enum

from college.domain.course import Course
from college.domain.inscription import Inscription, InvalidInscription, NewInscription
from college.domain.programme import Programme
from college.domain.student import Student


class Refusal(Enum):
    """Business refusals in FR-014 first-match order. Carries no sentence."""

    GRADE_ATTEMPT = "grade_attempt"
    NOT_REGISTERED = "not_registered"
    COURSE_MISSING = "course_missing"
    ALREADY_ENROLLED = "already_enrolled"


def is_registered(student: Student, programme: Programme | None) -> bool:
    """A complete student is registered when their own programme exists."""
    return programme is not None and programme.id == student.programme_id


def decide_self_enrollment(
    *,
    grade_attempted: bool,
    student: Student | None,
    programme: Programme | None,
    course: Course | None,
    existing: Inscription | InvalidInscription | None,
) -> NewInscription | Refusal | InvalidInscription:
    """Return the first refusal, an unreadable stored inscription, or the new inscription.

    student, programme, and course are None when missing or incomplete.
    programme is the one the student refers to. existing is the stored
    inscription for this student and course.
    """
    if grade_attempted:
        return Refusal.GRADE_ATTEMPT
    if student is None or not is_registered(student, programme):
        return Refusal.NOT_REGISTERED
    if course is None:
        return Refusal.COURSE_MISSING
    if isinstance(existing, InvalidInscription):
        return existing
    if existing is not None:
        return Refusal.ALREADY_ENROLLED
    return NewInscription(student.id, course.id)
