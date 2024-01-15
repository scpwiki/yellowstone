"""
Retrieves all information associated with a user.
"""

import logging

from ..exceptions import JobFailed
from ..requests import user_avatar
from ..core import BackupDispatcher

logger = logging.getLogger(__name__)


def get_user(core: BackupDispatcher, *, user_slug: str) -> None:
    ...

    # enqueue get_user_avatar for this user
