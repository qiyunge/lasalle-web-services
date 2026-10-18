"""Composition root. The only production module that constructs adapters."""

from collections.abc import Iterator
from contextlib import contextmanager

from flask import Flask

from college.adapters.inbound.http import create_blueprint
from college.adapters.outbound.sqlite_course_repository import SqliteCourseRepository
from college.adapters.outbound.sqlite_inscription_repository import (
    SqliteInscriptionRepository,
)
from college.adapters.outbound.sqlite_programme_repository import (
    SqliteProgrammeRepository,
)
from college.adapters.outbound.sqlite_student_repository import SqliteStudentRepository
from college.adapters.outbound.sqlite_unit_of_work import (
    SqliteUnitOfWork,
    initialize_schema,
    open_connection,
)
from college.application.ports import EnrollmentPorts

DEFAULT_DATABASE = "college.sqlite"

DEVELOPMENT_SEED = """
INSERT OR IGNORE INTO programme (id, name) VALUES (1, 'Computer Science');
INSERT OR IGNORE INTO student (id, name, email, programme_id)
    VALUES (1, 'Ada Lovelace', 'ada@college.test', 1);
INSERT OR IGNORE INTO student (id, name, email, programme_id)
    VALUES (2, 'Grace Hopper', 'grace@college.test', 1);
INSERT OR IGNORE INTO course (id, course_code, name)
    VALUES (1, 'CS101', 'Introduction to Computer Science');
INSERT OR IGNORE INTO course (id, course_code, name)
    VALUES (2, 'CS102', 'Introduction to Computer Science');
"""


def create_app(database: str = DEFAULT_DATABASE) -> Flask:
    application = Flask(__name__)
    application.config["DATABASE"] = database
    connection = open_connection(database)
    try:
        initialize_schema(connection)
    finally:
        connection.close()

    @contextmanager
    def enrollment_ports() -> Iterator[EnrollmentPorts]:
        connection = open_connection(database)
        try:
            yield EnrollmentPorts(
                programmes=SqliteProgrammeRepository(connection),
                students=SqliteStudentRepository(connection),
                courses=SqliteCourseRepository(connection),
                inscriptions=SqliteInscriptionRepository(connection),
                unit_of_work=SqliteUnitOfWork(connection),
            )
        finally:
            connection.close()

    @contextmanager
    def course_port() -> Iterator[SqliteCourseRepository]:
        connection = open_connection(database)
        try:
            yield SqliteCourseRepository(connection)
        finally:
            connection.close()

    application.register_blueprint(create_blueprint(enrollment_ports, course_port))
    return application


def seed_development(database: str = DEFAULT_DATABASE) -> None:
    """Load one programme, two students, and two courses for the manual check."""
    connection = open_connection(database)
    try:
        initialize_schema(connection)
        connection.executescript(DEVELOPMENT_SEED)
    finally:
        connection.close()
