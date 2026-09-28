from __future__ import annotations

from dataclasses import dataclass

from lab_3.core.domain.common import Result, Success, Failure

@dataclass(frozen=True)
class RequestValidationError:
    field: str
    message: str


@dataclass(frozen=True)
class RequestValidationErrors:
    errors: tuple[RequestValidationError, ...]

