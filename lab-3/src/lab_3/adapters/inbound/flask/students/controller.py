from flask import Response, jsonify, request
from lab_3.core.application.bus import CommandBus
from lab_3.core.domain.common import Failure
from lab_3.adapters.inbound.flask.students.request import parse_create_student_request
from lab_3.adapters.inbound.flask.students.mapper import to_create_student_command, map_create_student_error
from lab_3.adapters.inbound.flask.common.error_mapper import map_request_errors, map_validation_errors
from lab_3.core.domain.common import Success
from lab_3.adapters.inbound.flask.students.mapper import to_create_student_response

class StudentController:
    def __init__(self, command_bus: CommandBus) -> None:
        self._command_bus = command_bus

    def create_student(self) -> tuple[Response, int]:
        parse_result = parse_create_student_request(request.json)
        if isinstance(parse_result, Failure):
            response = map_request_errors(parse_result.error)
            return jsonify(response.body), response.status_code

        request_dto = parse_result.outcome
        command_result = to_create_student_command(request_dto)
        if isinstance(command_result, Failure):
            response = map_validation_errors(command_result.error)
            return jsonify(response.body), response.status_code

        result = self._command_bus.dispatch(command_result.outcome)
        if isinstance(result, Failure):
            response = map_create_student_error(result.error)
            return jsonify(response.body), response.status_code

        if isinstance(result, Success):
            response = to_create_student_response(result.outcome)
            return jsonify(response.to_dict()), 201

        raise RuntimeError("Unhandled create student result")