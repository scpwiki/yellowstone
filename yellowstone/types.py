"""
Contains common classes and type definitions.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, TypeVar, Union

from bs4 import Tag


@dataclass
class UserModuleData:
    id: int
    slug: str
    name: str


@dataclass
class DeletedUserData:
    id: int


@dataclass
class AnonymousUserData:
    ip: str


@dataclass
class CustomUserData:
    name: str

    @property
    def is_system(self) -> bool:
        """
        The 'Wikidot' user is special, and not a regular user.
        It designates the system user taking an action.
        """

        return self.name.casefold() == "wikidot"


@dataclass
class ForumLastPostData:
    posted_time: datetime
    posted_user: ForumPostUser
    thread_id: int
    post_id: int


Json = Union[None, int, float, str, list["Json"], dict[str, "Json"]]
ForumPostUser = Union[
    UserModuleData,
    DeletedUserData,
    AnonymousUserData,
    CustomUserData,
]


def assert_is_tag(object: Any, name: str = "Object") -> Tag:
    assert isinstance(object, Tag), f"{name} is not an HTML entity"
    return object
