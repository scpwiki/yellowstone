"""
Retrieves the next page of the list of site members.

If present, then queue the users for ingestion, as well
as the next page of the list.
"""

import logging
from typing import TYPE_CHECKING, TypedDict

from ..request import site_members

if TYPE_CHECKING:
    from ..core import BackupDispatcher

logger = logging.getLogger(__name__)


class SiteMemberJob(TypedDict):
    site_slug: str
    offset: int


def run(core: "BackupDispatcher", data: SiteMemberJob) -> None:
    site_slug = data["site_slug"]
    offset = data["offset"]["last_member_offset"]

    assert offset >= 1, "Offset cannot be zero or negative"
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

    # Save member data
    if members:
        with core.database.transaction():
            # Queue the next offset, for iterating over pages using the job queue
            core.job.index_site_members({"site_slug": site_slug, "offset": offset + 1})

            # Add all site members, and queue their users for update
            for member in members:
                core.database.add_site_member(
                    user_id=member.id,
                    site_id=site_id,
                    joined_at=member.joined_at,
                )
                core.job.fetch_user({"user_id": member.id})

    # Save member page progress
    core.database.update_last_member_offset(site_slug=site_slug, last_offset=offset)
