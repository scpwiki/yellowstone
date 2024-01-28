"""
Retrieve forum category data for a site.
"""

import logging
import re
from dataclasses import dataclass
from datetime import datetime

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
class ForumCategoryData:
    id: int
    name: str
    description: str
    thread_count: int
    post_count: int
    last_posted_time: datetime
    last_posted_user: ForumUserData
    last_thread_id: int
    last_post_id: int


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
    source = f"{wikidot.site_url(site_slug)}/forum"
    return list(map(lambda group: convert_group(source, group), soup.select(".forum-group")))


def convert_group(source: str, group: Tag) -> ForumGroupData:
    name = find_element(source, group, ".head .title").text
    description = find_element(source, group, ".head .description").text
    categories = list(map(lambda category: convert_category(source, category), group.select("table tr:not(.head)")))

    return ForumGroupData(
        name=name,
        description=description,
        categories=categories,
    )


def convert_category(source: str, category: Tag) -> ForumCategoryData:
    element = find_element(source, category, ".title a")
    id = int(regex_extract(source, element.attrs["href"], CATEGORY_ID_REGEX)[1])
    name = element.text

    description = find_element(source, category, ".description").text
    thread_count = int(find_element(source, category, ".threads").text)
    post_count = int(find_element(source, category, ".posts").text)

    element_last = find_element(source, category, ".last")

    element_user = find_element(source, element_last, "a")
    user_id = int(regex_extract(source, element_user.attrs["onclick"], USER_ID_REGEX)[1])
    user_slug = regex_extract(source, element_user.attrs["href"], USER_SLUG_REGEX)[1]
    user_name = find_element(source, element_user, "img.small").attrs["alt"]

    element_time = find_element(source, element_last, "span.odate")
    last_posted_time = get_entity_date(source, element_time)

    element_link = find_element(source, element_last, "a[href=\"/forum/*\"]")
    match = regex_extract(source, element_link.attrs["href"], LAST_THREAD_AND_POST_ID)
    last_thread_id = int(match[1])
    last_post_id = int(match[2])

    return ForumCategoryData(
        id=id,
        name=name,
        description=description,
        thread_count=thread_count,
        post_count=post_count,
        last_posted_time=last_posted_time,
        last_posted_user=ForumUserData(
            id=user_id,
            slug=user_slug,
            name=user_name,
        ),
        last_thread_id=last_thread_id,
        last_post_id=last_post_id,
    )
