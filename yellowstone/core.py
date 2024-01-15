"""
The backup dispatcher.

This class instance runs the core of the server, which intakes new events
and processes new tasks to be run in response.
"""

import json
import logging
from typing import NoReturn, Optional, TypedDict

import pugsql

from .config import Config, getenv
from .exceptions import UnknownJobError
from .jobs import JobType, get_site, get_user, get_user_avatar, index_site_members
from .s3 import S3
from .types import Json
from .wikidot import Wikidot

MAX_RETRIES = 4

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
        while True:
            logger.info("Starting new process cycle")
            self.insert_all_sites()
            self.queue_all_sites()
            self.process_all_jobs()

    def insert_all_sites(self) -> None:
        for site_slug in self.config.site_slugs:
            logger.info("Inserting site '%s' into database", site_slug)
            get_site.run(site_slug)

    def queue_all_sites(self) -> None:
        for site_slug in self.config.site_slugs:
            logger.info("Queueing site start jobs for '%s'", site_slug)
            self.add_job(JobType.INDEX_SITE_PAGES, site_slug)
            self.add_job(JobType.INDEX_SITE_FORUMS, site_slug)
            self.add_job(JobType.INDEX_SITE_MEMBERS, site_slug)

    def add_job(self, job_type: JobType, job_object: str, data: Json = None) -> None:
        logger.debug("Adding job %s for %s (data %r)", job_type.value, job_object, data)
        self.database.add_job(
            job_type=job_type.value,
            job_object=job_object,
            data=json.dumps(data),
        )

    def process_all_jobs(self) -> None:
        logger.info("Processing all jobs in queue")
        while True:
            jobs = self.database.get_jobs()
            if not jobs:
                logger.info("No more jobs received, done")
                return

            for job in jobs:
                self.process_job(job)

    def process_job(self, job: JobDict) -> None:
        job_type = JobType(job["job_type"])
        data = job["data"]
        value = job["job_object"]
        logger.info("Processing job %r", job)
        try:
            match job_type:
                case JobType.INDEX_SITE_PAGES:
                    raise NotImplementedError
                case JobType.INDEX_SITE_FORUMS:
                    raise NotImplementedError
                case JobType.INDEX_SITE_MEMBERS:
                    assert isinstance(data, Optional[int]), "INDEX_SITE_MEMBERS"
                    index_site_members.run(self, site_slug=value, offset=data)
                case JobType.FETCH_USER:
                    assert isinstance(data, int), "GET_USER"
                    get_user.run(self, user_slug=value, user_id=data)
                case JobType.FETCH_USER_AVATAR:
                    assert isinstance(data, int), "GET_USER_AVATAR"
                    get_user_avatar.run(self, user_slug=value, user_id=data)
                case _:
                    raise UnknownJobError(f"Unknown job type: {job_type}")
        except UnknownJobError:
            logger.error("Fatal: No job implementation", exc_info=True)
            raise
        except NotImplementedError:
            logger.error(
                "Job hit not-yet-implemented component, not increasing attempt count",
                exc_info=True,
            )
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
