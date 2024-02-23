"""
Retrieve a listing of revisions within a forum post.
"""

import logging
from dataclasses import dataclass

from ..scraper import (
    make_soup,
)
from ..wikidot import Wikidot

logger = logging.getLogger(__name__)


@dataclass
class ForumPostRevisionData:
    # TODO
    ...


def get(
    site_slug: str,
    *,
    category_id: int,
    thread_id: int,
    post_id: int,
    wikidot: Wikidot,
) -> list[ForumPostRevisionData]:
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
    # TODO
    _ = soup
