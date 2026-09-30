from __future__ import annotations

from typing import Protocol, Self


class TransactionRestartRequired(Exception):
    """The open transaction could not become a write and must be started again."""


class UnitOfWork(Protocol):
    def __enter__(self) -> Self: ...

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None: ...

    def commit(self) -> None: ...
