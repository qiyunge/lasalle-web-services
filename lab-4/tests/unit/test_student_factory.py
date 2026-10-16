"""Student construction enforces identity on every public path."""

import pytest

from college.domain.result import ConstructionError, Failure, Success
from college.domain.student import InvalidStudent, Student


def test_create_rejects_empty_or_missing_name_without_raising():
    for name in ("", None):
        result = Student.create(1, name, "ada@college.test", 1)
        assert isinstance(result, Failure)
        assert isinstance(result.error, InvalidStudent)
        assert result.error.id == 1


def test_create_rejects_empty_or_missing_email_without_raising():
    for email in ("", None):
        result = Student.create(1, "Ada Lovelace", email, 1)
        assert isinstance(result, Failure)
        assert isinstance(result.error, InvalidStudent)


def test_create_rejects_non_integer_ids_without_raising():
    for student_id, programme_id in ((None, 1), (True, 1), (1, None), (1, False)):
        result = Student.create(student_id, "Ada Lovelace", "ada@college.test", programme_id)
        assert isinstance(result, Failure)
        assert isinstance(result.error, InvalidStudent)


def test_create_rejects_non_string_text_without_raising():
    result = Student.create(1, 1, "ada@college.test", 1)
    assert isinstance(result, Failure)
    assert isinstance(result.error, InvalidStudent)


def test_direct_construction_of_an_invalid_student_raises():
    with pytest.raises(ConstructionError):
        Student(1, "", "ada@college.test", 1)


def test_valid_create_returns_the_student():
    result = Student.create(1, "Ada Lovelace", "ada@college.test", 1)
    assert isinstance(result, Success)
    assert result.value == Student(1, "Ada Lovelace", "ada@college.test", 1)
