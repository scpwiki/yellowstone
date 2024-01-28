"""
Retrieve forum category data for a site.
"""

import logging
import re
from dataclasses import dataclass
from datetime import datetime

from ..scraper import find_element, regex_extract
from ..wikidot import Wikidot

CATEGORY_ID_REGEX = re.compile(r'(?:<a href="\/forum\/c-)(\d*)')
CATEGORY_NAME_REGEX = re.compile(r'(?:<div class="title"><[^>]*>)([^<]*)')
CATEGORY_DESCRIPTION_REGEX = re.compile(
    r'(?:<\/a><\/div><div class="description">)([^<]*)'
)
CATEGORY_THREAD_COUNT_REGEX = re.compile(r'(?:td class="threads">)(\d*)')
CATEGORY_POST_COUNT_REGEX = re.compile(r'(?:td class="posts">)(\d*)')
LAST_POSTED_TIME_REGEX = re.compile(r"(?:time_)(\d*)")
LAST_POST_ID_REGEX = re.compile(r'(?:#post-)(\d*)(?:">Jump!)')
LAST_POSTER_ID_REGEX = re.compile(r'(?:userInfo\()(\d*)(?:\); return false;"  )')
LAST_POST_USERNAME_REGEX = re.compile(r'(?:alt=")([^"]*)')
LAST_THREAD_ID = re.compile(r"(?:\/forum\/t-)(\d*)(?:#)")

logger = logging.getLogger(__name__)


@dataclass
class ForumCategoryData:
    id: int
    name: str
    description: str
    thread_count: int
    post_count: int
    last_posted_time: datetime
    last_post_id: int
    last_poster_id: int
    last_poster_username: str
    last_thread_id: int


def get(
    site_slug: str,
    *,
    wikidot: Wikidot,
) -> list[ForumCategoryData]:
    logger.info("Retrieving forum category data for %s", site_slug)

    html = wikidot.ajax_module_connector(
        site_slug,
        "forum/ForumStartModule",
        {"hidden": True},
    )

    category_ids = CATEGORY_ID_REGEX.findall(html)
    category_names = CATEGORY_NAME_REGEX.findall(html)
    category_descriptions = CATEGORY_DESCRIPTION_REGEX.findall(html)
    category_threads = CATEGORY_THREAD_COUNT_REGEX.findall(html)
    category_posts = CATEGORY_POST_COUNT_REGEX.findall(html)
    category_last_posted = LAST_POSTED_TIME_REGEX.findall(html)
    category_last_post_ids = LAST_POST_ID_REGEX.findall(html)
    category_last_poster_ids = LAST_POSTER_ID_REGEX.findall(html)
    category_last_poster_usernames = LAST_POST_USERNAME_REGEX.findall(html)
    category_last_thread_ids = LAST_THREAD_ID.findall(html)
    items = len(category_ids)

    # If we remove these assertions, then you *must* replace zip() with itertools.zip_longest().
    assert items == len(
        category_names
    ), f"Category names length mismatch {items} != {len(category_names)}"

    assert items == len(
        category_descriptions
    ), f"Category descriptions length mismatch {items} != {len(category_descriptions)}"

    assert items == len(
        category_threads
    ), f"Category threads length mismatch {items} != {len(category_threads)}"

    assert items == len(
        category_posts
    ), f"Category posts length mismatch {items} != {len(category_posts)}"

    assert items == len(
        category_last_posted
    ), f"Category last posted length mismatch {items} != {len(category_last_posted)}"

    assert (
        items == len(category_last_post_ids)
    ), f"Category last post IDs length mismatch {items} != {len(category_last_post_ids)}"

    assert (
        items == len(category_last_poster_usernames)
    ), f"Category last poster usernames length mismatch {items} != {len(category_last_poster_usernames)}"

    assert (
        items == len(category_last_thread_ids)
    ), f"Category last thread IDs length mismatch {items} != {len(category_last_thread_ids)}"

    categories = []
    for (
        id,
        name,
        description,
        thread_count,
        post_count,
        last_posted_time,
        last_post_id,
        last_poster_id,
        last_poster_username,
        last_thread_id,
    ) in zip(
        category_ids,
        category_names,
        category_descriptions,
        category_threads,
        category_posts,
        category_last_posted,
        category_last_post_ids,
        category_last_poster_ids,
        category_last_poster_usernames,
        category_last_thread_ids,
    ):
        categories.append(
            ForumCategoryData(
                id=int(id),
                name=name,
                description=description,
                thread_count=int(thread_count),
                post_count=int(post_count),
                last_posted_time=datetime.fromtimestamp(int(last_posted_time)),
                last_post_id=int(last_post_id),
                last_poster_id=int(last_poster_id),
                last_poster_username=last_poster_username,
                last_thread_id=int(last_thread_id),
            )
        )

    return categories
