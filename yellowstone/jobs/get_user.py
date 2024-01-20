"""
Retrieves all information associated with a user.
"""

import logging
from typing import TYPE_CHECKING, TypedDict

from ..requests import user as user_data
from . import add_fetch_user_avatar_job

if TYPE_CHECKING:
    from ..core import BackupDispatcher

logger = logging.getLogger(__name__)


class GetUserJob(TypedDict):
    user_id: int


def run(core: "BackupDispatcher", data: GetUserJob) -> None:
    user_id = data["user_id"]
    logger.info("Retrieving user information for user ID %d", user_id)

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
    add_fetch_user_avatar_job(core.database, data)
