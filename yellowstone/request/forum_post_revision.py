"""
Retrieve the HTML data associated with an individual forum post revision.

Unfortunately, we cannot get the original wikitext through this mechanism,
so only the most recent post revision's wikitext is known. Unknown wikitexts
are stored as NULL in the database.
"""

import logging
from dataclasses import dataclass

from ..wikidot import Wikidot

logger = logging.getLogger(__name__)


@dataclass
class ForumPostRevisionData:
    revision_id: int
    post_id: int
    title: str
    html: str


def get(
    site_slug: str,
    *,
    category_id: int,
    thread_id: int,
    post_id: int,
    revision_id: int,
    wikidot: Wikidot,
) -> ForumPostRevisionData:
    logger.info(
        (
            "Retrieving forum post revision HTML for "
            "site %s category %d thread %d post %d revision %d"
        ),
        site_slug,
        category_id,
        thread_id,
        post_id,
        revision_id,
    )

    response = wikidot.ajax_module_connector_json(
        site_slug,
        "forum/sub/ForumPostRevisionModule",
        {"revisionId": revision_id},
    )
    assert response["body"] == "ok", "Response body not 'ok'"
    assert response["postId"] == post_id, "Post ID does not match response"
    return ForumPostRevisionData(
        revision_id=revision_id,
        post_id=post_id,
        title=response["title"],
        html=response["content"].strip(),
    )
