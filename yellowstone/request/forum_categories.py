"""
Retrieve forum category data for a site.
"""

import logging
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from bs4 import Tag

from ..request.site_members import USER_ID_REGEX
from ..request.user import USER_SLUG_REGEX
from ..scraper import find_element, make_soup, regex_extract, get_entity_date
from ..wikidot import Wikidot

CATEGORY_ID_REGEX = re.compile(r"\/forum\/c-(\d+)(?:\/.+)?")
LAST_THREAD_AND_POST_ID = re.compile(r"/forum/t-(\d+)#post-(\d+)")

logger = logging.getLogger(__name__)


@dataclass
class ForumUserData:
    id: int
    slug: str
    name: str


@dataclass
class ForumCategoryLastPostData:
    posted_time: datetime
    posted_user: ForumUserData
    thread_id: int
    post_id: int


@dataclass
class ForumCategoryData:
    id: int
    name: str
    description: str
    thread_count: int
    post_count: int
    last_post: Optional[ForumCategoryLastPostData]


@dataclass
class ForumGroupData:
    name: str
    description: str
    categories: list[ForumCategoryData]


def get(
    site_slug: str,
    *,
    wikidot: Wikidot,
) -> list[ForumGroupData]:
    logger.info("Retrieving forum category data for %s", site_slug)

    html = wikidot.ajax_module_connector(
        site_slug,
        "forum/ForumStartModule",
        {"hidden": True},
    )
    soup = make_soup(html)
    source = f"{site_slug} forum"
    return list(map(lambda group: extract_group(source, group), soup.select(".forum-group")))


def extract_group(source: str, group: Tag) -> ForumGroupData:
    name = find_element(source, group, ".head .title").text
    source = f"{source} group '{name}'"
    description = find_element(source, group, ".head .description").text
    categories = list(map(lambda category: extract_category(source, category), group.select("table tr:not(.head)")))

    return ForumGroupData(
        name=name,
        description=description,
        categories=categories,
    )


def extract_category(source: str, category: Tag) -> ForumCategoryData:
    element = find_element(source, category, ".title a")
    id = int(regex_extract(source, element.attrs["href"], CATEGORY_ID_REGEX)[1])
    name = element.text
    source = f"{source} category '{name}'"

    description = find_element(source, category, ".description").text
    thread_count = int(find_element(source, category, ".threads").text)
    post_count = int(find_element(source, category, ".posts").text)
    last_post = extract_last_post(source, find_element(source, category, ".last"))

    return ForumCategoryData(
        id=id,
        name=name,
        description=description,
        thread_count=thread_count,
        post_count=post_count,
        last_post=last_post,
    )


def extract_last_post(source: str, element: Tag) -> Optional[ForumCategoryLastPostData]:
    source = f"{source} last-info"

    children = tuple(element.children)
    if not children:
        # No posts in this category, thus no "last" post data
        return None

    element_user = find_element(source, element, "a")
    user_id = int(regex_extract(source, element_user.attrs["onclick"], USER_ID_REGEX)[1])
    user_slug = regex_extract(source, element_user.attrs["href"], USER_SLUG_REGEX)[1]
    user_name = find_element(source, element_user, "img.small").attrs["alt"]

    element_time = find_element(source, element, "span.odate")
    posted_time = get_entity_date(source, element_time)

    element_link = children[-1]
    assert element_link.name == "a", "Last element in element_last is not an anchor"
    match = regex_extract(source, element_link.attrs["href"], LAST_THREAD_AND_POST_ID)
    thread_id = int(match[1])
    post_id = int(match[2])

    return ForumCategoryLastPostData(
        posted_time=posted_time,
        posted_user=ForumUserData(
            id=user_id,
            slug=user_slug,
            name=user_name,
        ),
        thread_id=thread_id,
        post_id=post_id,
    )
