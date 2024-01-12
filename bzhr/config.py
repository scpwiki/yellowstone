"""
Parsing and storing information gathered from the configuration file.
"""

import tomllib
from argparse import ArgumentParser
from dataclasses import dataclass


@dataclass
class Config:
    s3_region: str
    s3_bucket: str
    site_slugs: list[str]

    def __init__(self, path):
        with open(path, "rb") as file:
            data = tomllib.load(file)

        self.s3_region = data["s3"]["region"]
        self.s3_bucket = data["s3"]["bucket"]
        self.site_slugs = data["wikidot"]["sites"]

    @staticmethod
    def parse_args():
        parser = ArgumentParser(description="The BZHR Wikidot backup system")
        parser.add_argument(
            "config",
            help="The path to the configuration file to use",
        )
        args = parser.parse_args()
        return Config(args.config)
