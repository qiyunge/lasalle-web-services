from flask import Flask

from lab_3.adapters.inbound.flask.inscription.controller import InscriptionController
from lab_3.adapters.inbound.flask.inscription.routes import inscription_blueprint
from lab_3.adapters.inbound.flask.programme.controller import ProgrammeController
from lab_3.adapters.inbound.flask.programme.routes import programme_blueprint
from lab_3.core.application.bus import CommandBus


def bootstrap_web(app: Flask, command_bus: CommandBus) -> None:
    inscription_controller = InscriptionController(command_bus=command_bus)
    blueprint_inscription = inscription_blueprint(
        controller=inscription_controller
    )
    
    programme_controller = ProgrammeController(command_bus=command_bus)
    blueprint_programme = programme_blueprint(
        controller=programme_controller
    )
    app.register_blueprint(blueprint_inscription)
    app.register_blueprint(blueprint_programme)
