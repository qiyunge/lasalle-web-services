"""Inbound HTTP adapter. Parses requests and maps use-case outcomes to responses."""

from flask import Blueprint, jsonify, request

from college.application.browse_courses import browse
from college.application.enroll_student import ABSENT, enroll

STATUS_BY_OUTCOME = {
    "enrolled": 201,
    "invalid": 400,
    "forbidden": 400,
    "not_registered": 400,
    "not_found": 404,
    "conflict": 409,
}


def create_blueprint(enrollment_ports, course_port) -> Blueprint:
    """Each factory returns fresh adapters for one request."""
    blueprint = Blueprint("college", __name__)

    @blueprint.post("/inscriptions")
    def post_inscription():
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            payload = {}
        with enrollment_ports() as ports:
            result = enroll(
                payload.get("acting_student_id"),
                payload.get("course_id"),
                student_id=payload.get("student_id", ABSENT),
                note=payload.get("note", ABSENT),
                **ports,
            )
        body = {"message": result.message}
        if result.inscription is not None:
            body["inscription"] = {
                "id": result.inscription.id,
                "student_id": result.inscription.student_id,
                "course_id": result.inscription.course_id,
                "note": result.inscription.note,
            }
        return jsonify(body), STATUS_BY_OUTCOME[result.outcome]

    @blueprint.get("/courses")
    def get_courses():
        with course_port() as courses:
            shown = browse(courses)
        return jsonify(
            {
                "courses": [
                    {
                        "id": course.id,
                        "course_code": course.course_code,
                        "name": course.name,
                    }
                    for course in shown
                ]
            }
        )

    return blueprint
