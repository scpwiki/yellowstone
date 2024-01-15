"""
Retrieves all information associated with a user.
"""

import logging
from typing import TYPE_CHECKING

from ..requests import user as user_data
from . import JobType

if TYPE_CHECKING:
    from ..core import BackupDispatcher

logger = logging.getLogger(__name__)


def run(core: "BackupDispatcher", *, user_slug: str, user_id: int) -> None:
    logger.info("Retrieving user information for '%s' (%d)", user_slug, user_id)

    user = user_data.get(user_id, wikidot=core.wikidot)
    core.database.add_user(
        user_slug=user.slug,
        user_name=user.name,
        user_id=user.id,
        created_at=user.created_at,
        real_name=user.real_name,
        gender=user.gender,
        birthday=user.birthday,
        location=user.location,
        website=user.website,
        bio=user.bio,
        wikidot_pro=user.wikidot_pro,
        karma=user.karma,
    )

    # Enqueue avatar job
    core.add_job(JobType.FETCH_USER_AVATAR, user_slug, user_id)
