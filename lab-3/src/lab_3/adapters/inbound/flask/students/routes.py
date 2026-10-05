from flask import Blueprint
from lab_3.adapters.inbound.flask.students.controller import StudentController
    
def student_blueprint(controller: StudentController) -> Blueprint:
    router = Blueprint("students", __name__, url_prefix="/students")

    @router.post("")
    def create_student():
        return controller.create_student()

    @router.get("/<int:student_id>")
    def get_student(student_id: int):
        return controller.get_student(student_id)

    @router.delete("/<int:student_id>")
    def delete_student(student_id: int):
        return controller.delete_student(student_id)

    return router