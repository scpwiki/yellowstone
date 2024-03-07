"""
Retrieve posts in a forum thread by page.
"""

import logging
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from bs4 import Tag

from ..scraper import (
    find_element,
    get_entity_date,
    get_entity_user,
    make_soup,
    regex_extract_int,
    regex_extract_str,
)
from ..types import ForumPostUser, assert_is_tag
from ..wikidot import Wikidot
from .forum_categories import CATEGORY_ID_REGEX

logger = logging.getLogger(__name__)

THREAD_TITLE = re.compile(r"\s*» (.+?)\s*")
POST_ID = re.compile(r"(?:post|fpc)-(\d+)")


@dataclass
class ForumPostData:
    id: int
    parent: Optional[int]
    title: str
    created_by: ForumPostUser
    created_at: datetime
    html: str


def get(
    site_slug: str,
    *,
    category_id: int,
    thread_id: int,
    offset: int,
    wikidot: Wikidot,
) -> list[ForumPostData]:
    assert offset >= 1, "Offset cannot be zero or negative"
    logger.info(
        "Retrieving forum post data for site %s thread %d (offset %d)",
        site_slug,
        thread_id,
        offset,
    )

    html = wikidot.ajax_module_connector(
        site_slug,
        "forum/ForumViewThreadModule",
        {"t": thread_id, "pageNo": offset},
    )
    soup = make_soup(html)
    source = f"forum category {category_id} thread {thread_id}"

    # Get header information
    breadcrumbs = assert_is_tag(soup.find("div", class_="forum-breadcrumbs"), "breadcrumbs")
    _, category_anchor = breadcrumbs.find_all("a")
    category_id_ex = regex_extract_int(
        source,
        category_anchor.attrs["href"],
        CATEGORY_ID_REGEX,
    )
    assert category_id == category_id_ex, "category ID in scraped thread doesn't match"

    thread_title_child = tuple(breadcrumbs.children)[-1]
    assert isinstance(
        thread_title_child,
        str,
    ), "last element in forum breadcrumbs is not text"
    thread_title = regex_extract_str(source, thread_title_child, THREAD_TITLE)

    # Here, we could get the forum thread's creator, created time, and description.
    # However we already got that above so it's not necessary here.

    # Iterate through posts
    container = assert_is_tag(soup.find(id="thread-container-posts"), "thread container")
    return list(
        map(
            lambda post: process_post(source, post),
            container.find_all(class_="post"),
        )
    )
    # TODO queue per-post jobs into batches of at most 10
    #      we don't need to be *that* efficient, just group
    #      by thread, so if a thread has < 10 posts just put
    #      them in one request and that's that


def process_post(source: str, post: Tag) -> ForumPostData:
    post_id = regex_extract_int(source, post.attrs["id"], POST_ID)
    source = f"{source} post {post_id}"

    title = find_element(source, post, class_="title").text.strip()
    started = find_element(source, post, class_="info")
    created_at = get_entity_date(
        source,
        find_element(source, started, "span", class_="odate"),
    )
    created_by = get_entity_user(
        source,
        find_element(source, started, class_="printuser"),
    )
    html = find_element(source, post, class_="content").decode_contents().strip()

    # NOTE: basic list of revisions can be seen in
    #       changes = post.find(class_="changes")

    # Process parents to determine inheritance
    # Structure is: [child (this post), parent, grandparent, etc.]
    # In other words:
    # * An orphan looks like:     [1000]
    # * A level-1 post looks like [1000, 2000]
    # * A level-2 post looks like [1000, 2000, 3000]
    # * etc
    parents = tuple(post.find_parents("div", class_="post-container"))
    match len(parents):
        case 1:
            # post is orphan
            parent = None
        case _:
            # post has a parent
            element = parents[1]
            parent = regex_extract_int(source, element.attrs["id"], POST_ID)

    return ForumPostData(
        id=post_id,
        parent=parent,
        title=title,
        created_at=created_at,
        created_by=created_by,
        html=html,
    )
