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
    # TODO
    ...


def get(
    site_slug: str,
    *,
    category_id: int,
    thread_id: int,
    post_id: int,
    revision_id: int,
    wikidot: Wikidot,
) -> list[str]:
    ...

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

    html = wikidot.ajax_module_connector(
        site_slug,
        "forum/sub/ForumPostRevisionModule",
        {"revisionId": revision_id},
    )
    _ = html
    # TODO
    raise NotImplementedError
