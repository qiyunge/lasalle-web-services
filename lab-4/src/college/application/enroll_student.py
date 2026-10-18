"""Self-enrollment use case.

1. Validate the input contract into a command of domain types, collecting
   every independent input failure.
2. Inside one transaction, load the facts and ask the domain service for
   the decision.
3. Store the new inscription, or report the refusal.

The use case does not decide eligibility and does not use HTTP terms.
"""

from dataclasses import dataclass
from enum import StrEnum
from typing import Final

from college.application.ports import EnrollmentPorts, PersistenceConflict
from college.domain.identifiers import CourseId, StudentId
from college.domain.inscription import Inscription, InvalidInscription, NewInscription
from college.domain.result import Failure, Success
from college.domain.self_enrollment import Refusal, decide_self_enrollment


class _Absent:
    """Marks a field the request did not supply."""


ABSENT: Final = _Absent()

ENROLLED: Final = "You are enrolled in this course."
STORED_INVALID: Final = "Stored inscription data is invalid."
MESSAGES: Final = {
    Refusal.GRADE_ATTEMPT: "Students cannot assign, change, or remove a grade.",
    Refusal.NOT_REGISTERED: "Only a registered student can enroll in a course.",
    Refusal.COURSE_MISSING: "That course does not exist.",
    Refusal.ALREADY_ENROLLED: "You are already enrolled in this course.",
}


@dataclass(frozen=True)
class SelfEnrollmentRequest:
    """Application input contract. Values are unvalidated primitives.

    acting_student_id comes from the trusted caller context. student_id is
    not accepted; it is carried only so validation can reject it. note is
    read after validation: any present value is a grade attempt.
    """

    acting_student_id: object
    course_id: object
    student_id: object = ABSENT
    note: object = ABSENT


@dataclass(frozen=True)
class ValidationError:
    """One independent input-validation failure. Not a business refusal."""

    code: str
    field: str


@dataclass(frozen=True)
class EnrollInCourse:
    """Validated command. Domain types only."""

    acting_student_id: StudentId
    course_id: CourseId


class Outcome(StrEnum):
    ENROLLED = "enrolled"
    INVALID_INPUT = "invalid_input"
    REFUSED = "refused"
    INTEGRITY = "integrity"


@dataclass(frozen=True)
class EnrollmentResult:
    outcome: Outcome
    message: str = ""
    refusal: Refusal | None = None
    inscription: Inscription | None = None
    errors: tuple[ValidationError, ...] = ()


def _required[I: (StudentId, CourseId)](
    value: object, field: str, kind: type[I]
) -> I | ValidationError:
    """A missing value is not also reported as not an integer."""
    if value is None:
        return ValidationError(f"{field}_missing", field)
    created = kind.create(value)
    if isinstance(created, Failure):
        return ValidationError(f"{field}_not_integer", field)
    return created.value


def validate(request: SelfEnrollmentRequest) -> EnrollInCourse | tuple[ValidationError, ...]:
    """Collect every independent input failure, in contract order. Do not stop at the first."""
    acting = _required(request.acting_student_id, "acting_student_id", StudentId)
    course = _required(request.course_id, "course_id", CourseId)
    errors = [value for value in (acting, course) if isinstance(value, ValidationError)]
    if request.student_id is not ABSENT:
        errors.append(ValidationError("target_student_not_accepted", "student_id"))
    if isinstance(acting, StudentId) and isinstance(course, CourseId) and not errors:
        return EnrollInCourse(acting, course)
    return tuple(errors)


def enroll(request: SelfEnrollmentRequest, ports: EnrollmentPorts) -> EnrollmentResult:
    command = validate(request)
    if not isinstance(command, EnrollInCourse):
        return EnrollmentResult(Outcome.INVALID_INPUT, errors=command)
    grade_attempted = request.note is not ABSENT
    try:
        with ports.unit_of_work:
            decision = _decide_from_storage(command, grade_attempted, ports)
            if isinstance(decision, Refusal):
                return _refused(decision)
            if isinstance(decision, InvalidInscription):
                ports.unit_of_work.rollback()
                return EnrollmentResult(Outcome.INTEGRITY, STORED_INVALID)
            created = ports.inscriptions.add(decision)
    except PersistenceConflict:
        return _refused(Refusal.ALREADY_ENROLLED)
    return EnrollmentResult(Outcome.ENROLLED, ENROLLED, inscription=created)


def _refused(refusal: Refusal) -> EnrollmentResult:
    return EnrollmentResult(Outcome.REFUSED, MESSAGES[refusal], refusal)


def _found[T](result: Success[T] | Failure[object]) -> T | None:
    """A missing or incomplete record is not an existing one."""
    return result.value if isinstance(result, Success) else None


def _decide_from_storage(
    command: EnrollInCourse, grade_attempted: bool, ports: EnrollmentPorts
) -> NewInscription | Refusal | InvalidInscription:
    student = _found(ports.students.get(command.acting_student_id))
    programme = _found(ports.programmes.get(student.programme_id)) if student else None
    course = _found(ports.courses.get(command.course_id))
    stored = ports.inscriptions.find(command.acting_student_id, command.course_id)
    existing: Inscription | InvalidInscription | None = _found(stored)
    if isinstance(stored, Failure) and isinstance(stored.error, InvalidInscription):
        existing = stored.error
    return decide_self_enrollment(
        grade_attempted=grade_attempted,
        student=student,
        programme=programme,
        course=course,
        existing=existing,
    )
