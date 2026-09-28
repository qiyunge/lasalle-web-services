from dataclasses import dataclass
from typing import Generic, TypeVar, TypeAlias

T = TypeVar('T')
E = TypeVar('E')

@dataclass(frozen=True)
class Success(Generic[T]):
    value: T

@dataclass(frozen=True)
class Failure(Generic[E]):
    error: E

Result: TypeAlias = Success[T] | Failure[E]



def collect_errors(*results: list[Result[T, E]]) -> list[E]|None:
    errors =  [ result.error for result in results if isinstance(result, Failure) ]
    return errors if errors else None   

