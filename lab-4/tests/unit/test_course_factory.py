"""Course construction enforces a code and a name on every public path."""

import pytest

from college.domain.course import Course, InvalidCourse
from college.domain.identifiers import CourseId
from college.domain.result import ConstructionError, Failure, Success


def test_reconstitute_rejects_an_empty_or_missing_code_or_name_without_raising():
    for code, name in (("", "Introduction"), ("CS101", ""), (None, "Introduction"), ("CS101", None)):
        result = Course.reconstitute(CourseId(10), code, name)
        assert isinstance(result, Failure)
        assert isinstance(result.error, InvalidCourse)
        assert result.error.id == 10


def test_direct_construction_of_an_invalid_course_raises():
    with pytest.raises(ConstructionError):
        Course(CourseId(10), "", "Introduction")


def test_direct_construction_requires_a_course_identifier():
    with pytest.raises(ConstructionError):
        Course(10, "CS101", "Introduction")


def test_valid_reconstitute_returns_the_course():
    result = Course.reconstitute(CourseId(10), "CS101", "Introduction")
    assert isinstance(result, Success)
    assert result.value == Course(CourseId(10), "CS101", "Introduction")


def test_course_has_no_raw_primitive_factory():
    assert not hasattr(Course, "create")
