"""HTTP contract tests for GET /courses."""

import sqlite3

from college.app import create_app
from college.adapters.outbound.sqlite_unit_of_work import initialize_schema


def _path(tmp_path, courses):
    path = tmp_path / "college.sqlite"
    connection = sqlite3.connect(path)
    initialize_schema(connection)
    for course_id, code, name in courses:
        connection.execute(
            "INSERT INTO course (id, course_code, name) VALUES (?, ?, ?)",
            (course_id, code, name),
        )
    connection.commit()
    connection.close()
    return path


def test_lists_courses_by_code(tmp_path):
    path = _path(
        tmp_path,
        [
            (2, "CS102", "Introduction"),
            (1, "CS101", "Introduction"),
            (3, "", "Blank code"),
        ],
    )
    response = create_app(str(path)).test_client().get("/courses")
    assert response.status_code == 200
    assert response.get_json() == {
        "courses": [
            {"id": 1, "course_code": "CS101", "name": "Introduction"},
            {"id": 2, "course_code": "CS102", "name": "Introduction"},
        ]
    }


def test_empty_course_list(tmp_path):
    path = _path(tmp_path, [])
    response = create_app(str(path)).test_client().get("/courses")
    assert response.status_code == 200
    assert response.get_json() == {"courses": []}
