from flask import jsonify, request
from lab_3.core.application.bus import CommandBus
from lab_3.adapters.inbound.flask.inscription.request import parse_create_inscription_request
from lab_3.adapters.inbound.flask.common.error_mapper import map_request_errors
from lab_3.adapters.inbound.flask.inscription.mapper import (
    to_create_inscription_command, 
    to_create_inscription_response,
    map_create_inscription_error)
from lab_3.core.domain.common import Result, Success, Failure


class InscriptionController:
    def __init__(self, command_bus: CommandBus) -> None:
        self._command_bus = command_bus

    def create_inscription(self):
        data = request.json
        parse_result = parse_create_inscription_request(data)
        if isinstance(parse_result, Failure):
            response = map_request_errors(parse_result.error)
            return jsonify(response.body), response.status_code

        request_dto = parse_result.value

        # adapter dto to command
        command = to_create_inscription_command(request_dto)
        result = self._command_bus.dispatch(command)

        # application result to http response dto
        if isinstance(result, Failure):
            response = map_create_inscription_error(result.error)
            return jsonify(response.body), response.status_code

        if isinstance(result, Success):
            response = to_create_inscription_response(result.value)
            return jsonify(response.to_dict()), 201

        
    
        