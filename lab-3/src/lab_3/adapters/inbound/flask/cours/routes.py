from flask import Blueprint

from lab_3.adapters.inbound.flask.cours.controller import CoursController


def cours_blueprint(controller: CoursController) -> Blueprint:
    router = Blueprint("cours", __name__, url_prefix="/cours")

    @router.get("")
    def list_cours():
        return controller.list_cours()

    @router.post("")
    def create_cours():
        return controller.create_cours()

    @router.get("/<int:cours_id>")
    def get_cours(cours_id: int):
        return controller.get_cours(cours_id)

    return router
