"""
The backup dispatcher.

This class instance runs the core of the server, which intakes new events
and processes new tasks to be run in response.
"""

import logging
import time
from typing import NoReturn

import pugsql

from .config import Config, getenv
from .job import (
    JobManager,
    get_site,
)
from .s3 import S3
from .wikidot import Wikidot

FULL_WORKLOAD_PAUSE = 10

logger = logging.getLogger(__name__)


class BackupDispatcher:
    __slots__ = (
        "config",
        "wikidot",
        "database",
        "job",
        "s3",
        "site_id_cache",
    )

    config: Config
    wikidot: Wikidot
    job: JobManager
    s3: S3
    site_id_cache: dict[str, int]

    def __init__(self, config) -> None:
        self.config = config
        self.wikidot = Wikidot(config)
        self.database = pugsql.module("queries/")
        self.database.connect(getenv("POSTGRES_DATABASE_URL"))
        self.job = JobManager(self.database)
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
            self.job.index_site_members(
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
            self.job.process(self, job)
        logger.info("No more jobs received, done")
