"""
Retrieves the basic structure for the forums in a site.
Required for all later forum processing on this site.
"""

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..core import BackupDispatcher

logger = logging.getLogger(__name__)


def run(core: "BackupDispatcher", *, site_slug: str) -> None:
    groups = forum_categories.get(site_slug, wikidot=core.wikidot)
    for group in groups:
        group_internal_id = core.database.add_forum_group(
            site_slug=site_slug,
            name=group.name,
            description=group.description,
            )

        for category in group.categories:
            core.database.add_forum_category(
                group_id=group_internal_id,
                category_id=category.id,
                name=category.name,
                description=category.description,
            )
            core.database.set_forum_category_progress(
                category_id=category.id,
            )
