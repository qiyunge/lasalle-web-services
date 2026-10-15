"""Acceptance tests for browsing courses."""

from college.application.browse_courses import browse
from college.domain.course import Course


class Catalog:
    def __init__(self, courses):
        self.courses = courses

    def list_all(self):
        return list(self.courses)

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
    )
    assert [(course.id, course.course_code, course.name) for course in shown] == [
        (1, "CS101", "Introduction"),
        (2, "CS102", "Introduction"),
    ]


def test_course_outside_a_programme_is_shown():
    shown = browse(Catalog([Course(1, "HIST200", "History")]))
    assert [course.course_code for course in shown] == ["HIST200"]


def test_already_enrolled_course_is_still_shown():
    shown = browse(Catalog([Course(1, "CS101", "Introduction")]))
    assert [course.id for course in shown] == [1]


def test_empty_catalog():
    assert browse(Catalog([])) == []


def test_course_without_code_or_name_is_not_shown():
    shown = browse(
        Catalog(
            [
                Course(1, "", "Introduction"),
                Course(2, "CS101", ""),
                Course(4, None, "History"),
                Course(5, "CS100", None),
                Course(3, "CS102", "Networks"),
            ]
        )
    )
    assert [course.id for course in shown] == [3]
