from typing import Protocol

from lab_3.core.application.command import Command


class CommandHandler[C, R](Protocol):
    def handle(self, command: C) -> R:
        ...

class CommandBus(Protocol):
    def dispatch[T](self, command: Command[T]) -> T: ...
