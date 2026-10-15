"""Concurrent enrollment leaves one inscription and its note unchanged."""

import sqlite3
import threading

import pytest

from college.app import create_app
from college.adapters.outbound.sqlite_inscription_repository import (
    SqliteInscriptionRepository,
)
from college.adapters.outbound.sqlite_unit_of_work import (
    SqliteUnitOfWork,
    initialize_schema,
    open_connection,
)
from college.application.ports import PersistenceConflict


def _seed(path):
    connection = sqlite3.connect(path)
    initialize_schema(connection)
    connection.execute("INSERT INTO programme (id) VALUES (1)")
    connection.execute(
        "INSERT INTO student (id, name, email, programme_id) VALUES (1, 'Ada', 'ada@college.test', 1)"
    )
    connection.execute(
        "INSERT INTO course (id, course_code, name) VALUES (10, 'CS101', 'Introduction')"
    )
    connection.commit()
    connection.close()


def test_concurrent_enrollment_keeps_one_inscription(tmp_path):
    path = tmp_path / "college.sqlite"
    _seed(path)
    barrier = threading.Barrier(2)
    results = []

    def attempt():
        client = create_app(str(path)).test_client()
        barrier.wait()
        response = client.post(
            "/inscriptions",
            json={"acting_student_id": 1, "course_id": 10},
        )
        results.append((response.status_code, response.get_json()["message"]))

    threads = [threading.Thread(target=attempt) for _ in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert sorted(results) == [
        (201, "You are enrolled in this course."),
        (409, "You are already enrolled in this course."),
    ]
    connection = sqlite3.connect(path)
    rows = connection.execute(
        "SELECT student_id, course_id, note FROM inscription"
    ).fetchall()
    connection.close()
    assert rows == [(1, 10, None)]


def test_duplicate_insert_is_a_conflict_and_rolls_back(tmp_path):
    path = tmp_path / "college.sqlite"
    _seed(path)
    connection = open_connection(str(path))
    connection.execute(
        "INSERT INTO inscription (student_id, course_id, note) VALUES (1, 10, 'A')"
    )
    repository = SqliteInscriptionRepository(connection)
    with pytest.raises(PersistenceConflict):
        with SqliteUnitOfWork(connection):
            repository.add(1, 10)
    rows = connection.execute(
        "SELECT student_id, course_id, note FROM inscription"
    ).fetchall()
    connection.close()
    assert [tuple(row) for row in rows] == [(1, 10, "A")]
