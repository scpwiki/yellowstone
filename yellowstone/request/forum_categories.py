"""
Retrieve forum category data for a site.
"""

import logging
import re
from dataclasses import dataclass
from typing import Optional

from bs4 import Tag

from ..scraper import (
    extract_last_forum_post,
    find_element,
    make_soup,
    regex_extract_int,
)
from ..types import ForumLastPostData
from ..wikidot import Wikidot

CATEGORY_ID_REGEX = re.compile(r"\/forum\/c-(\d+)(?:\/.+)?")

logger = logging.getLogger(__name__)


@dataclass
class ForumCategoryData:
    id: int
    name: str
    description: str
    thread_count: int
    post_count: int
    last_post: Optional[ForumLastPostData]


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
    return list(
        map(lambda group: extract_group(source, group), soup.select(".forum-group")),
    )


def extract_group(source: str, group: Tag) -> ForumGroupData:
    name = find_element(source, group, ".head .title").text
    source = f"{source} group '{name}'"
    description = find_element(source, group, ".head .description").text
    categories = list(
        map(
            lambda category: extract_category(source, category),
            group.select("table tr:not(.head)"),
        )
    )

    return ForumGroupData(
        name=name,
        description=description,
        categories=categories,
    )


def extract_category(source: str, category: Tag) -> ForumCategoryData:
    element = find_element(source, category, ".title a")
    id = regex_extract_int(source, element.attrs["href"], CATEGORY_ID_REGEX)
    name = element.text
    source = f"{source} category '{name}'"

    description = find_element(source, category, ".description").text
    thread_count = int(find_element(source, category, ".threads").text)
    post_count = int(find_element(source, category, ".posts").text)
    last_post = extract_last_forum_post(source, category)

    return ForumCategoryData(
        id=id,
        name=name,
        description=description,
        thread_count=thread_count,
        post_count=post_count,
        last_post=last_post,
    )
