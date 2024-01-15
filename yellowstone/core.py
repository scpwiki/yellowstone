"""
The backup dispatcher.

This class instance runs the core of the server, which intakes new events
and processes new tasks to be run in response.
"""

import json
import logging
from enum import Enum, unique
from typing import NoReturn, TypedDict

import pugsql

from .config import Config, getenv
from .jobs import *
from .s3 import S3
from .types import Json
from .wikidot import Wikidot

MAX_RETRIES = 5

logger = logging.getLogger(__name__)


@unique
class JobType(Enum):
    INDEX_SITE_PAGES = "index-site-pages"
    INDEX_SITE_FORUMS = "index-site-forums"
    INDEX_SITE_MEMBERS = "index-site-members"
    FETCH_USER = "fetch-user"
    FETCH_USER_AVATAR = "fetch-user-avatar"


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
    )

    config: Config
    wikidot: Wikidot
    s3: S3

    def __init__(self, config) -> None:
        self.config = config
        self.wikidot = Wikidot()
        self.database = pugsql.module("queries/")
        self.database.connect(getenv("POSTGRES_DATABASE_URL"))
        self.s3 = S3(config)

    def run(self) -> NoReturn:
        logger.info("Running Yellowstone dispatcher")
        while True:
            logger.info("Starting new process cycle")
            self.queue_all_sites()
            self.process_all_jobs()

    def queue_all_sites(self) -> None:
        for site_slug in self.config.site_slugs:
            logger.info("Queueing site start jobs")
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
        value = job["job_object"]
        data = json.loads(job["data"])
        logger.info("Processing job %r", job)
        try:
            match job_type:
                case JobType.INDEX_SITE_PAGES:
                    raise NotImplementedError
                case JobType.INDEX_SITE_FORUMS:
                    raise NotImplementedError
                case JobType.INDEX_SITE_MEMBERS:
                    raise NotImplementedError
                case JobType.FETCH_USER:
                    assert data is None, "GET_USER job has no data"
                    fetch_user(self, user_slug=value)
                case JobType.FETCH_USER_AVATAR:
                    assert isinstance(data, int), "GET_USER_AVATAR job data not integer"
                    fetch_user_avatar(self, user_slug=value, user_id=data)
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
        except Exception as error:
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
