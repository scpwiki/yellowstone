"""
Helpers and utilities for the Yellowstone unit tests.
"""

import os
from dataclasses import dataclass
from typing import Union

from yellowstone.config import Config
from yellowstone.wikidot import Wikidot

TEST_SOURCE = "[test_source]"


@dataclass
class FakeResponse:
    data: Union[dict, bytes, str]

    @staticmethod
    def from_file(filename: str) -> "FakeResponse":
        path = os.path.join(os.path.dirname(__file__), "data", f"{filename}.html")
        with open(path) as file:
            body = file.read()

        return FakeResponse(
            {
                "status": "ok",
                "CURRENT_TIMESTAMP": 1710000000,
                "body": body,
                "jsInclude": [],
                "cssInclude": [],
                "callbackIndex": 1,
            },
        )

    def raise_for_status(self):
        pass

    @property
    def content(self) -> Union[bytes, str]:
        assert isinstance(self.data, (bytes, str))
        return self.data

    def json(self) -> dict:
        assert isinstance(self.data, dict)
        return self.data


def make_wikidot():
    config = Config(
        s3_bucket="test",
        site_slugs=["test", "test-tls"],
        sites_use_tls=["test-tls"],
        sites_use_admin_members=[],
        always_fetch_site=True,
    )
    return Wikidot(config, username="test", api_key="test")
