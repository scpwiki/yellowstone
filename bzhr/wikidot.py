"""
Common utilities for interfacing with Wikidot.
"""

from xmlrpc.client import ServerProxy

from .config import Config


class Wikidot:
    __slots__ = ("proxy",)

    def __init__(self, config: Config):
        self.proxy = ServerProxy(
            f"https://{config.wikidot_username}:{config.wikidot_api_key}@www.wikidot.com/xml-rpc-api.php",
            use_builtin_types=True,
            use_datetime=True,
        )
