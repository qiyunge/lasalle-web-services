from flask import Flask
from .database import bootstrap_database
from .repositories import bootstrap_repositories
from .bus import bootstrap_command_bus
from .web import bootstrap_web

def create_app() -> Flask:
    app = Flask(__name__)
    connection = bootstrap_database()
    student_repository, cours_repository, inscription_repository = bootstrap_repositories(connection)
    
    command_bus = bootstrap_command_bus(student_repository, cours_repository, inscription_repository)
    bootstrap_web(app, command_bus)
    return app