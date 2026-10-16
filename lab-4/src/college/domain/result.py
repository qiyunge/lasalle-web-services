"""Success and failure values for domain construction. Standard library only."""

from dataclasses import dataclass


class ConstructionError(Exception):
    """A direct constructor call breached an invariant and returned no entity."""


@dataclass(frozen=True)
class Success:
    value: object


@dataclass(frozen=True)
class Failure:
    error: object


def is_integer(value) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def is_text(value) -> bool:
    return isinstance(value, str) and value != ""
