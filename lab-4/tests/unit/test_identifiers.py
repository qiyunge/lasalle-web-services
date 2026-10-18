"""Identifier types accept an integer and reject anything else."""

import pytest

from college.domain.identifiers import (
    CourseId,
    InscriptionId,
    InvalidIdentifier,
    ProgrammeId,
    StudentId,
)
from college.domain.result import ConstructionError, Failure, Success

KINDS = [StudentId, CourseId, ProgrammeId, InscriptionId]


@pytest.mark.parametrize("kind", KINDS)
def test_create_accepts_an_integer(kind):
    assert kind.create(1) == Success(kind(1))


@pytest.mark.parametrize("kind", KINDS)
@pytest.mark.parametrize("value", [None, True, False, "1", 1.5])
def test_create_rejects_a_non_integer(kind, value):
    assert kind.create(value) == Failure(InvalidIdentifier(value))
    with pytest.raises(ConstructionError):
        kind(value)


def test_identifiers_of_different_kinds_are_never_equal():
    assert StudentId(1) != CourseId(1)
    assert StudentId(1) != ProgrammeId(1)
    assert InscriptionId(1) != StudentId(1)
