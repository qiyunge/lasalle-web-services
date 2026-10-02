from dataclasses import dataclass


@dataclass(frozen=True)
class Success[T]:
    outcome: T


@dataclass(frozen=True)
class Failure[E]:
    error: E


type Result[T, E] = Success[T] | Failure[E]


def collect_errors[T, E](*results: Result[T, E]) -> list[E] | None:
    errors = [result.error for result in results if isinstance(result, Failure)]
    return errors or None
