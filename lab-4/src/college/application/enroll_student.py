"""Self-enrollment use case. Owns eligibility, existence, and business success."""

from dataclasses import dataclass

from college.application.ports import PersistenceConflict

ENROLLED = "You are enrolled in this course."
COURSE_MISSING = "That course does not exist."
ALREADY_ENROLLED = "You are already enrolled in this course."
NOT_REGISTERED = "Only a registered student can enroll in a course."
NOT_YOURSELF = "You can only enroll yourself."
GRADE_ATTEMPT = "Students cannot assign, change, or remove a grade."
ACTOR_REQUIRED = "acting_student_id is required."
COURSE_REQUIRED = "course_id is required."
IDS_NOT_INTEGERS = "acting_student_id and course_id must be integers."


@dataclass(frozen=True)
class EnrollmentResult:
    outcome: str
    message: str
    inscription: object = None


ABSENT = object()


def _refused(outcome: str, message: str) -> EnrollmentResult:
    return EnrollmentResult(outcome, message)


def _is_integer(value) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


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
    if acting_student_id is None:
        return _refused("invalid", ACTOR_REQUIRED)
    if course_id is None:
        return _refused("invalid", COURSE_REQUIRED)
    if not (_is_integer(acting_student_id) and _is_integer(course_id)):
        return _refused("invalid", IDS_NOT_INTEGERS)
    if note is not ABSENT:
        return _refused("forbidden", GRADE_ATTEMPT)
    if student_id is not ABSENT and student_id != acting_student_id:
        return _refused("forbidden", NOT_YOURSELF)
    try:
        with unit_of_work:
            student = students.get(acting_student_id)
            if (
                student is None
                or not student.has_identity()
                or programmes.get(student.programme_id) is None
            ):
                return _refused("not_registered", NOT_REGISTERED)
            course = courses.get(course_id)
            if course is None or not course.is_complete():
                return _refused("not_found", COURSE_MISSING)
            if inscriptions.find(acting_student_id, course_id) is not None:
                return _refused("conflict", ALREADY_ENROLLED)
            created = inscriptions.add(acting_student_id, course_id)
    except PersistenceConflict:
        return _refused("conflict", ALREADY_ENROLLED)
    return EnrollmentResult("enrolled", ENROLLED, created)


enroll.ABSENT = ABSENT
