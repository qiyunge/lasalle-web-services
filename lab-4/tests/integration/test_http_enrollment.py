"""HTTP contract tests for POST /inscriptions."""

import sqlite3

import pytest
from contextlib import contextmanager

from flask import Flask

from college.adapters.inbound.http import create_blueprint
from college.app import create_app
from college.adapters.outbound.sqlite_unit_of_work import initialize_schema
from college.application.ports import EnrollmentPorts
from college.domain.course import Course
from college.domain.email import Email
from college.domain.identifiers import CourseId, ProgrammeId, StudentId
from college.domain.inscription import InvalidInscription
from college.domain.programme import Programme
from college.domain.result import Failure, Success
from college.domain.student import Student


def _database(tmp_path):
    path = tmp_path / "college.sqlite"
    connection = sqlite3.connect(path)
    initialize_schema(connection)
    connection.execute(
        "INSERT INTO programme (id, name) VALUES (1, 'Computer Science')"
    )
    connection.execute(
        "INSERT INTO student (id, name, email, programme_id) VALUES (1, 'Ada', 'ada@college.test', 1)"
    )
    connection.execute(
        "INSERT INTO student (id, name, email, programme_id) VALUES (2, 'Grace', 'grace@college.test', 1)"
    )
    connection.execute(
        "INSERT INTO course (id, course_code, name) VALUES (10, 'CS101', 'Introduction')"
    )
    connection.commit()
    connection.close()
    return path


def _client(path):
    return create_app(str(path)).test_client()


def _rows(path):
    connection = sqlite3.connect(path)
    rows = connection.execute(
        "SELECT student_id, course_id, note FROM inscription ORDER BY id"
    ).fetchall()
    connection.close()
    return rows


def test_enroll_returns_created_inscription(tmp_path):
    path = _database(tmp_path)
    response = _client(path).post(
        "/inscriptions",
        json={"acting_student_id": 1, "course_id": 10},
    )
    assert response.status_code == 201
    body = response.get_json()
    assert body["message"] == "You are enrolled in this course."
    assert body["inscription"]["student_id"] == 1
    assert body["inscription"]["course_id"] == 10
    assert body["inscription"]["note"] is None
    assert isinstance(body["inscription"]["id"], int)
    assert _rows(path) == [(1, 10, None)]


def test_missing_course(tmp_path):
    path = _database(tmp_path)
    response = _client(path).post(
        "/inscriptions",
        json={"acting_student_id": 1, "course_id": 99},
    )
    assert response.status_code == 404
    assert response.get_json() == {"message": "That course does not exist."}
    assert _rows(path) == []


def test_duplicate_and_existing_note(tmp_path):
    path = _database(tmp_path)
    connection = sqlite3.connect(path)
    connection.execute(
        "INSERT INTO inscription (student_id, course_id, note) VALUES (1, 10, 'A')"
    )
    connection.commit()
    connection.close()
    response = _client(path).post(
        "/inscriptions",
        json={"acting_student_id": 1, "course_id": 10},
    )
    assert response.status_code == 409
    assert response.get_json() == {
        "message": "You are already enrolled in this course."
    }
    assert _rows(path) == [(1, 10, "A")]


def test_not_registered(tmp_path):
    path = _database(tmp_path)
    response = _client(path).post(
        "/inscriptions",
        json={"acting_student_id": 9, "course_id": 10},
    )
    assert response.status_code == 400
    assert response.get_json() == {
        "message": "Only a registered student can enroll in a course."
    }
    assert _rows(path) == []


def test_student_without_a_programme(tmp_path):
    path = _database(tmp_path)
    connection = sqlite3.connect(path)
    connection.execute("DELETE FROM programme")
    connection.commit()
    connection.close()
    response = _client(path).post(
        "/inscriptions",
        json={"acting_student_id": 1, "course_id": 10},
    )
    assert response.status_code == 400
    assert response.get_json() == {
        "message": "Only a registered student can enroll in a course."
    }


def test_enroll_other_student(tmp_path):
    path = _database(tmp_path)
    response = _client(path).post(
        "/inscriptions",
        json={"acting_student_id": 1, "course_id": 10, "student_id": 2},
    )
    assert response.status_code == 400
    assert response.get_json() == {
        "errors": [{"code": "target_student_not_accepted", "field": "student_id"}]
    }
    assert "message" not in response.get_json()
    assert _rows(path) == []


def test_equal_student_id_is_not_accepted(tmp_path):
    path = _database(tmp_path)
    response = _client(path).post(
        "/inscriptions",
        json={"acting_student_id": 1, "course_id": 10, "student_id": 1},
    )
    assert response.status_code == 400
    assert response.get_json() == {
        "errors": [{"code": "target_student_not_accepted", "field": "student_id"}]
    }
    assert _rows(path) == []


def test_programme_without_a_nonempty_name(tmp_path):
    path = _database(tmp_path)
    connection = sqlite3.connect(path)
    connection.execute("UPDATE programme SET name = '' WHERE id = 1")
    connection.commit()
    connection.close()
    response = _client(path).post(
        "/inscriptions",
        json={"acting_student_id": 1, "course_id": 10},
    )
    assert response.status_code == 400
    assert response.get_json() == {
        "message": "Only a registered student can enroll in a course."
    }
    assert _rows(path) == []


@pytest.mark.parametrize("note", [None, "", "A"])
def test_grade_attempt(tmp_path, note):
    path = _database(tmp_path)
    response = _client(path).post(
        "/inscriptions",
        json={"acting_student_id": 1, "course_id": 10, "note": note},
    )
    assert response.status_code == 400
    assert response.get_json() == {
        "message": "Students cannot assign, change, or remove a grade."
    }
    assert _rows(path) == []


def test_required_fields(tmp_path):
    client = _client(_database(tmp_path))
    missing_actor = client.post("/inscriptions", json={"course_id": 10})
    assert missing_actor.status_code == 400
    assert missing_actor.get_json() == {"message": "acting_student_id is required."}
    missing_course = client.post("/inscriptions", json={"acting_student_id": 1})
    assert missing_course.status_code == 400
    assert missing_course.get_json() == {"message": "course_id is required."}
    bad_type = client.post(
        "/inscriptions",
        json={"acting_student_id": "1", "course_id": 10},
    )
    assert bad_type.status_code == 400
    assert bad_type.get_json() == {
        "message": "acting_student_id and course_id must be integers."
    }
    fraction = client.post(
        "/inscriptions",
        json={"acting_student_id": 1.5, "course_id": 10},
    )
    assert fraction.status_code == 400
    assert fraction.get_json() == {
        "message": "acting_student_id and course_id must be integers."
    }
    boolean_course = client.post(
        "/inscriptions",
        json={"acting_student_id": 1, "course_id": True},
    )
    assert boolean_course.status_code == 400
    assert boolean_course.get_json() == {
        "message": "acting_student_id and course_id must be integers."
    }


def test_invalid_stored_inscription_is_internal_failure():
    class Found:
        def find(self, student_id, course_id):
            return Failure(InvalidInscription(1, student_id, course_id, None))

        def add(self, student_id, course_id):
            raise AssertionError("add must not run")

    class Students:
        def get(self, student_id):
            return Success(
                Student(StudentId(1), "Ada", Email("ada@college.test"), ProgrammeId(1))
            )

    class Courses:
        def get(self, course_id):
            return Success(Course(CourseId(10), "CS101", "Introduction"))

    class Programmes:
        def get(self, programme_id):
            return Success(Programme(ProgrammeId(1), "Computer Science"))

    class Work:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def rollback(self):
            return None

    @contextmanager
    def enrollment_ports():
        yield EnrollmentPorts(
            programmes=Programmes(),
            students=Students(),
            courses=Courses(),
            inscriptions=Found(),
            unit_of_work=Work(),
        )

    @contextmanager
    def course_port():
        yield None

    application = Flask(__name__)
    application.register_blueprint(create_blueprint(enrollment_ports, course_port))
    response = application.test_client().post(
        "/inscriptions",
        json={"acting_student_id": 1, "course_id": 10},
    )
    assert response.status_code == 500
    assert response.get_json() == {"message": "Stored inscription data is invalid."}
    assert "inscription" not in response.get_json()


def test_both_identifiers_missing_is_an_errors_array(tmp_path):
    response = _client(_database(tmp_path)).post("/inscriptions", json={})
    assert response.status_code == 400
    assert response.get_json() == {
        "errors": [
            {"code": "acting_student_id_missing", "field": "acting_student_id"},
            {"code": "course_id_missing", "field": "course_id"},
        ]
    }


def test_target_student_field_accumulates_with_an_identifier_error(tmp_path):
    path = _database(tmp_path)
    response = _client(path).post(
        "/inscriptions",
        json={"acting_student_id": 1, "student_id": 1, "note": "A"},
    )
    assert response.status_code == 400
    assert response.get_json() == {
        "errors": [
            {"code": "course_id_missing", "field": "course_id"},
            {"code": "target_student_not_accepted", "field": "student_id"},
        ]
    }
    assert _rows(path) == []


def test_body_that_is_not_a_json_object(tmp_path):
    client = _client(_database(tmp_path))
    not_json = client.post(
        "/inscriptions", data="hello", content_type="text/plain"
    )
    assert not_json.status_code == 400
    assert not_json.get_json() == {
        "errors": [
            {"code": "acting_student_id_missing", "field": "acting_student_id"},
            {"code": "course_id_missing", "field": "course_id"},
        ]
    }
    a_list = client.post("/inscriptions", json=[1, 10])
    assert a_list.status_code == 400
    assert a_list.get_json() == {
        "errors": [
            {"code": "acting_student_id_missing", "field": "acting_student_id"},
            {"code": "course_id_missing", "field": "course_id"},
        ]
    }
