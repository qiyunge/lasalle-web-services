"""Email is required and present. Uniqueness spans students and is not checked here."""

import pytest

from college.domain.email import Email, InvalidEmail
from college.domain.result import ConstructionError, Failure, Success


def test_create_accepts_a_present_address():
    assert Email.create("ada@college.test") == Success(Email("ada@college.test"))


@pytest.mark.parametrize("value", ["", None, 1])
def test_create_rejects_a_missing_or_empty_address(value):
    assert Email.create(value) == Failure(InvalidEmail(value))
    with pytest.raises(ConstructionError):
        Email(value)


def test_addresses_compare_exactly_as_stored():
    assert Email("ada@college.test") != Email("Ada@college.test")
