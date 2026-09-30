from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RequestValidationError:
    field: str
    message: str


@dataclass(frozen=True)
class RequestValidationErrors:
    errors: tuple[RequestValidationError, ...]
