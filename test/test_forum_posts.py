import unittest
from unittest.mock import patch

import requests

from yellowstone.request import forum_posts
from yellowstone.request.forum_posts import ForumPostData

from .helpers import FakeResponse, make_wikidot


class TestForumPosts(unittest.TestCase):
    def setUp(self):
        self.wikidot = make_wikidot()

    def test_forum_posts(self):
        http_response = FakeResponse.ajax_from_file("forum_posts")
        with patch.object(requests, "post", return_value=http_response) as mock:
            models = forum_posts.get(
                "scp-wiki",
                category_id=50742,
                thread_id=76692,
                offset=1,
                wikidot=self.wikidot,
            )
            mock.assert_called_once()

        self.assertEqual(len(models), 122)
        self.assertIsInstance(models[0], ForumPostData)

        self.assertEqual(models[0].id, 326022)
        self.assertIsNone(models[0].parent)
        self.assertEqual(models[0].title, "")
        self.assertEqual(models[0].created_by.id, 247274)
        self.assertEqual(models[0].created_by.slug, "wonderful-lizard")
        self.assertEqual(models[0].created_by.name, "Wonderful Lizard")
        self.assertIn("How on Earth is there no discussion on this?", models[0].html)

        self.assertEqual(models[1].id, 328393)
        self.assertEqual(models[1].parent, 326022)
        self.assertEqual(models[1].title, "Re:")
        self.assertEqual(models[1].created_by.id, 247532)
        self.assertEqual(models[1].created_by.slug, "devas")
        self.assertEqual(models[1].created_by.name, "Devas")
        self.assertIn("Who knows?", models[1].html)
