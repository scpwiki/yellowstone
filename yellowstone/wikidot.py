"""
Common utilities for interfacing with Wikidot.
"""

import random
import string
from xmlrpc.client import ServerProxy

from .config import getenv

import requests


class Wikidot:
    __slots__ = ("proxy",)

    def __init__(self) -> None:
        username = getenv("WIKIDOT_USERNAME")
        api_key = getenv("WIKIDOT_API_KEY")
        self.proxy = ServerProxy(
            f"https://{username}:{api_key}@www.wikidot.com/xml-rpc-api.php",
            use_builtin_types=True,
            use_datetime=True,
        )

    def ajax_module_connector(self, site_slug: str, data: dict) -> dict:
        # Set token7
        token7 = self.generate_token7()
        data["wikidot_token7"] = token7
        cookies = requests.cookies.RequestsCookieJar()
        cookies.set(
            "wikidot_token7",
            token7,
            domain=f"{site_slug}.wikidot.com",
            path="/",
        )

        # Make HTTP request
        r = requests.post(
            f"https://{site_slug}.wikidot.com/ajax_module_connector",
            data=data,
            cookies=cookies,
        )
        r.raise_for_status()
        response = r.json()

        # Process body
        match response["status"]:
            case "ok":
                body = response["body"]
                assert isinstance(body, dict)
                return body
            case "wrong_token7":
                raise WikidotTokenError
            case status:
                raise WikidotError(status)

    @staticmethod
    def generate_token7() -> str:
        # TODO need to do fetching logic
        return "".join(random.choice(string.hexdigits) for _ in range(32))


class WikidotError(RuntimeError):
    pass


class WikidotTokenError(WikidotError):
    pass
