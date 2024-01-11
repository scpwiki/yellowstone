"""
The backup dispatcher.

This class instance runs the core of the server, which intakes new events
and processes new tasks to be run in response.
"""

from .config import Config
from .wikidot import Wikidot


class BackupDispatcher:
    __slots__ = (
        "config",
        "wikidot",
    )

    config: Config
    wikidot: Wikidot

    def __init__(self, config):
        self.config = config
        self.wikidot = Wikidot()

    async def main_loop(self):
        pass
