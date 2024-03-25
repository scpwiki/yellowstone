"""
Retrieve posts in a forum thread by page.
"""

import logging
import re
from collections import namedtuple
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from bs4 import Tag

from ..scraper import (
    find_element,
    get_entity_user,
    make_soup,
    regex_extract_int,
)
from ..types import ForumPostUser, assert_is_tag
from ..utils import chunks
from ..wikidot import Wikidot
from .forum_categories import CATEGORY_ID_REGEX

logger = logging.getLogger(__name__)

THREAD_TITLE = re.compile(r"\s*» (.+?)\s*")
POST_ID = re.compile(r"(?:post|fpc)-(\d+)")

ForumPostDataPartial = namedtuple("ForumPostDataPartial", ("id", "created_by"))


@dataclass
class ForumPostData:
    id: int
    parent: Optional[int]
    title: str
    created_by: ForumPostUser
    created_at: datetime
    wikitext: str
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
    breadcrumbs = assert_is_tag(
        soup.find("div", class_="forum-breadcrumbs"),
        "breadcrumbs",
    )
    _, category_anchor = breadcrumbs.find_all("a")
    category_id_ex = regex_extract_int(
        source,
        category_anchor.attrs["href"],
        CATEGORY_ID_REGEX,
    )
    assert category_id == category_id_ex, "category ID in scraped thread doesn't match"

    # Here, we could get the forum thread's creator, created time, and description.
    # However we already got that above so it's not necessary here.

    # Iterate through posts, build most of the data
    container = assert_is_tag(
        soup.find(id="thread-container-posts"),
        "thread container",
    )
    partial_posts = tuple(
        map(
            lambda post: process_post_partial(source, post),
            container.find_all(class_="post"),
        )
    )

    # Then do batch post fetches until everything is populated.
    # Wikidot allows at most 10 posts to be fetched per request.
    posts: list[ForumPostData] = []
    for chunk in chunks(partial_posts, 10):
        results = wikidot.proxy.posts.get(
            {
                "site": site_slug,
                "posts": [str(post.id) for post in chunk],
            }
        )
        for partial in chunk:
            assert isinstance(partial, dict)
            data = results[str(partial.id)]

            assert partial.id == data["id"]
            posts.append(
                ForumPostData(
                    id=partial.id,
                    parent=data["reply_to"],
                    title=data["title"],
                    created_by=partial.created_by,
                    created_at=datetime.fromisoformat(data["created_at"]),
                    wikitext=data["content"],
                    html=data["html"].strip(),
                )
            )

    return posts


def process_post_partial(source: str, post: Tag) -> ForumPostDataPartial:
    post_id = regex_extract_int(source, post.attrs["id"], POST_ID)
    source = f"{source} post {post_id}"

    started = find_element(source, post, class_="info")
    created_by = get_entity_user(
        source,
        find_element(source, started, class_="printuser"),
    )

    # NOTE: Basic list of revisions can be seen in
    #       changes = post.find(class_="changes")

    # NOTE: You can get a list of the parentage with
    #       parents = tuple(post.find_parents("div", class_="post-container"))
    #
    # Process parents to determine inheritance
    # Structure is: [child (this post), parent, grandparent, etc.]
    # In other words:
    # * An orphan looks like:     [1000]
    # * A level-1 post looks like [1000, 2000]
    # * A level-2 post looks like [1000, 2000, 3000]
    # * etc

    return ForumPostDataPartial(
        id=post_id,
        created_by=created_by,
    )
