import unittest
from unittest.mock import call, patch

import requests

from yellowstone.request import forum_posts
from yellowstone.request.forum_posts import ForumPostData

from .helpers import FakeResponse, get_test_json, make_wikidot


class TestForumPosts(unittest.TestCase):
    def setUp(self):
        self.wikidot = make_wikidot()

    def test_forum_posts(self):
        http_response = FakeResponse.ajax_from_file("forum_posts")
        api_response_1 = get_test_json("forum_posts_1")
        api_response_2 = get_test_json("forum_posts_2")

        with patch.object(requests, "post", return_value=http_response) as ajax_mock:
            with patch.object(
                self.wikidot.api,
                "posts_get",
                side_effect=[api_response_1, api_response_2],
            ) as api_mock:
                models = forum_posts.get(
                    "scp-wiki",
                    category_id=50742,
                    thread_id=76692,
                    offset=1,
                    wikidot=self.wikidot,
                )

                # calls once for the whole HTML
                ajax_mock.assert_called_once()

                # calls twice for each group of posts (chunks of 10)
                api_mock.assert_has_calls(
                    [
                        call(
                            site="scp-wiki",
                            posts=[
                                "326022",
                                "328393",
                                "1930722",
                                "2240448",
                                "2514445",
                                "2777373",
                                "3651072",
                                "3651085",
                                "6259068",
                                "4288597",
                            ],
                        ),
                    ],
                    [
                        call(
                            site="scp-wiki",
                            posts=[
                                "4688320",
                                "4725042",
                                "4767904",
                                "4783580",
                                "4809182",
                                "5089080",
                                "5159793",
                                "6144934",
                                "5520725",
                            ],
                        ),
                    ],
                )

        self.assertEqual(len(models), 19)
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
