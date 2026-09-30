from __future__ import annotations

from typing import Any

from lab_3.core.application.command import Command 
from lab_3.core.application.bus.command_bus import CommandHandler
class SimpleCommandBus:
    def __init__(self) -> None:
        self._handlers: dict[type, Any] = {}

    def register(self, command_type: type, handler: Any) -> None:
        if command_type in self._handlers:
            raise ValueError(
                f"Handler already registered for command type: {command_type.__name__}"
            )
        self._handlers[command_type] = handler

    def dispatch[T](self, command: Command[T]) -> T:
        handler = self._handlers.get(type(command))
        if handler is None:
            raise LookupError(
                f"No handler registered for command type: {type(command).__name__}"
            )
        return handler.handle(command)
