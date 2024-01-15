"""
Parsing and storing information gathered from the configuration file.
"""

import logging
import os
import tomllib
from argparse import ArgumentParser
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class Config:
    s3_bucket: str
    site_slugs: list[str]
    sites_use_tls: list[str]
    sites_use_admin_members: list[str]

    def __init__(self, path: str) -> None:
        with open(path, "rb") as file:
            logger.info("Reading configuration file from %s", path)
            data = tomllib.load(file)

        self.s3_bucket = data["s3"]["bucket"]
        self.site_slugs = data["wikidot"]["sites"]
        self.sites_use_tls = data["wikidot"]["use-tls"]
        self.sites_use_admin_members = data["wikidot"]["use-admin-members-list"]

    @staticmethod
    def parse_args() -> "Config":
        logger.debug("Parsing command-line arguments")
        parser = ArgumentParser(description="The Yellowstone Wikidot backup system")
        parser.add_argument(
            "config",
            help="The path to the configuration file to use",
        )
        args = parser.parse_args()
        return Config(args.config)

    def uses_tls(self, site_slug: str) -> bool:
        return site_slug in self.sites_use_tls

    def uses_admin_members(self, site_slug: str) -> bool:
        return site_slug in self.sites_use_admin_members


def getenv(var_name) -> str:
    value = os.getenv(var_name)
    if not value:
        raise RuntimeError(f"No value for environment variable {var_name}")
    return value
