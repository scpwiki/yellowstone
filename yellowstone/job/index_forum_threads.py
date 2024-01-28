"""
Retrieves the next page of the list of forum threads within a category.

If present, then queue the threads for ingestion, as well
as the next page of the list.
"""

from typing import TypedDict


class ForumThreadsJob(TypedDict):
    pass


def run(core: "BackupDispatcher", *, data: ForumThreadsJob) -> None:
    # TODO
    pass
