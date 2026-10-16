"""Repositories report missing and invalid stored rows as Result values."""

from college.adapters.outbound.sqlite_course_repository import SqliteCourseRepository
from college.adapters.outbound.sqlite_inscription_repository import (
    SqliteInscriptionRepository,
)
from college.adapters.outbound.sqlite_programme_repository import (
    SqliteProgrammeRepository,
)
from college.adapters.outbound.sqlite_student_repository import SqliteStudentRepository
from college.adapters.outbound.sqlite_unit_of_work import initialize_schema, open_connection
from college.application.ports import Missing
from college.domain.course import Course, InvalidCourse
from college.domain.inscription import Inscription
from college.domain.programme import Programme
from college.domain.result import Failure, Success
from college.domain.student import InvalidStudent, Student


def _connection(tmp_path):
    connection = open_connection(str(tmp_path / "college.sqlite"))
    initialize_schema(connection)
    return connection


def test_empty_student_name_is_an_invalid_record(tmp_path):
    connection = _connection(tmp_path)
    connection.execute(
        "INSERT INTO student (id, name, email, programme_id) VALUES (1, '', 'ada@college.test', 1)"
    )
    connection.commit()
    result = SqliteStudentRepository(connection).get(1)
    assert result == Student.create(1, "", "ada@college.test", 1)
    assert isinstance(result, Failure)
    assert isinstance(result.error, InvalidStudent)
    connection.close()


def test_missing_student_is_not_an_entity(tmp_path):
    connection = _connection(tmp_path)
    result = SqliteStudentRepository(connection).get(9)
    assert isinstance(result, Failure)
    assert isinstance(result.error, Missing)
    connection.close()


def test_empty_course_code_is_an_invalid_record(tmp_path):
    connection = _connection(tmp_path)
    connection.execute(
        "INSERT INTO course (id, course_code, name) VALUES (10, '', 'Introduction')"
    )
    connection.commit()
    result = SqliteCourseRepository(connection).get(10)
    assert result == Course.create(10, "", "Introduction")
    assert isinstance(result.error, InvalidCourse)
    connection.close()


def test_programme_is_present_or_missing(tmp_path):
    connection = _connection(tmp_path)
    connection.execute("INSERT INTO programme (id) VALUES (1)")
    connection.commit()
    repository = SqliteProgrammeRepository(connection)
    assert repository.get(1) == Success(Programme(1))
    missing = repository.get(2)
    assert isinstance(missing, Failure)
    assert isinstance(missing.error, Missing)
    connection.close()


def test_rollback_discards_the_open_transaction(tmp_path):
    connection = _connection(tmp_path)
    from college.adapters.outbound.sqlite_unit_of_work import SqliteUnitOfWork

    work = SqliteUnitOfWork(connection)
    with work:
        connection.execute("INSERT INTO programme (id) VALUES (1)")
        work.rollback()
    row = connection.execute("SELECT id FROM programme WHERE id = 1").fetchone()
    assert row is None
    connection.close()


def test_invalid_inscription_is_returned_unchanged(tmp_path):
    connection = _connection(tmp_path)
    connection.execute(
        "INSERT INTO inscription (id, student_id, course_id, note) VALUES (4, 'bad', 10, NULL)"
    )
    connection.commit()
    stored = connection.execute(
        "SELECT id, student_id, course_id, note FROM inscription WHERE id = 4"
    ).fetchone()
    expected = Inscription.create(
        stored["id"], stored["student_id"], stored["course_id"], stored["note"]
    )
    assert isinstance(expected, Failure)
    found = SqliteInscriptionRepository(connection).find(stored["student_id"], stored["course_id"])
    assert found == expected
    connection.close()
