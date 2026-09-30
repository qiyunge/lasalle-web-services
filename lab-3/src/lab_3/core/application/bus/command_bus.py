from typing import Protocol

from lab_3.core.application.command import Command


class CommandBus(Protocol):
    def dispatch[T](self, command: Command[T]) -> T: ...
