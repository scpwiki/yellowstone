"""
Miscellaneous utility functions.
"""

from itertools import islice
from typing import Iterable, TypeVar

T = TypeVar("T")


def chunks(it: Iterable[T], size: int) -> Iterable[tuple[T, ...]]:
    iterator = iter(it)
    while chunk := tuple(islice(iterator, size)):
        yield chunk
