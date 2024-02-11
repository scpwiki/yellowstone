"""
Retrieve a listing of revisions within a forum post.
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
    select_element,
    get_entity_date,
    get_entity_user,
    make_soup,
    regex_extract_int,
)
from ..types import ForumLastPostData, UserModuleData
from ..wikidot import Wikidot

logger = logging.getLogger(__name__)


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
