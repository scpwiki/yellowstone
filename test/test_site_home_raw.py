import unittest
from unittest.mock import patch

import requests

from yellowstone.request import site_home_raw
from yellowstone.request.site_home_raw import SiteHomeData

from .helpers import FakeResponse, make_wikidot


class TestSiteHomeRaw(unittest.TestCase):
    def setUp(self):
        self.wikidot = make_wikidot()

    def test_site_home(self):
        http_response = FakeResponse.from_file("site_home_raw")
        with patch.object(requests, "get", return_value=http_response) as mock:
            model = site_home_raw.get("scp-wiki", wikidot=self.wikidot)
            mock.assert_called_once()

        self.assertIsInstance(model, SiteHomeData)
        self.assertEqual(model.id, 66711)
        self.assertEqual(model.slug, "scp-wiki")
        self.assertEqual(model.name, "SCP Foundation")
        self.assertEqual(model.tagline, "Secure, Contain, Protect")
        self.assertEqual(model.language, "en")
        self.assertEqual(model.home_page_slug, "main")
        self.assertEqual(model.home_page_id, 1403571722)
        self.assertEqual(model.home_page_discussion_thread_id, 14881792)
        self.assertEqual(model.home_page_category_id, 366566)
