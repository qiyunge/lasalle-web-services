"""Self-enrollment use case. Owns eligibility, existence, and business success."""

from dataclasses import dataclass

from college.application.ports import PersistenceConflict
from college.domain.inscription import InvalidInscription
from college.domain.result import Failure, Success

ENROLLED = "You are enrolled in this course."
COURSE_MISSING = "That course does not exist."
ALREADY_ENROLLED = "You are already enrolled in this course."
NOT_REGISTERED = "Only a registered student can enroll in a course."
NOT_YOURSELF = "You can only enroll yourself."
GRADE_ATTEMPT = "Students cannot assign, change, or remove a grade."
STORED_INVALID = "Stored inscription data is invalid."


@dataclass(frozen=True)
class EnrollmentResult:
    outcome: str
    message: str
    inscription: object = None


ABSENT = object()


def _refused(outcome: str, message: str) -> EnrollmentResult:
    return EnrollmentResult(outcome, message)


def enroll(
    acting_student_id,
    course_id,
    *,
    student_id=ABSENT,
    note=ABSENT,
    programmes,
    students,
    courses,
    inscriptions,
    unit_of_work,
) -> EnrollmentResult:
    if note is not ABSENT:
        return _refused("forbidden", GRADE_ATTEMPT)
    if student_id is not ABSENT and student_id != acting_student_id:
        return _refused("forbidden", NOT_YOURSELF)
    try:
        with unit_of_work:
            student_result = students.get(acting_student_id)
            if isinstance(student_result, Failure) or not isinstance(
                programmes.get(student_result.value.programme_id), Success
            ):
                return _refused("not_registered", NOT_REGISTERED)
            if isinstance(courses.get(course_id), Failure):
                return _refused("not_found", COURSE_MISSING)
            found = inscriptions.find(acting_student_id, course_id)
            if isinstance(found, Failure) and isinstance(found.error, InvalidInscription):
                unit_of_work.rollback()
                return EnrollmentResult("integrity", STORED_INVALID)
            if isinstance(found, Success):
                return _refused("conflict", ALREADY_ENROLLED)
            created = inscriptions.add(acting_student_id, course_id)
    except PersistenceConflict:
        return _refused("conflict", ALREADY_ENROLLED)
    return EnrollmentResult("enrolled", ENROLLED, created)


enroll.ABSENT = ABSENT
