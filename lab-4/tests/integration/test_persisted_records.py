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
from college.domain.course import InvalidCourse
from college.domain.email import Email
from college.domain.identifiers import CourseId, InscriptionId, ProgrammeId, StudentId
from college.domain.inscription import Inscription, InvalidInscription
from college.domain.programme import InvalidProgramme, Programme
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
    result = SqliteStudentRepository(connection).get(StudentId(1))
    assert result == Failure(InvalidStudent(1))
    connection.close()


def test_stored_student_with_an_invalid_programme_identifier_is_an_invalid_record(tmp_path):
    connection = _connection(tmp_path)
    connection.execute(
        "INSERT INTO student (id, name, email, programme_id) VALUES (1, 'Ada', 'ada@college.test', 'abc')"
    )
    connection.commit()
    result = SqliteStudentRepository(connection).get(StudentId(1))
    assert result == Failure(InvalidStudent(1))
    connection.close()


def test_valid_stored_student_is_reconstituted_with_identifier_types(tmp_path):
    connection = _connection(tmp_path)
    connection.execute(
        "INSERT INTO student (id, name, email, programme_id) VALUES (1, 'Ada', 'ada@college.test', 2)"
    )
    connection.commit()
    result = SqliteStudentRepository(connection).get(StudentId(1))
    assert result == Success(
        Student(StudentId(1), "Ada", Email("ada@college.test"), ProgrammeId(2))
    )
    connection.close()


def test_empty_student_email_is_an_invalid_record(tmp_path):
    connection = _connection(tmp_path)
    connection.execute(
        "INSERT INTO student (id, name, email, programme_id) VALUES (1, 'Ada', '', 1)"
    )
    connection.commit()
    result = SqliteStudentRepository(connection).get(StudentId(1))
    assert result == Failure(InvalidStudent(1))
    connection.close()


def test_missing_student_is_not_an_entity(tmp_path):
    connection = _connection(tmp_path)
    result = SqliteStudentRepository(connection).get(StudentId(9))
    assert isinstance(result, Failure)
    assert isinstance(result.error, Missing)
    connection.close()


def test_empty_course_code_is_an_invalid_record(tmp_path):
    connection = _connection(tmp_path)
    connection.execute(
        "INSERT INTO course (id, course_code, name) VALUES (10, '', 'Introduction')"
    )
    connection.commit()
    result = SqliteCourseRepository(connection).get(CourseId(10))
    assert result == Failure(InvalidCourse(10))
    connection.close()


def test_programme_is_present_or_missing(tmp_path):
    connection = _connection(tmp_path)
    connection.execute(
        "INSERT INTO programme (id, name) VALUES (1, 'Computer Science')"
    )
    connection.commit()
    repository = SqliteProgrammeRepository(connection)
    assert repository.get(ProgrammeId(1)) == Success(
        Programme(ProgrammeId(1), "Computer Science")
    )
    missing = repository.get(ProgrammeId(2))
    assert isinstance(missing, Failure)
    assert isinstance(missing.error, Missing)
    connection.execute("INSERT INTO programme (id, name) VALUES (3, '')")
    connection.commit()
    assert repository.get(ProgrammeId(3)) == Failure(InvalidProgramme(3))
    connection.close()


def test_rollback_discards_the_open_transaction(tmp_path):
    connection = _connection(tmp_path)
    from college.adapters.outbound.sqlite_unit_of_work import SqliteUnitOfWork

    work = SqliteUnitOfWork(connection)
    with work:
        connection.execute(
            "INSERT INTO programme (id, name) VALUES (1, 'Computer Science')"
        )
        work.rollback()
    row = connection.execute("SELECT id FROM programme WHERE id = 1").fetchone()
    assert row is None
    connection.close()


def test_invalid_inscription_is_returned_unchanged(tmp_path):
    connection = _connection(tmp_path)
    connection.execute(
        "INSERT INTO inscription (id, student_id, course_id, note) VALUES (4, 1, 10, X'00')"
    )
    connection.commit()
    found = SqliteInscriptionRepository(connection).find(StudentId(1), CourseId(10))
    assert found == Failure(InvalidInscription(4, 1, 10, b"\x00"))
    connection.close()


def test_valid_stored_inscription_is_reconstituted_with_identifier_types(tmp_path):
    connection = _connection(tmp_path)
    connection.execute(
        "INSERT INTO inscription (id, student_id, course_id, note) VALUES (4, 1, 10, 'A')"
    )
    connection.commit()
    found = SqliteInscriptionRepository(connection).find(StudentId(1), CourseId(10))
    assert found == Success(Inscription(InscriptionId(4), StudentId(1), CourseId(10), "A"))
    connection.close()
