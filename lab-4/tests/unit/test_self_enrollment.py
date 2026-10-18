"""The self-enrollment domain service owns eligibility and the FR-014 order."""

import pytest

from college.domain.course import Course
from college.domain.email import Email
from college.domain.identifiers import CourseId, InscriptionId, ProgrammeId, StudentId
from college.domain.inscription import Inscription, InvalidInscription, NewInscription
from college.domain.programme import Programme
from college.domain.self_enrollment import Refusal, decide_self_enrollment
from college.domain.student import Student

ADA = Student(StudentId(1), "Ada Lovelace", Email("ada@college.test"), ProgrammeId(1))
SCIENCE = Programme(ProgrammeId(1), "Computer Science")
CS101 = Course(CourseId(10), "CS101", "Introduction")
EXISTING = Inscription(InscriptionId(5), StudentId(1), CourseId(10), "A")
CORRUPT = InvalidInscription(5, 1, 10, b"\x00")


def _decide(**overrides):
    facts = {
        "grade_attempted": False,
        "student": ADA,
        "programme": SCIENCE,
        "course": CS101,
        "existing": None,
    }
    facts.update(overrides)
    return decide_self_enrollment(**facts)


def test_eligible_student_gets_a_new_inscription_without_a_grade():
    decision = _decide()
    assert decision == NewInscription(StudentId(1), CourseId(10))
    assert decision.stored_as(InscriptionId(7)) == Inscription(
        InscriptionId(7), StudentId(1), CourseId(10), None
    )


@pytest.mark.parametrize(
    ("overrides", "refusal"),
    [
        ({"grade_attempted": True}, Refusal.GRADE_ATTEMPT),
        ({"student": None}, Refusal.NOT_REGISTERED),
        ({"programme": None}, Refusal.NOT_REGISTERED),
        ({"course": None}, Refusal.COURSE_MISSING),
        ({"existing": EXISTING}, Refusal.ALREADY_ENROLLED),
    ],
)
def test_each_refusal(overrides, refusal):
    assert _decide(**overrides) is refusal


def test_programme_must_be_the_students_programme():
    other = Programme(ProgrammeId(2), "History")
    assert _decide(programme=other) is Refusal.NOT_REGISTERED


@pytest.mark.parametrize(
    ("overrides", "refusal"),
    [
        (
            {"grade_attempted": True, "student": None, "course": None, "existing": CORRUPT},
            Refusal.GRADE_ATTEMPT,
        ),
        ({"student": None, "course": None, "existing": EXISTING}, Refusal.NOT_REGISTERED),
        ({"course": None, "existing": EXISTING}, Refusal.COURSE_MISSING),
    ],
)
def test_first_matching_refusal_wins(overrides, refusal):
    assert _decide(**overrides) is refusal


def test_corrupt_stored_inscription_is_returned_for_the_caller_to_handle():
    assert _decide(existing=CORRUPT) == CORRUPT
