"""Course construction enforces a code and a name on every public path."""

import pytest

from college.domain.course import Course, InvalidCourse
from college.domain.result import ConstructionError, Failure, Success


def test_create_rejects_a_non_integer_id_without_raising():
    for course_id in (None, True, "10"):
        result = Course.create(course_id, "CS101", "Introduction")
        assert isinstance(result, Failure)
        assert isinstance(result.error, InvalidCourse)


def test_create_rejects_an_empty_or_missing_code_or_name_without_raising():
    for code, name in (("", "Introduction"), ("CS101", ""), (None, "Introduction"), ("CS101", None)):
        result = Course.create(10, code, name)
        assert isinstance(result, Failure)
        assert isinstance(result.error, InvalidCourse)
        assert result.error.id == 10


def test_direct_construction_of_an_invalid_course_raises():
    with pytest.raises(ConstructionError):
        Course(10, "", "Introduction")


def test_valid_create_returns_the_course():
    result = Course.create(10, "CS101", "Introduction")
    assert isinstance(result, Success)
    assert result.value == Course(10, "CS101", "Introduction")
