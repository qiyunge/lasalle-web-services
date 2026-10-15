"""Programme capability. Imports no other capability."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Programme:
    """id is required. Identifier."""

    id: int
