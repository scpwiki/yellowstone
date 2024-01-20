"""
The backup dispatcher.

This class instance runs the core of the server, which intakes new events
and processes new tasks to be run in response.
"""

import json
import logging
import time
from typing import NoReturn, TypedDict, cast

import pugsql

from .config import Config, getenv
from .exceptions import UnknownJobError
from .jobs import (
    JobType,
    add_index_site_members_job,
    get_site,
    get_user,
    get_user_avatar,
    index_site_members,
)
from .jobs.index_site_members import START_OFFSET as START_MEMBER_OFFSET
from .s3 import S3
from .types import Json
from .wikidot import Wikidot

MAX_RETRIES = 4
FULL_WORKLOAD_PAUSE = 10

logger = logging.getLogger(__name__)


class JobDict(TypedDict):
    job_id: int
    job_type: str
    job_object: str
    attempts: int
    data: Json


class BackupDispatcher:
    __slots__ = (
        "config",
        "wikidot",
        "database",
        "s3",
        "site_id_cache",
    )

    config: Config
    wikidot: Wikidot
    s3: S3
    site_id_cache: dict[str, int]

    def __init__(self, config) -> None:
        self.config = config
        self.wikidot = Wikidot(config)
        self.database = pugsql.module("queries/")
        self.database.connect(getenv("POSTGRES_DATABASE_URL"))
        self.s3 = S3(config)
        self.site_id_cache = {}

    def run(self) -> NoReturn:
        logger.info("Running Yellowstone dispatcher")
        self.insert_all_sites()
        while True:
            self.queue_all_sites()
            self.process_all_jobs()
            logger.info("Finished everything! Starting new process cycle")
            time.sleep(FULL_WORKLOAD_PAUSE)

    def insert_all_sites(self) -> None:
        for site_slug in self.config.site_slugs:
            logger.info("Inserting site '%s' into database", site_slug)
            get_site.run(self, site_slug=site_slug)

    def queue_all_sites(self) -> None:
        for site_slug in self.config.site_slugs:
            logger.info("Queueing site start jobs for '%s'", site_slug)
            # XXX add_index_site_pages_job(site_slug)
            # XXX add_index_site_forums_job(site_slug)
            add_index_site_members_job(
                self.database,
                {
                    "site_slug": site_slug,
                    "offset": START_MEMBER_OFFSET,
                },
            )

    def process_all_jobs(self) -> None:
        logger.info("Processing all jobs in queue")
        while True:
            job = self.database.get_job()
            if job is None:
                break
            self.process_job(job)
        logger.info("No more jobs received, done")

    def has_jobs(self) -> bool:
        row = self.database.has_jobs()
        exists = row["exists"]
        assert isinstance(exists, bool)
        return exists

    def process_job(self, job: JobDict) -> None:
        job_type = JobType(job["job_type"])
        data = job["data"]
        logger.info("Processing job %r", job)
        try:
            match job_type:
                case JobType.INDEX_SITE_PAGES:
                    raise NotImplementedError
                case JobType.INDEX_SITE_FORUMS:
                    raise NotImplementedError
                case JobType.INDEX_SITE_MEMBERS:
                    index_site_members.run(
                        self,
                        cast(index_site_members.SiteMemberJob, data),
                    )
                case JobType.FETCH_USER:
                    get_user.run(self, cast(get_user.GetUserJob, data))
                case JobType.FETCH_USER_AVATAR:
                    get_user_avatar.run(
                        self,
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
                        job_object=job["job_object"],
                        data=json.dumps(job["data"]),
                    )
        else:
            logger.debug("Job completed successfully, removing from queue")
            self.database.delete_job(job_id=job["job_id"])
