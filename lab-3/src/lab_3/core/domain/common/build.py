from __future__ import annotations


def build[T](cls: type[T], **fields: object) -> T:
    obj = object.__new__(cls)
    for name, value in fields.items():
        object.__setattr__(obj, name, value)
    return obj


def set_attributes[T](obj: T, **fields: object) -> T:
    for name, value in fields.items():
        object.__setattr__(obj, name, value)
    return obj
