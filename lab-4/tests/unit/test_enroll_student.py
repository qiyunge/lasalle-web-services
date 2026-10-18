"""Acceptance tests for the self-enrollment use case."""

import pytest

from college.application.enroll_student import ABSENT, SelfEnrollmentRequest, enroll
from college.application.ports import EnrollmentPorts, Missing, PersistenceConflict
from college.domain.course import Course, InvalidCourse
from college.domain.email import Email
from college.domain.identifiers import CourseId, InscriptionId, ProgrammeId, StudentId
from college.domain.inscription import Inscription, InvalidInscription
from college.domain.programme import Programme
from college.domain.result import Failure, Success
from college.domain.student import InvalidStudent, Student


def _inscription(id, student_id, course_id, note):
    return Inscription(InscriptionId(id), StudentId(student_id), CourseId(course_id), note)


class NullUnitOfWork:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def rollback(self):
        return None


class Store:
    """In-memory records keyed by the identifier's number."""

    def __init__(self, programmes, students, courses, inscriptions):
        self.programmes = programmes
        self.students = students
        self.courses = courses
        self.inscriptions = list(inscriptions)


def _lookup(records, key):
    if key.value not in records:
        return Failure(Missing())
    found = records[key.value]
    if isinstance(found, Failure):
        return found
    return Success(found)


class Programmes:
    def __init__(self, store):
        self.store = store

    def get(self, programme_id):
        return _lookup(self.store.programmes, programme_id)


class Students:
    def __init__(self, store):
        self.store = store

    def get(self, student_id):
        return _lookup(self.store.students, student_id)


class Courses:
    def __init__(self, store):
        self.store = store

    def get(self, course_id):
        return _lookup(self.store.courses, course_id)

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
                return Success(inscription)
        return Failure(Missing())

    def add(self, inscription):
        created = inscription.stored_as(InscriptionId(len(self.store.inscriptions) + 1))
        self.store.inscriptions.append(created)
        return created


class ConflictInscriptions:
    def find(self, student_id, course_id):
        return Failure(Missing())

    def add(self, inscription):
        raise PersistenceConflict


def _store():
    return Store(
        programmes={1: Programme(ProgrammeId(1), "Computer Science")},
        students={
            1: Student(StudentId(1), "Ada Lovelace", Email("ada@college.test"), ProgrammeId(1)),
            2: Student(StudentId(2), "Grace Hopper", Email("grace@college.test"), ProgrammeId(1)),
        },
        courses={
            10: Course(CourseId(10), "CS101", "Introduction"),
            11: Course(CourseId(11), "CS102", "Introduction"),
        },
        inscriptions=[],
    )


def _ports(store, inscriptions=None, unit_of_work=None):
    return EnrollmentPorts(
        programmes=Programmes(store),
        students=Students(store),
        courses=Courses(store),
        inscriptions=inscriptions or Inscriptions(store),
        unit_of_work=unit_of_work or NullUnitOfWork(),
    )


def _enroll(store, inscriptions=None, **overrides):
    payload = {
        "acting_student_id": 1,
        "course_id": 10,
        "student_id": ABSENT,
        "note": ABSENT,
    }
    payload.update(overrides)
    return enroll(SelfEnrollmentRequest(**payload), _ports(store, inscriptions))


def test_student_enrolls_without_an_administrator():
    store = _store()
    result = _enroll(store)
    assert result.message == "You are enrolled in this course."
    assert result.inscription.student_id == StudentId(1)
    assert result.inscription.course_id == CourseId(10)
    assert result.inscription.note is None
    assert len(store.inscriptions) == 1


def test_programme_does_not_block_enrollment():
    store = _store()
    result = _enroll(store, course_id=11)
    assert result.message == "You are enrolled in this course."
    assert result.inscription.course_id == CourseId(11)


def test_second_course_creates_a_separate_inscription():
    store = _store()
    first = _enroll(store)
    second = _enroll(store, course_id=11)
    assert first.inscription.course_id == CourseId(10)
    assert second.inscription.course_id == CourseId(11)
    assert len(store.inscriptions) == 2


def test_missing_course():
    store = _store()
    result = _enroll(store, course_id=99)
    assert result.message == "That course does not exist."
    assert store.inscriptions == []


def test_duplicate_leaves_existing_note_unchanged():
    store = _store()
    store.inscriptions.append(_inscription(5, 1, 10, "A"))
    result = _enroll(store)
    assert result.message == "You are already enrolled in this course."
    assert store.inscriptions == [_inscription(5, 1, 10, "A")]


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
    "stored",
    [Failure(InvalidStudent(1))] * 4,
)
def test_incomplete_student_is_not_registered(stored):
    store = _store()
    store.students[1] = stored
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
    "stored",
    [Failure(InvalidCourse(10))] * 4,
)
def test_incomplete_course_does_not_exist(stored):
    store = _store()
    store.courses[10] = stored
    result = _enroll(store)
    assert result.message == "That course does not exist."
    assert store.inscriptions == []


def _has_error(result, code, field):
    return (code, field) in [(error.code, error.field) for error in result.errors]


@pytest.mark.parametrize("student_id", [2, 1])
def test_supplied_student_id_is_not_accepted(student_id):
    store = _store()
    result = _enroll(store, student_id=student_id)
    assert _has_error(result, "target_student_not_accepted", "student_id")
    assert result.message == ""
    assert store.inscriptions == []


@pytest.mark.parametrize("note", [None, "", "A"])
def test_note_is_a_grade_attempt(note):
    store = _store()
    result = _enroll(store, note=note)
    assert result.message == "Students cannot assign, change, or remove a grade."
    assert store.inscriptions == []


def test_target_student_field_wins_over_a_grade_attempt():
    store = _store()
    result = _enroll(store, student_id=2, note="A")
    assert _has_error(result, "target_student_not_accepted", "student_id")
    assert result.message != "Students cannot assign, change, or remove a grade."
    assert store.inscriptions == []


def test_grade_attempt_wins_over_an_unregistered_student():
    store = _store()
    result = _enroll(store, acting_student_id=9, note="A")
    assert result.message == "Students cannot assign, change, or remove a grade."
    assert store.inscriptions == []


def test_grade_attempt_wins_over_a_missing_course():
    store = _store()
    result = _enroll(store, course_id=99, note="A")
    assert result.message == "Students cannot assign, change, or remove a grade."
    assert store.inscriptions == []


def test_grade_attempt_wins_over_an_existing_inscription():
    store = _store()
    store.inscriptions.append(_inscription(5, 1, 10, "A"))
    result = _enroll(store, note="A")
    assert result.message == "Students cannot assign, change, or remove a grade."
    assert store.inscriptions == [_inscription(5, 1, 10, "A")]


def test_target_student_field_wins_over_an_unregistered_student():
    store = _store()
    result = _enroll(store, acting_student_id=9, student_id=2)
    assert _has_error(result, "target_student_not_accepted", "student_id")
    assert result.message == ""
    assert store.inscriptions == []


def test_target_student_field_wins_over_a_missing_course():
    store = _store()
    result = _enroll(store, course_id=99, student_id=2)
    assert _has_error(result, "target_student_not_accepted", "student_id")
    assert result.message == ""
    assert store.inscriptions == []


def test_target_student_field_wins_over_an_existing_inscription():
    store = _store()
    store.inscriptions.append(_inscription(5, 1, 10, "A"))
    result = _enroll(store, student_id=2)
    assert _has_error(result, "target_student_not_accepted", "student_id")
    assert result.message == ""
    assert store.inscriptions == [_inscription(5, 1, 10, "A")]


def test_unregistered_student_wins_over_a_missing_course():
    store = _store()
    result = _enroll(store, acting_student_id=9, course_id=99)
    assert result.message == "Only a registered student can enroll in a course."
    assert store.inscriptions == []


def test_missing_course_wins_over_an_existing_inscription():
    store = _store()
    store.inscriptions.append(_inscription(5, 1, 99, None))
    result = _enroll(store, course_id=99)
    assert result.message == "That course does not exist."
    assert store.inscriptions == [_inscription(5, 1, 99, None)]


def test_two_students_can_enroll_in_the_same_course():
    store = _store()
    first = _enroll(store)
    second = _enroll(store, acting_student_id=2)
    assert first.message == "You are enrolled in this course."
    assert second.message == "You are enrolled in this course."
    assert {item.student_id for item in store.inscriptions} == {StudentId(1), StudentId(2)}


class InvalidInscriptions:
    def __init__(self):
        self.add_called = False

    def find(self, student_id, course_id):
        return Failure(InvalidInscription(5, student_id.value, course_id.value, b"\x00"))

    def add(self, inscription):
        self.add_called = True
        return None


class RecordingUnitOfWork:
    def __init__(self):
        self.rolled_back = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def rollback(self):
        self.rolled_back = True


def test_invalid_stored_inscription_is_an_integrity_failure():
    store = _store()
    inscriptions = InvalidInscriptions()
    work = RecordingUnitOfWork()
    result = enroll(
        SelfEnrollmentRequest(acting_student_id=1, course_id=10),
        _ports(store, inscriptions, work),
    )
    assert result.outcome == "integrity"
    assert result.message == "Stored inscription data is invalid."
    assert result.inscription is None
    assert inscriptions.add_called is False
    assert work.rolled_back is True
    grade = enroll(
        SelfEnrollmentRequest(acting_student_id=1, course_id=10, note="A"),
        _ports(store, inscriptions, RecordingUnitOfWork()),
    )
    assert grade.message == "Students cannot assign, change, or remove a grade."


def test_input_errors_accumulate_before_business_rules():
    store = _store()
    result = _enroll(
        store,
        acting_student_id=None,
        course_id=True,
        student_id=1,
        note="A",
    )
    assert [(error.code, error.field) for error in result.errors] == [
        ("acting_student_id_missing", "acting_student_id"),
        ("course_id_not_integer", "course_id"),
        ("target_student_not_accepted", "student_id"),
    ]
    assert result.message == ""
    assert store.inscriptions == []


def test_both_missing_identifiers_are_collected():
    store = _store()
    result = _enroll(store, acting_student_id=None, course_id=None)
    assert [(error.code, error.field) for error in result.errors] == [
        ("acting_student_id_missing", "acting_student_id"),
        ("course_id_missing", "course_id"),
    ]
    assert store.inscriptions == []


def test_one_missing_identifier_is_only_that_code():
    store = _store()
    result = _enroll(store, course_id=None)
    assert [(error.code, error.field) for error in result.errors] == [
        ("course_id_missing", "course_id")
    ]
    assert store.inscriptions == []
