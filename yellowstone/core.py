"""
The backup dispatcher.

This class instance runs the core of the server, which intakes new events
and processes new tasks to be run in response.
"""

import json
from enum import Enum, unique
from typing import NoReturn, TypedDict

import pugsql

from .config import Config, getenv
from .s3 import S3
from .types import Json
from .wikidot import Wikidot


@unique
class JobType(Enum):
    INDEX_SITE_PAGES = "index-site-pages"
    INDEX_SITE_FORUMS = "index-site-forums"
    INDEX_SITE_MEMBERS = "index-site-members"


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
        while True:
            self.queue_all_sites()
            self.process_all_jobs()

    def queue_all_sites(self) -> None:
        for site_slug in self.config.site_slugs:
            self.add_job(JobType.INDEX_SITE_PAGES, site_slug)
            self.add_job(JobType.INDEX_SITE_FORUMS, site_slug)
            self.add_job(JobType.INDEX_SITE_MEMBERS, site_slug)

    def add_job(self, job_type: JobType, job_object: str, data: Json = None) -> None:
        self.database.add_job(
            job_type=job_type.value,
            job_object=job_object,
            data=json.dumps(data),
        )

    def process_all_jobs(self) -> None:
        while True:
            jobs = self.database.get_jobs()
            if not jobs:
                # No more jobs
                return

            for job in jobs:
                self.process_job(job)

    def process_job(self, job: JobDict) -> None:
        job_type = JobType(job["job_type"])
        match job_type:
            case JobType.INDEX_SITE_PAGES:
                raise NotImplemented
            case JobType.INDEX_SITE_FORUMS:
                raise NotImplemented
            case JobType.INDEX_SITE_MEMBERS:
                raise NotImplemented
