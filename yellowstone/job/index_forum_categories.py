"""
Retrieves all forum groups and categories for this site.

This then queues each forum category for thread indexing.
This is the top-level job for forums in a site.
"""

import logging
from typing import TYPE_CHECKING, Optional, TypedDict

from ..request import forum_categories
from ..utils import sql_array

if TYPE_CHECKING:
    from ..core import BackupDispatcher

logger = logging.getLogger(__name__)


class ForumCategoriesJob(TypedDict):
    site_slug: str


class ForumCategoryProgressRow(TypedDict):
    thread_count: int
    post_count: int
    last_thread_id: Optional[int]
    last_post_id: Optional[int]


def run(core: "BackupDispatcher", data: ForumCategoriesJob) -> None:
    site_slug = data["site_slug"]

    # Clear out and re-insert forum groups
    core.database.delete_forum_groups(site_slug=site_slug)

    groups = forum_categories.get(site_slug, wikidot=core.wikidot)
    for group in groups:
        core.database.add_forum_group(
            site_slug=site_slug,
            name=group.name,
            description=group.description,
            category_ids=sql_array(category.id for category in group.categories),
        )

        for category in group.categories:
            logger.info("Indexing forum category '%s' (%d)", category.name, category.id)

            # Upsert forum categories, associating internal forum group IDs
            core.database.add_forum_category(
                category_id=category.id,
                site_slug=site_slug,
                name=category.name,
                description=category.description,
            )

            # Update progress, and if needed, queue
            progress = core.database.get_forum_category_progress(
                category_id=category.id,
            )
            core.database.set_forum_category_progress(
                category_id=category.id,
                thread_count=category.thread_count,
                post_count=category.post_count,
                last_thread_id=getattr(category.last_post, "thread_id", None),
                last_post_id=getattr(category.last_post, "post_id", None),
            )

            if progress is None or needs_update(progress, category):
                core.job.index_forum_threads(
                    {"site_slug": site_slug, "category_id": category.id, "offset": None},
                )


def needs_update(
    last_progress: ForumCategoryProgressRow,
    category: forum_categories.ForumCategoryData,
) -> bool:
    if category.thread_count > last_progress["thread_count"]:
        logger.debug(
            "Forum category %d has more threads (%d > %d)",
            category.id,
            category.thread_count,
            last_progress["thread_count"],
        )
        return True

    if category.post_count > last_progress["post_count"]:
        logger.debug(
            "Forum category %d has more posts (%d > %d)",
            category.id,
            category.post_count,
            last_progress["post_count"],
        )
        return True

    if category.last_post is not None:
        last_thread_id = last_progress["last_thread_id"] or 0
        if category.last_post.thread_id > last_thread_id:
            logger.debug(
                "Forum category %d has a new thread ID (%d > %d)",
                category.id,
                category.last_post.thread_id,
                last_thread_id,
            )
            return True

        last_post_id = last_progress["last_post_id"] or 0
        if category.last_post.post_id > last_post_id:
            logger.debug(
                "Forum category %d has a new post ID (%d > %d)",
                category.id,
                category.last_post.post_id,
                last_post_id,
            )
            return True

    logger.debug("Forum category %d has nothing new to index", category.id)
    return False
