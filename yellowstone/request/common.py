"""
Common types and utilities used by multiple requests.
"""

import re
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from bs4 import Tag

from ..scraper import (
    find_element,
    get_entity_date,
    get_entity_user,
    regex_extract,
)

LAST_THREAD_AND_POST_ID = re.compile(r"/forum/t-(\d+)#post-(\d+)")
USER_ID_REGEX = re.compile(r"WIKIDOT\.page\.listeners\.userInfo\((\d+)\).*")
USER_SLUG_REGEX = re.compile(r"https?://www\.wikidot\.com/user:info/([^/]+)")


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


def get_user_slug(source: str, element: Tag) -> str:
    href = element["href"]
    assert isinstance(href, str), "multiple href attributes found"
    match = regex_extract(source, href, USER_SLUG_REGEX)
    assert isinstance(match[1], str), "match group is not a string"
    return match[1]


def extract_last_post(source: str, element: Tag) -> Optional[ForumLastPostData]:
    source = f"{source} last-info"

    children = tuple(element.children)
    if all(isinstance(c, str) for c in children):
        # If there are no HTML element childrens,
        # there are no posts in this category,
        # which means there is no "last post" data.
        return None

    posted_user = get_entity_user(source, find_element(source, element, "a"))
    posted_time = get_entity_date(source, find_element(source, element, "span.odate"))

    element_link = children[-1]
    assert isinstance(element_link, Tag), "Last child in last_info is not an element"
    assert element_link.name == "a", "Last child in last_info is not an anchor"
    match = regex_extract(source, element_link.attrs["href"], LAST_THREAD_AND_POST_ID)
    thread_id = int(match[1])
    post_id = int(match[2])

    return ForumLastPostData(
        posted_time=posted_time,
        posted_user=posted_user,
        thread_id=thread_id,
        post_id=post_id,
    )
