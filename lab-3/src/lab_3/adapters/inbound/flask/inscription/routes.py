from flask import Blueprint

from .controller import InscriptionController


def inscription_blueprint(controller: InscriptionController) -> Blueprint:
    router = Blueprint("inscription", __name__, url_prefix="/inscriptions")

    @router.post("")
    def create_inscription():
        return controller.create_inscription()

    @router.patch("/<int:id>")
    def update_inscription_note(id: int):
        return controller.update_inscription_note(id)
    return router
