"""
Contains common classes and type definitions.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Union

Json = Union[None, int, float, str, list["Json"], dict[str, "Json"]]


@dataclass
class UserModuleData:
    id: int
    slug: str
    name: str


@dataclass
class ForumLastPostData:
    posted_time: datetime
    posted_user: UserModuleData
    thread_id: int
    post_id: int
