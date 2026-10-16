"""Acceptance tests for browsing courses."""

from college.application.browse_courses import browse
from college.application.ports import CourseList
from college.domain.course import Course, InvalidCourse


class Catalog:
    def __init__(self, courses, invalid=()):
        self.courses = courses
        self.invalid = invalid

    def list_all(self):
        return CourseList(tuple(self.courses), tuple(self.invalid))

    def get(self, course_id):
        for course in self.courses:
            if course.id == course_id:
                return course
        return None


def test_every_course_is_shown_in_code_order():
    shown = browse(
        Catalog(
            [
                Course(2, "CS102", "Introduction"),
                Course(1, "CS101", "Introduction"),
            ]
        )
    ).courses
    assert [(course.id, course.course_code, course.name) for course in shown] == [
        (1, "CS101", "Introduction"),
        (2, "CS102", "Introduction"),
    ]


def test_course_outside_a_programme_is_shown():
    shown = browse(Catalog([Course(1, "HIST200", "History")])).courses
    assert [course.course_code for course in shown] == ["HIST200"]


def test_already_enrolled_course_is_still_shown():
    shown = browse(Catalog([Course(1, "CS101", "Introduction")])).courses
    assert [course.id for course in shown] == [1]


def test_empty_catalog():
    assert browse(Catalog([])).courses == ()


class Batch:
    def list_all(self):
        return CourseList(
            courses=(Course(3, "CS102", "Networks"),),
            invalid=(InvalidCourse(1),),
        )


def test_invalid_stored_course_stays_on_the_batch():
    result = browse(Batch())
    assert [course.id for course in result.courses] == [3]
    assert result.invalid == (InvalidCourse(1),)


def test_course_without_code_or_name_is_not_shown():
    result = browse(
        Catalog(
            [Course(3, "CS102", "Networks")],
            invalid=(
                InvalidCourse(1),
                InvalidCourse(2),
                InvalidCourse(4),
                InvalidCourse(5),
            ),
        )
    )
    assert [course.id for course in result.courses] == [3]
    assert result.invalid == (
        InvalidCourse(1),
        InvalidCourse(2),
        InvalidCourse(4),
        InvalidCourse(5),
    )
