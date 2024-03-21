"""
Retrieve a listing of revisions within a forum post.
"""

import logging
import re

from ..scraper import (
    make_soup,
    regex_extract_int,
)
from ..wikidot import Wikidot

REVISION_ID_REGEX = re.compile(
    r"WIKIDOT\.modules\.ForumViewThreadModule\.listeners\.showRevision\(event, (\d+)\)"
)

logger = logging.getLogger(__name__)


def get(
    site_slug: str,
    *,
    category_id: int,
    thread_id: int,
    post_id: int,
    wikidot: Wikidot,
) -> list[int]:
    ...

    logger.info(
        "Retrieving forum post revision data for site %s category %d thread %d post %d",
        site_slug,
        category_id,
        thread_id,
        post_id,
    )

    html = wikidot.ajax_module_connector(
        site_slug,
        "forum/sub/ForumPostRevisionsModule",
        {"postId": post_id},
    )
    soup = make_soup(html)
    source = f"forum post {post_id}"
    revision_ids = []

    for element in soup.select('td a[href="javascript:;"]'):
        revision_ids.append(
            regex_extract_int(source, element.attrs["onclick"], REVISION_ID_REGEX),
        )

    revision_ids.reverse()
    return revision_ids
