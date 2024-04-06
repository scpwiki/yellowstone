"""
Wrapper for the XML-RPC Wikidot API.
"""

import logging
from typing import Any
from xmlrpc.client import ServerProxy

from .config import getenv

logger = logging.getLogger(__name__)


class WikidotApi:
    proxy: ServerProxy

    def __init__(self, username=None, api_key=None):
        username = username or getenv("WIKIDOT_USERNAME")
        api_key = api_key or getenv("WIKIDOT_API_KEY")
        self.proxy = ServerProxy(
            f"https://{username}:{api_key}@www.wikidot.com/xml-rpc-api.php",
            use_builtin_types=True,
            use_datetime=True,
        )

    def posts_get(self, *, site: str, posts: list[str]) -> dict[str, dict[str, Any]]:
        return self.proxy.posts.get(
            {
                "site": site,
                "posts": posts,
            }
        )
