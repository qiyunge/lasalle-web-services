"""Inbound HTTP adapter. Translates JSON to the input contract and outcomes to responses."""

from flask import Blueprint, jsonify, request

from college.application.browse_courses import browse
from college.application.enroll_student import (
    ABSENT,
    EnrollmentResult,
    Outcome,
    SelfEnrollmentRequest,
    ValidationError,
    enroll,
)
from college.domain.course import Course
from college.domain.inscription import Inscription
from college.domain.self_enrollment import Refusal

ACTOR_REQUIRED = "acting_student_id is required."
COURSE_REQUIRED = "course_id is required."
IDS_NOT_INTEGERS = "acting_student_id and course_id must be integers."

_SINGLE_IDENTIFIER_MESSAGE = {
    "acting_student_id_missing": ACTOR_REQUIRED,
    "course_id_missing": COURSE_REQUIRED,
    "acting_student_id_not_integer": IDS_NOT_INTEGERS,
    "course_id_not_integer": IDS_NOT_INTEGERS,
}

_STATUS_BY_REFUSAL = {
    Refusal.GRADE_ATTEMPT: 400,
    Refusal.NOT_REGISTERED: 400,
    Refusal.COURSE_MISSING: 404,
    Refusal.ALREADY_ENROLLED: 409,
}


def _request_from(payload: dict) -> SelfEnrollmentRequest:
    return SelfEnrollmentRequest(
        acting_student_id=payload.get("acting_student_id"),
        course_id=payload.get("course_id"),
        student_id=payload.get("student_id", ABSENT),
        note=payload.get("note", ABSENT),
    )


def _validation_body(errors: tuple[ValidationError, ...]) -> dict[str, object]:
    """One required-identifier failure keeps its sentence. Anything else is the errors array."""
    if len(errors) == 1 and errors[0].code in _SINGLE_IDENTIFIER_MESSAGE:
        return {"message": _SINGLE_IDENTIFIER_MESSAGE[errors[0].code]}
    return {"errors": [{"code": error.code, "field": error.field} for error in errors]}


def _inscription_json(inscription: Inscription) -> dict[str, object]:
    return {
        "id": inscription.id.value,
        "student_id": inscription.student_id.value,
        "course_id": inscription.course_id.value,
        "note": inscription.note,
    }


def _course_json(course: Course) -> dict[str, object]:
    return {"id": course.id.value, "course_code": course.course_code, "name": course.name}


def _response(result: EnrollmentResult) -> tuple[dict[str, object], int]:
    if result.outcome is Outcome.INVALID_INPUT:
        return _validation_body(result.errors), 400
    if result.inscription is None:
        status = _STATUS_BY_REFUSAL[result.refusal] if result.refusal else 500
        return {"message": result.message}, status
    return {"message": result.message, "inscription": _inscription_json(result.inscription)}, 201


def create_blueprint(enrollment_ports, course_port) -> Blueprint:
    """Each factory yields fresh adapters for one request."""
    blueprint = Blueprint("college", __name__)

    @blueprint.post("/inscriptions")
    def post_inscription():
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            payload = {}
        with enrollment_ports() as ports:
            result = enroll(_request_from(payload), ports)
        body, status = _response(result)
        return jsonify(body), status

    @blueprint.get("/courses")
    def get_courses():
        with course_port() as courses:
            batch = browse(courses)
        return jsonify({"courses": [_course_json(course) for course in batch.courses]})

    return blueprint
