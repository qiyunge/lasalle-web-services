from typing import Protocol

from lab_3.core.application.query import Query


class QueryBus(Protocol):
    def dispatch[R](self, query: Query[R]) -> R:
        ...