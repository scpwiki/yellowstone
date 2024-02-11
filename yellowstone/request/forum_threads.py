"""
Retrieve forum threads in a forum category by page.
"""

import logging
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from bs4 import Tag

from ..scraper import (
    ScrapingError,
    extract_last_forum_post,
    find_element,
    get_entity_date,
    get_entity_user,
    make_soup,
    regex_extract,
)
from ..types import ForumLastPostData, UserModuleData
from ..wikidot import Wikidot

LAST_THREAD_ID = re.compile(r"/forum/t-(\d+)(?:\/.*)?")

logger = logging.getLogger(__name__)


@dataclass
class ForumThreadData:
    id: int
    title: str
    description: str
    sticky: bool
    created_by: UserModuleData
    created_at: datetime
    post_count: int
    last_post: Optional[ForumLastPostData]


def get(
    site_slug: str,
    forum_category_id: int,
    offset: int,
    *,
    wikidot: Wikidot,
) -> list[ForumThreadData]:
    logger.info(
        "Retrieving forum thread data for site %s category %d (offset %d)",
        site_slug,
        forum_category_id,
        offset,
    )

    html = wikidot.ajax_module_connector(
        site_slug,
        "forum/ForumViewCategoryModule",
        {
            "c": forum_category_id,
            "p": offset,
        },
    )
    soup = make_soup(html)
    source = f"forum category {forum_category_id}"
    return list(
        map(
            lambda category: process_row(source, category),
            soup.select("table tr:not(.head)"),
        )
    )


def process_row(source: str, row: Tag) -> ForumThreadData:
    description = find_element(source, row, ".description").text.strip()

    header = find_element(source, row, ".name")
    post_count = int(find_element(source, row, ".posts").text.strip())

    # Thread title
    sticky = False
    title = None
    for child in find_element(source, header, ".title").children:
        if isinstance(child, str) and child.strip():
            # Copy text for "sticky"
            sticky = True
        elif isinstance(child, Tag) and child.name == "a":
            # Anchor, with thread data
            thread_id = int(
                regex_extract(source, child.attrs["href"], LAST_THREAD_ID)[1],
            )
            title = child.text
            source = f"{source} thread '{title}'"

    if title is None:
        raise ScrapingError(f"Could not find anchor in {source}")

    # Thread origin
    started = find_element(source, row, ".started")
    started_at = get_entity_date(source, find_element(source, started, "span.odate"))
    started_by = get_entity_user(source, find_element(source, started, ".printuser a"))

    # Thread's last post
    last_post = extract_last_forum_post(source, row)

    return ForumThreadData(
        id=thread_id,
        title=title,
        description=description,
        sticky=sticky,
        created_by=started_by,
        created_at=started_at,
        post_count=post_count,
        last_post=last_post,
    )
