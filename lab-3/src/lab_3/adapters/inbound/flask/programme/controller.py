from flask import Response,jsonify, request

from .mapper import to_programme_list_response

from lab_3.core.application.ports.inbound.programmes.list import ProgrammeListQuery
from lab_3.core.application.bus.command_bus import CommandBus
from lab_3.core.domain.common.validation import ValidationErrors
from lab_3.adapters.inbound.flask.common.error_mapper import map_request_errors, map_validation_errors

from lab_3.adapters.inbound.flask.programme.request import parse_create_programme_request
from lab_3.adapters.inbound.flask.programme.mapper import to_create_programme_command, to_create_programme_response, map_create_programme_error
from lab_3.core.domain.common import Failure, Success
from lab_3.core.application.ports.inbound.programmes.create import CreateProgrammeResult

class ProgrammeController:
    def __init__(self, command_bus: CommandBus, ) -> None:
        self._command_bus = command_bus

    def list_programmes(self) -> tuple[Response,int]:
        result = self._command_bus.dispatch(ProgrammeListQuery())
        return jsonify(to_programme_list_response(result)), 200

    def create_programme(self) -> tuple[Response,int]:
        parse_result = parse_create_programme_request(request.json)
        if isinstance(parse_result, Failure):
            response = map_request_errors(parse_result.error)
            return jsonify(response.body), response.status_code

        request_dto = parse_result.value

        command_result = to_create_programme_command(request_dto)
        if isinstance(command_result, Failure):
            response = map_validation_errors(command_result.error)
            return jsonify(response.body), response.status_code

        result = self._command_bus.dispatch(command_result.value)
        if isinstance(result, Failure):
            response = map_create_programme_error(result.error)
            return jsonify(response.body), response.status_code

        if isinstance(result, Success):
            response = to_create_programme_response(result.value)
            return jsonify(response.to_dict()), 201

        raise RuntimeError("Unhandled create programme result")