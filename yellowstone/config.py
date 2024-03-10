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
    always_fetch_site: bool

    @staticmethod
    def from_file(path: str) -> "Config":
        with open(path, "rb") as file:
            logger.info("Reading configuration file from %s", path)
            data = tomllib.load(file)

        return Config(
            s3_bucket=data["s3"]["bucket"],
            site_slugs=data["wikidot"]["sites"],
            sites_use_tls=data["wikidot"]["use-tls"],
            sites_use_admin_members=data["wikidot"]["use-admin-members-list"],
            always_fetch_site=data["wikidot"]["always-fetch-site"],
        )

    @staticmethod
    def parse_args() -> "Config":
        logger.debug("Parsing command-line arguments")
        parser = ArgumentParser(description="The Yellowstone Wikidot backup system")
        parser.add_argument(
            "config",
            help="The path to the configuration file to use",
        )
        args = parser.parse_args()
        return Config.from_file(args.config)

    def uses_tls(self, site_slug: str) -> bool:
        return site_slug in self.sites_use_tls

    def uses_admin_members(self, site_slug: str) -> bool:
        return site_slug in self.sites_use_admin_members


def getenv(var_name) -> str:
    value = os.getenv(var_name)
    if value is None:
        raise RuntimeError(f"No value for environment variable {var_name}")
    return value
