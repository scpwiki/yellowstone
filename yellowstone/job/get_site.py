"""
Retrieves basic information associated with a site.

Required for all later processing on this site.
Because of this, it's a special job that cannot
be re-queued, but is instead manually run at the
start of the process.
"""

import logging
from typing import TYPE_CHECKING

from ..request import site_home_raw
from ..wikidot import Wikidot

if TYPE_CHECKING:
    from ..core import BackupDispatcher

logger = logging.getLogger(__name__)


def run(core: "BackupDispatcher", *, site_slug: str) -> None:
    def should_fetch() -> bool:
        if core.config.always_fetch_site:
            return True

        site_row = core.database.get_site(site_slug=site_slug)
        if site_row is None:
            return True

        core.site_id_cache[site_slug] = site_row["wikidot_id"]
        return False

    if should_fetch():
        site = insert_site(site_slug, database=core.database, wikidot=core.wikidot)
        core.site_id_cache[site_slug] = site.id


def insert_site(
    site_slug: str,
    *,
    database,
    wikidot: Wikidot,
) -> site_home_raw.SiteHomeData:
    site = site_home_raw.get(site_slug, wikidot=wikidot)

    database.add_site(
        site_slug=site.slug,
        site_id=site.id,
        name=site.name,
        tagline=site.tagline,
        language=site.language,
        home_slug=site.home_page_slug,
    )
    database.add_site_progress(site_slug=site.slug)

    # TODO insert basic home data
    _ = site.home_page_id
    _ = site.home_page_discussion_thread_id
    _ = site.home_page_category_id

    return site
