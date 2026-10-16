"""Inscription construction enforces structure, not existence or a grade range."""

import pytest

from college.domain.inscription import Inscription, InvalidInscription
from college.domain.result import ConstructionError, Failure, Success


def test_create_rejects_a_non_integer_identifier_without_raising():
    for arguments in (
        (None, 1, 10, None),
        (1, "1", 10, None),
        (1, 1, True, None),
    ):
        result = Inscription.create(*arguments)
        assert isinstance(result, Failure)
        assert isinstance(result.error, InvalidInscription)


def test_create_rejects_a_note_that_is_not_text_without_raising():
    result = Inscription.create(1, 1, 10, 1)
    assert isinstance(result, Failure)
    assert isinstance(result.error, InvalidInscription)


def test_absent_note_and_a_grade_string_are_valid():
    for note in (None, "A"):
        result = Inscription.create(1, 1, 10, note)
        assert isinstance(result, Success)
        assert result.value == Inscription(1, 1, 10, note)


def test_create_does_not_require_the_student_or_the_course_to_exist():
    result = Inscription.create(1, 99, 99, None)
    assert isinstance(result, Success)
    assert result.value.student_id == 99
    assert result.value.course_id == 99


def test_direct_construction_of_an_invalid_inscription_raises():
    with pytest.raises(ConstructionError):
        Inscription(1, "1", 10, None)
