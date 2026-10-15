"""Acceptance tests for self-enrollment. These fail until the use case exists."""

import pytest

from college.application.enroll_student import enroll
from college.application.ports import PersistenceConflict
from college.domain.course import Course
from college.domain.inscription import Inscription
from college.domain.programme import Programme
from college.domain.student import Student


class NullUnitOfWork:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class Store:
    def __init__(self, programmes, students, courses, inscriptions):
        self.programmes = programmes
        self.students = students
        self.courses = courses
        self.inscriptions = list(inscriptions)


class Programmes:
    def __init__(self, store):
        self.store = store

    def get(self, programme_id):
        return self.store.programmes.get(programme_id)


class Students:
    def __init__(self, store):
        self.store = store

    def get(self, student_id):
        return self.store.students.get(student_id)


class Courses:
    def __init__(self, store):
        self.store = store

    def get(self, course_id):
        return self.store.courses.get(course_id)

    def list_all(self):
        return list(self.store.courses.values())


class Inscriptions:
    def __init__(self, store):
        self.store = store

    def find(self, student_id, course_id):
        for inscription in self.store.inscriptions:
            if (
                inscription.student_id == student_id
                and inscription.course_id == course_id
            ):
                return inscription
        return None

    def add(self, student_id, course_id):
        created = Inscription(
            id=len(self.store.inscriptions) + 1,
            student_id=student_id,
            course_id=course_id,
            note=None,
        )
        self.store.inscriptions.append(created)
        return created


class ConflictInscriptions:
    def find(self, student_id, course_id):
        return None

    def add(self, student_id, course_id):
        raise PersistenceConflict


def _store():
    return Store(
        programmes={1: Programme(1)},
        students={
            1: Student(1, "Ada Lovelace", "ada@college.test", 1),
            2: Student(2, "Grace Hopper", "grace@college.test", 1),
        },
        courses={
            10: Course(10, "CS101", "Introduction"),
            11: Course(11, "CS102", "Introduction"),
        },
        inscriptions=[],
    )


def _enroll(store, inscriptions=None, **overrides):
    payload = {
        "acting_student_id": 1,
        "course_id": 10,
        "student_id": enroll.ABSENT,
        "note": enroll.ABSENT,
    }
    payload.update(overrides)
    return enroll(
        payload["acting_student_id"],
        payload["course_id"],
        student_id=payload["student_id"],
        note=payload["note"],
        programmes=Programmes(store),
        students=Students(store),
        courses=Courses(store),
        inscriptions=inscriptions or Inscriptions(store),
        unit_of_work=NullUnitOfWork(),
    )


def test_student_enrolls_without_an_administrator():
    store = _store()
    result = _enroll(store)
    assert result.message == "You are enrolled in this course."
    assert result.inscription.student_id == 1
    assert result.inscription.course_id == 10
    assert result.inscription.note is None
    assert len(store.inscriptions) == 1


def test_programme_does_not_block_enrollment():
    store = _store()
    result = _enroll(store, course_id=11)
    assert result.message == "You are enrolled in this course."
    assert result.inscription.course_id == 11


def test_second_course_creates_a_separate_inscription():
    store = _store()
    first = _enroll(store)
    second = _enroll(store, course_id=11)
    assert first.inscription.course_id == 10
    assert second.inscription.course_id == 11
    assert len(store.inscriptions) == 2


def test_missing_course():
    store = _store()
    result = _enroll(store, course_id=99)
    assert result.message == "That course does not exist."
    assert store.inscriptions == []


def test_duplicate_leaves_existing_note_unchanged():
    store = _store()
    store.inscriptions.append(Inscription(5, 1, 10, "A"))
    result = _enroll(store)
    assert result.message == "You are already enrolled in this course."
    assert store.inscriptions == [Inscription(5, 1, 10, "A")]


def test_persistence_conflict_is_already_enrolled():
    store = _store()
    result = _enroll(store, inscriptions=ConflictInscriptions())
    assert result.message == "You are already enrolled in this course."
    assert result.inscription is None


def test_missing_student_is_not_registered():
    store = _store()
    result = _enroll(store, acting_student_id=9)
    assert result.message == "Only a registered student can enroll in a course."
    assert store.inscriptions == []


@pytest.mark.parametrize(
    "student",
    [
        Student(1, "", "ada@college.test", 1),
        Student(1, "Ada", "", 1),
        Student(1, None, "ada@college.test", 1),
        Student(1, "Ada", None, 1),
    ],
)
def test_incomplete_student_is_not_registered(student):
    store = _store()
    store.students[1] = student
    result = _enroll(store)
    assert result.message == "Only a registered student can enroll in a course."
    assert store.inscriptions == []


def test_missing_programme_is_not_registered():
    store = _store()
    store.programmes.clear()
    result = _enroll(store)
    assert result.message == "Only a registered student can enroll in a course."
    assert store.inscriptions == []


@pytest.mark.parametrize(
    "course",
    [
        Course(10, "", "Introduction"),
        Course(10, "CS101", ""),
        Course(10, None, "Introduction"),
        Course(10, "CS101", None),
    ],
)
def test_incomplete_course_does_not_exist(course):
    store = _store()
    store.courses[10] = course
    result = _enroll(store)
    assert result.message == "That course does not exist."
    assert store.inscriptions == []


def test_enroll_other_student():
    store = _store()
    result = _enroll(store, student_id=2)
    assert result.message == "You can only enroll yourself."
    assert store.inscriptions == []


def test_same_student_id_is_self_enrollment():
    store = _store()
    result = _enroll(store, student_id=1)
    assert result.message == "You are enrolled in this course."


@pytest.mark.parametrize("note", [None, "A"])
def test_note_is_a_grade_attempt(note):
    store = _store()
    result = _enroll(store, note=note)
    assert result.message == "Students cannot assign, change, or remove a grade."
    assert store.inscriptions == []


def test_grade_attempt_wins_over_enrolling_someone_else():
    store = _store()
    result = _enroll(store, student_id=2, note="A")
    assert result.message == "Students cannot assign, change, or remove a grade."


def test_two_students_can_enroll_in_the_same_course():
    store = _store()
    first = _enroll(store)
    second = _enroll(store, acting_student_id=2)
    assert first.message == "You are enrolled in this course."
    assert second.message == "You are enrolled in this course."
    assert {item.student_id for item in store.inscriptions} == {1, 2}


def test_missing_acting_student_id():
    result = _enroll(_store(), acting_student_id=None)
    assert result.message == "acting_student_id is required."


def test_missing_course_id():
    result = _enroll(_store(), course_id=None)
    assert result.message == "course_id is required."


@pytest.mark.parametrize(
    "overrides",
    [
        {"acting_student_id": 1.5},
        {"course_id": True},
        {"acting_student_id": "1"},
    ],
)
def test_ids_must_be_integers(overrides):
    result = _enroll(_store(), **overrides)
    assert result.message == "acting_student_id and course_id must be integers."
