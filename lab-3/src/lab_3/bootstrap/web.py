from flask import Flask
from lab_3.core.application.bus import CommandBus
from lab_3.core.application.ports.inbound.create_inscription import CreateInscriptionCommand
from lab_3.adapters.inbound.flask.inscription.controller import InscriptionController
from lab_3.adapters.inbound.flask.inscription.routes import create_inscription_blueprint


def bootstrap_web(app: Flask, command_bus: CommandBus) -> None:
    inscription_controller = InscriptionController(command_bus= command_bus)
    inscription_blueprint = create_inscription_blueprint(controller=inscription_controller)
    app.register_blueprint(inscription_blueprint)