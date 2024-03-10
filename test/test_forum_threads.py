import unittest
from unittest.mock import patch

import requests

from yellowstone.request import forum_threads
from yellowstone.request.forum_threads import ForumThreadData

from .helpers import FakeResponse, make_wikidot


class TestForumThreads(unittest.TestCase):
    def setUp(self):
        self.wikidot = make_wikidot()

    def test_forum_threads(self):
        http_response = FakeResponse.ajax_from_file("forum_threads")
        with patch.object(requests, "post", return_value=http_response) as mock:
            models = forum_threads.get(
                "scp-wiki",
                category_id=50742,
                offset=1,
                wikidot=self.wikidot,
            )
            mock.assert_called_once()

        self.assertEqual(len(models), 20)
        self.assertIsInstance(models[0], ForumThreadData)

        self.assertEqual(models[0].id, 1082671)
        self.assertIn("Trying to find an SCP or Tale", models[0].title)
        self.assertIn("What the title says", models[0].description)
        self.assertTrue(models[0].sticky)
        self.assertEqual(models[0].created_by.name, "Zyn")
        self.assertEqual(models[0].post_count, 1123)

        self.assertEqual(models[2].id, 561991)
        self.assertEqual(models[2].title, "The Leak")
        self.assertEqual(models[2].description, "In-universe spoilers/info leaks")
        self.assertTrue(models[2].sticky)
        self.assertEqual(models[2].created_by.name, "Dr Gears")
