"""
Retrieves the next page of the list of forum threads within a category.

If present, then queue the threads for ingestion, as well
as the next page of the list.
"""

import logging
from typing import TYPE_CHECKING, Optional, TypedDict, Union

from ..request import forum_threads
from ..request.forum_threads import ForumThreadData

if TYPE_CHECKING:
    from ..core import BackupDispatcher

logger = logging.getLogger(__name__)


class ForumThreadsJob(TypedDict):
    site_slug: str
    offset: Optional[int]
    category_id: int


class ForumThreadProgressRow(TypedDict):
    post_count: int
    last_offset: Optional[int]
    last_post_id: Optional[int]


def run(core: "BackupDispatcher", data: ForumThreadsJob) -> None:
    site_slug = data["site_slug"]
    category_id = data["category_id"]

    # Fetch posts from each offset of this thread until it is exhausted
    offset = data["offset"] or 1
    threads: Union[list[ForumThreadData], bool] = True

    while threads:
        threads = forum_threads.get(
            site_slug,
            category_id=category_id,
            offset=offset,
            wikidot=core.wikidot,
        )
        offset += 1
        # TODO save threads


def needs_update(
    last_progress: ForumThreadProgressRow,
    thread: forum_threads.ForumThreadData,
) -> bool:
    if thread.post_count > last_progress["post_count"]:
        logger.debug(
            "Forum thread %d has more posts (%d > %d)",
            thread.id,
            thread.post_count,
            last_progress["post_count"],
        )
        return True

    if thread.last_post is not None:
        last_post_id = last_progress["last_post_id"] or 0
        if thread.last_post.post_id > last_post_id:
            logger.debug(
                "Forum thread %d has a new post ID (%d > %d)",
                thread.id,
                last_post_id,
            )
            return True

    logger.debug("Forum thread %d has nothing new to index", thread.id)
    return False
