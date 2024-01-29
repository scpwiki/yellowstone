"""
Retrieves the next page of the list of forum threads within a category.

If present, then queue the threads for ingestion, as well
as the next page of the list.
"""

import logging
from typing import TYPE_CHECKING, TypedDict

if TYPE_CHECKING:
    from ..core import BackupDispatcher

logger = logging.getLogger(__name__)


class ForumThreadsJob(TypedDict):
    site_slug: str
    category_id: int


def run(core: "BackupDispatcher", data: ForumThreadsJob) -> None:
    # TODO
    pass
