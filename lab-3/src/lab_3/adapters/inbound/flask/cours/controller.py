from flask import Response, jsonify, request

from lab_3.adapters.inbound.flask.common.error_mapper import (
    map_request_errors,
    map_validation_errors,
)
from lab_3.adapters.inbound.flask.cours.mapper import (
    map_create_cours_error,
    map_get_cours_error,
    to_create_cours_command,
    to_create_cours_response,
    to_get_cours_command,
    to_get_cours_response,
    to_list_cours_command,
    to_list_cours_response,
)
from lab_3.adapters.inbound.flask.cours.request import (
    parse_create_cours_request,
    parse_get_cours_request,
    parse_list_cours_request,
)
from lab_3.core.application.bus import CommandBus
from lab_3.core.domain.common import Failure, Success


class CoursController:
    def __init__(self, command_bus: CommandBus) -> None:
        self._command_bus = command_bus

    def create_cours(self) -> tuple[Response, int]:
        parse_result = parse_create_cours_request(request.json)
        if isinstance(parse_result, Failure):
            response = map_request_errors(parse_result.error)
            return jsonify(response.body), response.status_code

        command_result = to_create_cours_command(parse_result.outcome)
        if isinstance(command_result, Failure):
            response = map_validation_errors(command_result.error)
            return jsonify(response.body), response.status_code

        result = self._command_bus.dispatch(command_result.outcome)
        if isinstance(result, Failure):
            response = map_create_cours_error(result.error)
            return jsonify(response.body), response.status_code

        if isinstance(result, Success):
            response = to_create_cours_response(result.outcome)
            return jsonify(response.to_dict()), 201

        raise RuntimeError("Unhandled create cours result")

    def get_cours(self, cours_id: int) -> tuple[Response, int]:
        parse_result = parse_get_cours_request(cours_id)
        if isinstance(parse_result, Failure):
            response = map_request_errors(parse_result.error)
            return jsonify(response.body), response.status_code

        command_result = to_get_cours_command(parse_result.outcome)
        if isinstance(command_result, Failure):
            response = map_validation_errors(command_result.error)
            return jsonify(response.body), response.status_code

        result = self._command_bus.dispatch(command_result.outcome)
        if isinstance(result, Failure):
            response = map_get_cours_error(result.error)
            return jsonify(response.body), response.status_code

        if isinstance(result, Success):
            response = to_get_cours_response(result.outcome)
            return jsonify(response.to_dict()), 200

        raise RuntimeError("Unhandled get cours result")

    def list_cours(self) -> tuple[Response, int]:
        parse_result = parse_list_cours_request(
            request.args.get("page"),
            request.args.get("page_size"),
        )
        if isinstance(parse_result, Failure):
            response = map_request_errors(parse_result.error)
            return jsonify(response.body), response.status_code

        command_result = to_list_cours_command(parse_result.outcome)
        if isinstance(command_result, Failure):
            response = map_validation_errors(command_result.error)
            return jsonify(response.body), response.status_code

        result = self._command_bus.dispatch(command_result.outcome)
        if isinstance(result, Failure):
            raise RuntimeError(f"Unhandled list cours result: {result.error!r}")

        if isinstance(result, Success):
            response = to_list_cours_response(result.outcome)
            return jsonify(response.to_dict()), 200

        raise RuntimeError("Unhandled list cours result")
