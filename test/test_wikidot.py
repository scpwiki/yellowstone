import unittest
from unittest.mock import patch

import requests

from yellowstone.config import Config
from yellowstone.wikidot import Wikidot

from .helpers import FakeResponse


class TestWikidotClass(unittest.TestCase):
    def setUp(self):
        self.config = Config(
            s3_bucket="test",
            site_slugs=["test", "test-tls"],
            sites_use_tls=["test-tls"],
            sites_use_admin_members=[],
            always_fetch_site=True,
        )
        self.wikidot = Wikidot(self.config, username="test", api_key="test")

    def test_ajax_module_connector(self):
        http_response = FakeResponse.from_file("user_info_win")
        with patch.object(requests, "post", return_value=http_response):
            html = self.wikidot.ajax_module_connector(
                "www",
                "users/UserInfoWinModule",
                {"user_id": 4598089},
            )
            self.assertEqual(html, http_response.data["body"])

    def test_site_url(self):
        ajax_url = self.wikidot.site_url("test")
        self.assertEqual(ajax_url, "http://test.wikidot.com")

        ajax_url = self.wikidot.site_url("test-tls")
        self.assertEqual(ajax_url, "https://test-tls.wikidot.com")

    def test_ajax_url(self):
        ajax_url = self.wikidot.ajax_module_url("test")
        self.assertEqual(ajax_url, "http://test.wikidot.com/ajax-module-connector.php")

        ajax_url = self.wikidot.ajax_module_url("test-tls")
        self.assertEqual(
            ajax_url, "https://test-tls.wikidot.com/ajax-module-connector.php"
        )

    def test_generate_token7(self):
        token7 = self.wikidot.generate_token7()
        self.assertEqual(len(token7), 32)
