from flask import Flask

from lab_3.adapters.outbound.sqlite.unit_of_work import (
    SqliteConnectionProvider,
    SqliteUnitOfWork,
)

from .bus import bootstrap_command_bus
from .database import bootstrap_database
from .repositories import bootstrap_repositories
from .web import bootstrap_web


def create_app() -> Flask:
    app = Flask(__name__)
    connection_factory = bootstrap_database()
    connections = SqliteConnectionProvider()
    unit_of_work = SqliteUnitOfWork(connection_factory)
    student_repository, cours_repository, inscription_repository = (
        bootstrap_repositories(connections)
    )
    command_bus = bootstrap_command_bus(
        student_repository,
        cours_repository,
        inscription_repository,
        unit_of_work,
    )
    bootstrap_web(app, command_bus)
    return app
