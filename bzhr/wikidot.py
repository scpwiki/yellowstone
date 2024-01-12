"""
Common utilities for interfacing with Wikidot.
"""

from xmlrpc.client import ServerProxy

from .config import getenv


class Wikidot:
    __slots__ = ("proxy",)

    def __init__(self):
        username = getenv("WIKIDOT_USERNAME")
        api_key = getenv("WIKIDOT_API_KEY")
        self.proxy = ServerProxy(
            f"https://{username}:{api_key}@www.wikidot.com/xml-rpc-api.php",
            use_builtin_types=True,
            use_datetime=True,
        )
