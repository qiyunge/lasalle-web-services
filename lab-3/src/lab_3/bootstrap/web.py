from flask import Flask

from lab_3.adapters.inbound.flask.inscription.controller import InscriptionController
from lab_3.adapters.inbound.flask.inscription.routes import inscription_blueprint
from lab_3.adapters.inbound.flask.programme.controller import ProgrammeController
from lab_3.adapters.inbound.flask.programme.routes import programme_blueprint
from lab_3.core.application.bus import CommandBus
from lab_3.adapters.inbound.flask.students.controller import StudentController
from lab_3.adapters.inbound.flask.students.routes import student_blueprint


def bootstrap_web(app: Flask, command_bus: CommandBus) -> None:
    inscription_controller = InscriptionController(command_bus=command_bus)
    blueprint_inscription = inscription_blueprint(
        controller=inscription_controller
    )
    app.register_blueprint(blueprint_inscription)

    ##programme blueprint
    programme_controller = ProgrammeController(command_bus=command_bus)
    blueprint_programme = programme_blueprint(
        controller=programme_controller
    )
    app.register_blueprint(blueprint_programme)
    ##student blueprint
    
    student_controller = StudentController(command_bus=command_bus)
    blueprint_student = student_blueprint(
        controller=student_controller
    )
    app.register_blueprint(blueprint_student)
  