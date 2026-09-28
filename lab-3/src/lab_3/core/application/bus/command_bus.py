from typing import Protocol,Any

class CommandBus(Protocol):
    def dispatch(self, command: Any) -> Any:
        ...