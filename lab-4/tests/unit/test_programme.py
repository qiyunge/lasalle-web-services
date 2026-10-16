"""Programme construction checks the identifier only."""

import pytest

from college.domain.programme import Programme
from college.domain.result import ConstructionError


def test_valid_programme_is_returned():
    assert Programme(1).id == 1


def test_invalid_programme_does_not_return():
    with pytest.raises(ConstructionError):
        Programme(None)


def test_boolean_id_is_not_an_integer():
    with pytest.raises(ConstructionError):
        Programme(True)
