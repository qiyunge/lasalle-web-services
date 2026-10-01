from flask import Blueprint

from .controller import ProgrammeController


def programme_blueprint(controller: ProgrammeController) -> Blueprint:
    router = Blueprint("programme", __name__, url_prefix="/programmes")

    @router.get("")
    def list_programmes():
        return controller.list_programmes()

    return router
