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

    def __init__(self, path) -> None:
        with open(path, "rb") as file:
            logger.info("Reading configuration file from %s", path)
            data = tomllib.load(file)

        self.s3_bucket = data["s3"]["bucket"]
        self.site_slugs = data["wikidot"]["sites"]

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


def getenv(var_name) -> str:
    value = os.getenv(var_name)
    if not value:
        raise RuntimeError(f"No value for environment variable {var_name}")
    return value
