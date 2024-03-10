import unittest
from unittest.mock import patch

import requests

from yellowstone.request import forum_categories
from yellowstone.request.forum_categories import ForumGroupData

from .helpers import FakeResponse, make_wikidot


class TestForumCategories(unittest.TestCase):
    def setUp(self):
        self.wikidot = make_wikidot()

    def test_forum_categories(self):
        http_response = FakeResponse.ajax_from_file("forum_categories")
        with patch.object(requests, "post", return_value=http_response) as mock:
            models = forum_categories.get("scp-wiki", wikidot=self.wikidot)
            mock.assert_called_once()

        self.assertEqual(len(models), 8)
        self.assertIsInstance(models[0], ForumGroupData)

        self.assertEqual(models[0].name, "Site Announcements and Proposals")
        self.assertEqual(
            models[0].description,
            "Announce new pages, suggest policy, and interact with new site members.",
        )

        self.assertEqual(len(models[0].categories), 4)
        self.assertEqual(models[0].categories[0].name, "Sitewide Announcements")
        self.assertEqual(models[0].categories[0].thread_count, 190)
        self.assertEqual(models[0].categories[0].post_count, 6091)
        self.assertEqual(models[0].categories[1].name, "Page Announcements")
        self.assertEqual(models[0].categories[1].thread_count, 173)
        self.assertEqual(models[0].categories[1].post_count, 28560)

        self.assertEqual(models[1].name, "Staff Processes")
        self.assertTrue(models[1].description.startswith("Staff recruitment threads"))
        self.assertEqual(len(models[1].categories), 3)
        self.assertEqual(models[1].categories[0].name, "Staff Policy Discussions")
        self.assertEqual(models[1].categories[0].thread_count, 176)
        self.assertEqual(models[1].categories[0].post_count, 2160)
