"""Programme capability. Imports no other capability."""

from dataclasses import dataclass

from college.domain.result import ConstructionError, is_integer


@dataclass(frozen=True)
class Programme:
    """id is required. Identifier."""

    id: int

    def __post_init__(self) -> None:
        if not is_integer(self.id):
            raise ConstructionError
