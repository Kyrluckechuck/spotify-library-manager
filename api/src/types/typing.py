from __future__ import annotations

from typing import Any, Protocol, Type, TypeVar, Union, cast, runtime_checkable

T = TypeVar("T")


@runtime_checkable
class SupportsIdInt(Protocol):
    id: int


@runtime_checkable
class SupportsIdStr(Protocol):
    id: str


SupportsId = Union[SupportsIdInt, SupportsIdStr]


def build_gql(cls: Type[T], **kwargs: Any) -> T:
    """
    Construct a Strawberry GraphQL type in a mypy-friendly way.

    Many frameworks decorate classes and mypy struggles to infer their
    constructor signatures. This helper wraps the call and casts the
    result to the intended type, centralizing the workaround in one
    place rather than sprinkling per-call ignores.
    """
    return cast(T, cls(**kwargs))  # type: ignore[redundant-cast]
