"""The presence rule shared by required text fields."""

from typing import TypeGuard


def is_present(value: object) -> TypeGuard[str]:
    """A required text value is present when it is a non-empty string. No trimming."""
    return isinstance(value, str) and value != ""
