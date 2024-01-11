"""
Parsing and storing information gathered from the configuration file.
"""

import tomllib
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
