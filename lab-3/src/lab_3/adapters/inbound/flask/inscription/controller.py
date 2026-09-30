from flask import Response, jsonify, request

from lab_3.adapters.inbound.flask.common.error_mapper import (
    map_request_errors,
    map_validation_errors,
)
from lab_3.adapters.inbound.flask.inscription.mapper import (
    map_create_inscription_error,
    to_create_inscription_command,
    to_create_inscription_response,
    map_update_inscription_note_error,
    to_update_inscription_note_command,
    to_update_inscription_note_response,
)
from lab_3.adapters.inbound.flask.inscription.request import (
    parse_create_inscription_request,
    parse_update_inscription_note_request,
)
from lab_3.core.application.bus import CommandBus
from lab_3.core.domain.common import Failure, Success


class InscriptionController:
    def __init__(self, command_bus: CommandBus) -> None:
        self._command_bus = command_bus

    def create_inscription(self) -> tuple[Response, int]:
        parse_result = parse_create_inscription_request(request.json)
        if isinstance(parse_result, Failure):
            response = map_request_errors(parse_result.error)
            return jsonify(response.body), response.status_code

        request_dto = parse_result.value

        command_result = to_create_inscription_command(request_dto)
        if isinstance(command_result, Failure):
            response = map_validation_errors(command_result.error)
            return jsonify(response.body), response.status_code

        result = self._command_bus.dispatch(command_result.value)

        if isinstance(result, Failure):
            response = map_create_inscription_error(result.error)
            return jsonify(response.body), response.status_code

        if isinstance(result, Success):
            response = to_create_inscription_response(result.value)
            return jsonify(response.to_dict()), 201

        raise RuntimeError("Unhandled create inscription result")

    def update_inscription_note(self, id: int) -> tuple[Response, int]:
        parse_result = parse_update_inscription_note_request(id, request.json)
        if isinstance(parse_result, Failure):
            response = map_request_errors(parse_result.error)
            return jsonify(response.body), response.status_code

        request_dto = parse_result.value

        command_result = to_update_inscription_note_command(request_dto)
        if isinstance(command_result, Failure):
            response = map_validation_errors(command_result.error)
            return jsonify(response.body), response.status_code

        result = self._command_bus.dispatch(command_result.value)

        if isinstance(result, Failure):
            respose =  map_update_inscription_note_error(result.error)
            return jsonify(response.body), response.status_code

        if isinstance(result, Success):
            response = to_update_inscription_note_response(result.value)
            return jsonify(response.to_dict()), 200

        raise RuntimeError("Unhandled update inscription note result")
