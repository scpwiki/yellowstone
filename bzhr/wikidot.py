"""
Common utilities for interfacing with Wikidot.
"""

import os
from xmlrpc.client import ServerProxy

from .config import Config


class Wikidot:
    __slots__ = ("proxy",)

    def __init__(self):
        username = os.getenv("WIKIDOT_USERNAME")
        api_key = os.getenv("WIKIDOT_API_KEY")
        self.proxy = ServerProxy(
            f"https://{username}:{api_key}@www.wikidot.com/xml-rpc-api.php",
            use_builtin_types=True,
            use_datetime=True,
        )
