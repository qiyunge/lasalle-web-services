from lab_3.core.application.query import Query
from typing import Callable, Any, cast

class SimpleQueryBus:
    def __init__(self) -> None:
        self._handlers:dict[type[object], Callable[[object], object]]= {}

    def register[Q,R](self, query_type: type[Q], handler: Callable[[Q], R]) -> None:
        if query_type in self._handlers:
            raise ValueError(f"Handler already registered for query type {query_type}")
        
        def invoke(query:object)->object:
            return handler(cast(Q,query))
        self._handlers[query_type] = invoke

    def dispatch[R](self, query: Query[R]) -> R:
        handler = self._handlers.get(type(query))

        if handler is None:
            raise LookupError(f"No handler registered for query type {type(query)}")

        return cast(R, handler(query))