"""
Retrieves the next page of the list of site members.

If present, then queue the users for ingestion, as well
as the next page of the list.
"""

import logging
from typing import Optional

from ..core import BackupDispatcher
from .. import JobType
from ..requests import site_members

START_OFFSET = 1

logger = logging.getLogger(__name__)


def run(core: BackupDispatcher, *, site_slug: str, offset: Optional[int]) -> None:
    offset = offset or START_OFFSET
    site_id = core.site_id_cache[site_slug]
    logger.info(
        "Retrieving page %d of site members from '%s' (%d)",
        offset,
        site_slug,
        site_id,
    )

    # Make request and process all results
    members = site_members.get(
        site_slug,
        offset,
        wikidot=core.wikidot,
        use_admin=core.config.uses_admin_members(site_slug),
    )

    if members:
        with core.database.transaction():
            # Queue the next offset, for iterating over pages using the job queue
            core.add_job(JobType.INDEX_SITE_MEMBERS, site_slug, offset + 1)

            # Add all site members, and queue their users for update
            for member in members:
                core.database.add_site_member(
                    user_id=member.id,
                    site_id=site_id,
                    joined_at=member.joined_at,
                )
                core.add_job(JobType.FETCH_USER, member.slug, member.id)
