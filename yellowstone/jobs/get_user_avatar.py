"""
Stores the current avatar for a user.
"""

import logging
from typing import TYPE_CHECKING

from ..requests import user_avatar

if TYPE_CHECKING:
    from ..core import BackupDispatcher

logger = logging.getLogger(__name__)


def run(core: "BackupDispatcher", *, user_slug: str, user_id: int) -> None:
    logger.info("Downloading avatar for user '%s' (%d)", user_slug, user_id)
    avatar = user_avatar.get(user_id)
    hash = core.s3.upload_avatar(avatar)
    core.database.add_user_avatar(hash=hash, user_id=user_id)
