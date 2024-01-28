"""
Retrieves all forum groups and categories for this site.

This then queues each forum category for thread indexing.
"""

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..core import BackupDispatcher

logger = logging.getLogger(__name__)


def run(core: "BackupDispatcher", *, site_slug: str) -> None:
    # Clear out previous forum groups
    core.database.delete_forum_groups(site_slug=site_slug)

    groups = forum_categories.get(site_slug, wikidot=core.wikidot)
    for group in groups:
        # Re-insert forum groups, get our IDs for them
        group_internal_id = core.database.add_forum_group(
            site_slug=site_slug,
            name=group.name,
            description=group.description,
            )

        # Upsert forum categories, associating internal forum group IDs
        for category in group.categories:
            core.database.add_forum_category(
                group_id=group_internal_id,
                category_id=category.id,
                name=category.name,
                description=category.description,
            )
            core.database.set_forum_category_progress(
                category_id=category.id,
                thread_count=category.thread_count,
                post_count=category.post_count,
                last_thread_id=getattr(category.last_post, "thread_id", None),
                last_post_id=getattr(category.last_post, "post_id", None),
            )
