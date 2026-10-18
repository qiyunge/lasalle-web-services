"""Programme construction requires an identifier and a nonempty name."""

import pytest

from college.domain.identifiers import ProgrammeId
from college.domain.programme import InvalidProgramme, Programme
from college.domain.result import ConstructionError, Failure, Success


def test_valid_programme_is_returned():
    programme = Programme(ProgrammeId(1), "Computer Science")
    assert programme.id == ProgrammeId(1)
    assert programme.name == "Computer Science"


@pytest.mark.parametrize("programme_id", [None, True, 1])
def test_constructor_requires_a_programme_identifier(programme_id):
    with pytest.raises(ConstructionError):
        Programme(programme_id, "Computer Science")


def test_empty_name_does_not_return():
    with pytest.raises(ConstructionError):
        Programme(ProgrammeId(1), "")


def test_reconstitute_returns_success_for_a_valid_programme():
    assert Programme.reconstitute(ProgrammeId(1), "Computer Science") == Success(
        Programme(ProgrammeId(1), "Computer Science")
    )


@pytest.mark.parametrize("name", ["", None, 1])
def test_reconstitute_returns_failure_without_raising(name):
    result = Programme.reconstitute(ProgrammeId(1), name)
    assert result == Failure(InvalidProgramme(1))


def test_programme_has_no_raw_primitive_factory():
    assert not hasattr(Programme, "create")
