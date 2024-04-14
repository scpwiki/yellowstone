"""
Helpers and utilities for the Yellowstone unit tests.
"""

import json
import os
from dataclasses import dataclass
from typing import Union

from yellowstone.config import Config
from yellowstone.types import Json
from yellowstone.wikidot import Wikidot

TEST_SOURCE = "[test_source]"


@dataclass
class FakeResponse:
    data: Union[dict, bytes, str]

    @staticmethod
    def from_file(filename: str, extension: str = "html") -> "FakeResponse":
        return FakeResponse(get_test_data(filename, extension))

    @staticmethod
    def from_json(filename: str, extension: str = "json") -> "FakeResponse":
        return FakeResponse(get_test_json(filename, extension))

    @staticmethod
    def ajax_from_file(filename: str, extension: str = "html") -> "FakeResponse":
        return FakeResponse(
            {
                "status": "ok",
                "CURRENT_TIMESTAMP": 1710000000,
                "body": get_test_data(filename, extension),
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

    @property
    def text(self) -> str:
        assert isinstance(self.data, str)
        return self.data

    def json(self) -> dict:
        assert isinstance(self.data, dict)
        return self.data


def get_test_data(filename: str, extension: str = "html") -> str:
    path = os.path.join(os.path.dirname(__file__), "data", f"{filename}.{extension}")
    with open(path) as file:
        return file.read()


def get_test_json(filename: str, extension: str = "json") -> Json:
    return json.loads(get_test_data(filename, extension))  # type: ignore


def make_wikidot() -> Wikidot:
    config = Config(
        s3_bucket="test",
        site_slugs=["test", "test-tls"],
        sites_use_tls=["test-tls"],
        sites_use_admin_members=[],
        always_fetch_site=True,
    )
    return Wikidot(config, username="test", api_key="test")
