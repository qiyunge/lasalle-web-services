from flask import Blueprint
from lab_3.adapters.inbound.flask.students.controller import StudentController
    
def student_blueprint(controller: StudentController) -> Blueprint:
    router = Blueprint("students", __name__, url_prefix="/students")

    @router.post("")
    def create_student():
        return controller.create_student()

    return router