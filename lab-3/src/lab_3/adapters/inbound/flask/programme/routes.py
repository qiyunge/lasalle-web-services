from flask import Blueprint
from flask import request
from .controller import ProgrammeController

def programme_blueprint(controller: ProgrammeController) -> Blueprint:
    router = Blueprint("programme", __name__, url_prefix="/programmes")

    @router.get("")
    def list_programmes():
        return controller.list_programmes()


    @router.post("")
    def create_programme():
        return controller.create_programme()
        
    return router
