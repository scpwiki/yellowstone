"""
The backup dispatcher.

This class instance runs the core of the server, which intakes new events
and processes new tasks to be run in response.
"""

import pugsql

from .config import Config, getenv
from .s3 import S3
from .wikidot import Wikidot


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

    def __init__(self, config):
        self.config = config
        self.wikidot = Wikidot()
        self.s3 = S3(config)
        self.database = pugsql.module("queries/")
        self.database.connect(getenv("POSTGRES_DATABASE_URL"))

    async def main_loop(self):
        pass
