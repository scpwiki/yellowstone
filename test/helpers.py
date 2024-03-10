"""
Helpers and utilities for the Yellowstone unit tests.
"""

import os
from dataclasses import dataclass

TEST_SOURCE = "[test_source]"


@dataclass
class FakeResponse:
    data: dict

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

    def json(self) -> dict:
        return self.data
