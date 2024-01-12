"""
The backup dispatcher.

This class instance runs the core of the server, which intakes new events
and processes new tasks to be run in response.
"""

import pugsql

from .config import Config, getenv
from .wikidot import Wikidot


class BackupDispatcher:
    __slots__ = (
        "config",
        "wikidot",
        "database",
    )

    config: Config
    wikidot: Wikidot

    def __init__(self, config):
        self.config = config
        self.wikidot = Wikidot()
        self.database = pugsql.module("queries/")
        self.database.connect(getenv("POSTGRES_DATABASE_URL"))

    def main_loop(self):
        pass
