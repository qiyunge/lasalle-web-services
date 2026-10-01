from flask import Response,jsonify

from .mapper import to_programme_list_response

from lab_3.core.application.ports.inbound.programmes.list import ProgrammeListQuery
from lab_3.core.application.bus.command_bus import CommandBus

class ProgrammeController:
    def __init__(self, command_bus: CommandBus, ) -> None:
        self._command_bus = command_bus

    def list_programmes(self) -> tuple[Response,int]:
        result = self._command_bus.dispatch(ProgrammeListQuery())
        return jsonify(to_programme_list_response(result)), 200