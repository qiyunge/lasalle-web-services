"""Outcomes of domain construction. Standard library only."""

from dataclasses import dataclass


class ConstructionError(Exception):
    """A direct constructor call breached an invariant and returned no object."""


@dataclass(frozen=True)
class Success[T]:
    value: T


@dataclass(frozen=True)
class Failure[E]:
    error: E
