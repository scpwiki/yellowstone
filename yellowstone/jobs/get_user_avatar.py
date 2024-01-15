"""
Stores the current avatar for a user.
"""

import logging

from ..exceptions import JobFailed
from ..requests import user_avatar
from ..core import BackupDispatcher

logger = logging.getLogger(__name__)


def get_user_avatar(core: BackupDispatcher, *, user_slug: str, user_id: int) -> None:
    logging.info("Downloading avatar for user '%s' (%d)", user_slug, user_id)
    user = core.database.get_user_by_id(user_id=user_id)
    if user is None:
        logging.error("No user found with this ID, marking as deleted")
        raise JobFailed

    avatar = user_avatar.get(user_id)
    hash = core.s3.upload_avatar(avatar)
    core.database.add_user_avatar(hash=hash, user_id=user_id)
