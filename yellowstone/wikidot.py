"""
Common utilities for interfacing with Wikidot.
"""

import logging
import random
import string
from functools import cache
from xmlrpc.client import ServerProxy

import requests

from .config import Config, getenv
from .exception import WikidotError, WikidotTokenError

logger = logging.getLogger(__name__)


class Wikidot:
    __slots__ = ("proxy", "config")

    config: Config
    proxy: ServerProxy

    def __init__(self, config) -> None:
        username = getenv("WIKIDOT_USERNAME")
        api_key = getenv("WIKIDOT_API_KEY")
        self.config = config
        self.proxy = ServerProxy(
            f"https://{username}:{api_key}@www.wikidot.com/xml-rpc-api.php",
            use_builtin_types=True,
            use_datetime=True,
        )

    def ajax_module_connector(
        self,
        site_slug: str,
        module_name: str,
        data: dict,
    ) -> str:
        logger.debug("Making AJAX call for site '%s': %r", site_slug, data)

        # Set token7
        token7 = self.generate_token7()
        data["moduleName"] = module_name
        data["wikidot_token7"] = token7

        # Make HTTP request
        r = requests.post(
            self.ajax_module_url(site_slug),
            cookies={"wikidot_token7": token7},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data=data,
        )
        r.raise_for_status()
        response = r.json()

        # Process body
        match response["status"]:
            case "ok":
                body = response["body"]
                assert isinstance(body, str)
                return body
            case "wrong_token7":
                raise WikidotTokenError
            case "not_ok":
                raise WikidotError(response["message"])
            case status:
                raise WikidotError(status)

    @cache
    def site_url(self, site_slug: str) -> str:
        protocol = "https" if self.config.uses_tls(site_slug) else "http"
        return f"{protocol}://{site_slug}.wikidot.com"

    @cache
    def ajax_module_url(self, site_slug: str) -> str:
        return f"{self.site_url(site_slug)}/ajax-module-connector.php"

    @staticmethod
    def generate_token7() -> str:
        return "".join(random.choice(string.hexdigits) for _ in range(32))
