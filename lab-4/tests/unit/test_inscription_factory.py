"""Inscription construction enforces structure, not existence or a grade range."""

import pytest

from college.domain.identifiers import CourseId, InscriptionId, StudentId
from college.domain.inscription import Inscription, InvalidInscription, NewInscription
from college.domain.result import ConstructionError, Failure, Success

ID = InscriptionId(1)
ADA = StudentId(1)
CS101 = CourseId(10)


def test_reconstitute_rejects_a_note_that_is_not_text_without_raising():
    result = Inscription.reconstitute(ID, ADA, CS101, 1)
    assert result == Failure(InvalidInscription(1, 1, 10, 1))


def test_absent_note_and_a_grade_string_are_valid():
    for note in (None, "A"):
        result = Inscription.reconstitute(ID, ADA, CS101, note)
        assert isinstance(result, Success)
        assert result.value == Inscription(ID, ADA, CS101, note)


def test_reconstitute_does_not_require_the_student_or_the_course_to_exist():
    result = Inscription.reconstitute(ID, StudentId(99), CourseId(99), None)
    assert isinstance(result, Success)
    assert result.value.student_id == StudentId(99)
    assert result.value.course_id == CourseId(99)


def test_direct_construction_of_an_invalid_inscription_raises():
    with pytest.raises(ConstructionError):
        Inscription(ID, "1", CS101, None)


def test_direct_construction_requires_an_inscription_identifier():
    with pytest.raises(ConstructionError):
        Inscription(1, ADA, CS101, None)


def test_new_inscription_is_stored_without_a_grade():
    created = NewInscription(ADA, CS101).stored_as(InscriptionId(4))
    assert created == Inscription(InscriptionId(4), ADA, CS101, None)


def test_new_inscription_requires_identifier_types():
    with pytest.raises(ConstructionError):
        NewInscription(1, CS101)


def test_inscription_has_no_raw_primitive_factory():
    assert not hasattr(Inscription, "create")
