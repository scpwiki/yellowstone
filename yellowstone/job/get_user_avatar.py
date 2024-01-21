"""
Stores the current avatar for a user.
"""

import logging
from typing import TYPE_CHECKING, TypedDict

from ..request import user_avatar

if TYPE_CHECKING:
    from ..core import BackupDispatcher

logger = logging.getLogger(__name__)


class GetUserAvatarJob(TypedDict):
    user_id: int


def run(core: "BackupDispatcher", data: GetUserAvatarJob) -> None:
    user_id = data["user_id"]
    logger.info("Downloading avatar for user ID %d", user_id)
    avatar = user_avatar.get(user_id)
    hash = core.s3.upload_avatar(avatar)
    core.database.add_user_avatar(hash=hash, user_id=user_id)
