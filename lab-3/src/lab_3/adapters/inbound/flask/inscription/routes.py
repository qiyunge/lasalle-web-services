from flask import Blueprint

from .controller import InscriptionController

def create_inscription_blueprint(controller: InscriptionController) -> Blueprint:
    router = Blueprint('inscription', __name__, url_prefix='/inscriptions')

    @router.post('')
    def create_inscription():
        return controller.create_inscription()

    return router
  