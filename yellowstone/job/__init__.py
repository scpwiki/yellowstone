"""
Contains all jobs which can be invoked by the service.

This refers to high-level operations which retrieve some
usable chunk of information from various sources within
Wikidot. For instance, a combination of an XMLRPC API call
and scraping.
"""

import json
import logging
from enum import Enum, unique
from typing import TYPE_CHECKING, TypedDict, cast

from ..exception import UnknownJobError
from ..types import Json
from . import (
    get_user,
    get_user_avatar,
    index_forum_categories,
    index_forum_threads,
    index_site_members,
)
from .get_user import GetUserJob
from .get_user_avatar import GetUserAvatarJob
from .index_forum_threads import ForumThreadsJob
from .index_site_members import SiteMemberJob

if TYPE_CHECKING:
    from ..core import BackupDispatcher

logger = logging.getLogger(__name__)

MAX_RETRIES = 4


@unique
class JobType(Enum):
    INDEX_SITE_PAGES = "index-site-pages"
    INDEX_SITE_MEMBERS = "index-site-members"
    INDEX_FORUM_CATEGORIES = "index-forum-categories"
    INDEX_FORUM_THREADS = "index-forum-threads"
    FETCH_USER = "fetch-user"
    FETCH_USER_AVATAR = "fetch-user-avatar"


class JobDict(TypedDict):
    job_id: int
    job_type: str
    attempts: int
    data: Json


class JobManager:
    __slots__ = ("database",)

    def __init__(self, database):
        self.database = database

    def add_raw(self, type: JobType, data: Json) -> None:
        self.database.add_job(
            job_type=type.value,
            data=json.dumps(data),
        )

    def index_site_pages(self, data: None) -> None:
        self.add_raw(JobType.INDEX_SITE_PAGES, data)

    def index_site_members(self, data: SiteMemberJob) -> None:
        self.add_raw(JobType.INDEX_SITE_MEMBERS, cast(Json, data))

    def index_site_members_continue(self, site_slug: str) -> None:
        # Only queue if there already isn't a member index job for the site
        job = self.database.get_site_member_job(site_slug=site_slug)
        if job is not None:
            logger.debug("Found an index-site-members job for this site")
            return

        # Reads the last member page, and continues from there
        result = self.database.get_last_member_offset(site_slug=site_slug)
        self.index_site_members(
            {
                "site_slug": site_slug,
                "offset": result["last_member_offset"],
            },
        )

    def index_forum_categories(self, site_slug: str) -> None:
        self.add_raw(JobType.INDEX_FORUM_CATEGORIES, site_slug=site_slug)

    def index_forum_threads(self, data: ForumThreadsJob) -> None:
        self.add_raw(JobType.INDEX_FORUM_THREADS, cast(Json, data))

    def fetch_user(self, data: GetUserJob) -> None:
        self.add_raw(JobType.FETCH_USER, cast(Json, data))

    def fetch_user_avatar(self, data: GetUserAvatarJob) -> None:
        self.add_raw(JobType.FETCH_USER_AVATAR, cast(Json, data))

    def has(self) -> bool:
        row = self.database.has_jobs()
        exists = row["exists"]
        assert isinstance(exists, bool)
        return exists

    def process(self, core: "BackupDispatcher", job: JobDict) -> None:
        job_type = JobType(job["job_type"])
        data = job["data"]
        logger.info("Processing job %r", job)
        try:
            match job_type:
                case JobType.INDEX_SITE_PAGES:
                    raise NotImplementedError
                case JobType.INDEX_SITE_MEMBERS:
                    index_site_members.run(
                        core,
                        cast(index_site_members.SiteMemberJob, data),
                    )
                case JobType.INDEX_FORUM_CATEGORIES:
                    index_forum_categories.run(
                        core,
                        cast(index_forum_categories.ForumCategoriesJob, data),
                    )
                case JobType.INDEX_FORUM_THREADS:
                    index_forum_threads.run(
                        core,
                        cast(index_forum_threads.ForumThreadsJob, data),
                    )
                case JobType.FETCH_USER:
                    get_user.run(
                        core,
                        cast(get_user.GetUserJob, data),
                    )
                case JobType.FETCH_USER_AVATAR:
                    get_user_avatar.run(
                        core,
                        cast(get_user_avatar.GetUserAvatarJob, data),
                    )
                case _:
                    raise UnknownJobError(f"Unknown job type: {job_type}")
        except UnknownJobError:
            logger.error("Fatal: No job implementation", exc_info=True)
            raise
        except Exception as _:
            logger.error("Error occurred while processing job", exc_info=True)
            if job["attempts"] < MAX_RETRIES:
                logger.debug(
                    "Adding to attempt count, currently at %d",
                    job["attempts"],
                )
                self.database.fail_job(job_id=job["job_id"])
            else:
                logger.error("Job failed too many times, sending to dead letter queue")
                with self.database.transaction():
                    self.database.delete_job(job_id=job["job_id"])
                    self.database.add_dead_job(
                        job_id=job["job_id"],
                        job_type=job["job_type"],
                        data=json.dumps(job["data"]),
                    )
        else:
            logger.debug("Job completed successfully, removing from queue")
            self.database.delete_job(job_id=job["job_id"])
