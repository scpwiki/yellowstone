"""
Parsing and storing information gathered from the configuration file.
"""

import tomllib
from dataclasses import dataclass


@dataclass
class Config:
    wikidot_username: str
    wikidot_api_key: str
    aws_region: str
    aws_access_key: str
    aws_secret_key: str
    s3_bucket: str
    site_slugs: list[str]

    def __init__(self, path):
        with open(path, "rb") as file:
            data = tomllib.load(file)

        self.wikidot_username = data["wikidot"]["username"]
        self.wikidot_api_key = data["wikidot"]["api-key"]
        self.aws_region = data["aws"]["region"]
        self.s3_bucket = data["aws"]["bucket"]
        self.aws_access_key = data["aws"]["access-key"]
        self.aws_secret_key = data["aws"]["secret-key"]
        self.site_slugs = data["backup"]["sites"]
