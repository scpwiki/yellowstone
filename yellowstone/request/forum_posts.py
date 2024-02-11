"""
Retrieve posts in a forum thread by page.
"""

import logging
import re
from dataclasses import dataclass

from bs4 import Tag

from ..scraper import (
    find_element,
    get_entity_date,
    get_entity_user,
    make_soup,
    regex_extract_int,
    regex_extract_str,
)
from ..wikidot import Wikidot
from .forum_categories import CATEGORY_ID_REGEX

logger = logging.getLogger(__name__)

THREAD_TITLE = re.compile(r"\s*» (.+?)\s*")
POST_ID = re.compile(r"post-(\d+)")  # NOTE: post-container uses fpc-XXXX instead


@dataclass
class ForumPostData:
    ...


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
        {"t": thread_id},
    )
    soup = make_soup(html)
    source = f"forum category {category_id} thread {thread_id}"

    # Get header information
    breadcrumbs = soup.find("div", class_="forum-breadcrumbs")
    _, category_anchor = breadcrumbs.find_all("a")
    category_id_ex = regex_extract_int(source, category_anchor.attrs["href"], CATEGORY_ID_REGEX)
    assert category_id == category_id_ex, "category ID in scraped thread doesn't match"

    thread_title = tuple(breadcrumbs.children)[-1]
    assert isinstance(thread_title, str), "last element in forum breadcrumbs is not text"
    thread_title = regex_extract_str(source, thread_title, THREAD_TITLE)

    # Here, we could get the forum thread's creator, created time, and description.
    # However we already got that above so it's not necessary here.

    # Iterate through posts
    container = soup.find(id="thread-container-posts")
    return list(
        map(
            lambda post: process_post(source, post),
            soup.find_all(class_="post"),
        )
    )


def process_post(source: str, post: Tag) -> ForumPostData:
    post_id = regex_extract_int(source, post.attrs["id"], POST_ID)
    source = f"{source} post {post_id}"

    # Get post data
    title = find_element(source, post, class_="title").text.strip()
    started = find_element(source, post, class_="info")
    created_at = get_entity_date(source, find_element(source, started, "span", class_="odate"))
    created_by = get_entity_user(source, select_element(source, started, ".printuser a"))
    html = str(find_element(source, post, class_="content"))

    # Get basic revision metadata
    changes = post.find(class_="changes")
    if changes is None:
        # No revisions
        # TODO
    else:
        # TODO go through each

    import pdb; pdb.set_trace()
    ...

    # XXX process post structure
    # We only need one parent up because that parent will also know its parent, etc.
    parent = post.find_parent("div", class_="post")

    # TODO queue per-post jobs into batches of at most 10
    #      we don't need to be *that* efficient, just group
    #      by thread, so if a thread has < 10 posts just put
    #      them in one request and that's that
