"""Student invariants and reconstitution from validated value objects."""

import pytest

from college.domain.email import Email
from college.domain.identifiers import ProgrammeId, StudentId
from college.domain.result import ConstructionError, Failure, Success
from college.domain.student import InvalidStudent, Student

ADA_ID = StudentId(1)
ADA_EMAIL = Email("ada@college.test")
SCIENCE_ID = ProgrammeId(1)


def test_reconstitute_rejects_empty_or_missing_name_without_raising():
    for name in ("", None):
        result = Student.reconstitute(ADA_ID, name, ADA_EMAIL, SCIENCE_ID)
        assert result == Failure(InvalidStudent(1))


def test_reconstitute_rejects_non_string_name_without_raising():
    result = Student.reconstitute(ADA_ID, 1, ADA_EMAIL, SCIENCE_ID)
    assert result == Failure(InvalidStudent(1))


def test_valid_reconstitute_returns_the_student():
    result = Student.reconstitute(ADA_ID, "Ada Lovelace", ADA_EMAIL, SCIENCE_ID)
    assert result == Success(Student(ADA_ID, "Ada Lovelace", ADA_EMAIL, SCIENCE_ID))


def test_reconstitute_does_not_accept_raw_identifiers():
    with pytest.raises(ConstructionError):
        Student.reconstitute(1, "Ada Lovelace", ADA_EMAIL, 1)


def test_direct_construction_of_an_invalid_student_raises():
    with pytest.raises(ConstructionError):
        Student(ADA_ID, "", ADA_EMAIL, SCIENCE_ID)


def test_direct_construction_requires_identifier_types():
    with pytest.raises(ConstructionError):
        Student(1, "Ada Lovelace", ADA_EMAIL, 1)


def test_direct_construction_requires_an_email_value_object():
    with pytest.raises(ConstructionError):
        Student(ADA_ID, "Ada Lovelace", "ada@college.test", SCIENCE_ID)


def test_student_has_no_raw_primitive_factory():
    assert not hasattr(Student, "create")
