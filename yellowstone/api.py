"""
Wrapper for the XML-RPC Wikidot API.
"""

import logging
from xmlrpc.client import ServerProxy

logger = logging.getLogger(__name__)


class WikidotApi:
    __slots__ = ("proxy",)

    def __init__(self, username=None, api_key=None):
        username = username or getenv("WIKIDOT_USERNAME")
        api_key = api_key or getenv("WIKIDOT_API_KEY")
        self.proxy = ServerProxy(
            f"https://{username}:{api_key}@www.wikidot.com/xml-rpc-api.php",
            use_builtin_types=True,
            use_datetime=True,
        )

    def posts_get(self, *, site_slug: str, posts: list[str]) -> dict[str, dict]:
        return self.proxy.posts.get(
            {
                "site": site_slug,
                "posts": posts,
            }
        )
