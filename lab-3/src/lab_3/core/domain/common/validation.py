from dataclasses import dataclass


@dataclass(frozen=True)
class ValidationError:
    field: str
    message: str


@dataclass(frozen=True)
class ValidationErrors:
    errors: tuple[ValidationError, ...]

    def __bool__(self) -> bool:
        return bool(self.errors)
