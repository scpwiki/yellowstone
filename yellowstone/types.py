"""
Contains class and type definitions for use in annotations.
"""

from dataclasses import dataclass
from typing import Union

Json = Union[None, int, float, str, list["Json"], dict[str, "Json"]]


@dataclass
class ForumUserData:
    id: int
    slug: str
    name: str
