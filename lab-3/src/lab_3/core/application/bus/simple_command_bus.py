from __future__ import annotations

from typing import Callable, Any
from .command_bus import CommandBus


class SimpleCommandBus:
    def __init__(self) -> None:
        self._handlers = {}

    def register(self, command_type: type, handler: any) -> None:
        if command_type in self._handlers:
            raise ValueError(f"Handler already registered for command type: {command_type.__name__}")
        self._handlers[command_type] = handler

    def dispatch(self, command: Any) -> Any:
        command_type = type(command)
        handler = self._handlers.get(command_type)
        if handler is None:
            raise LookupError(f"No handler registered for command type: {command_type.__name__}")
        return handler.handle(command)