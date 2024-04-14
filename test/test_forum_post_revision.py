import unittest
from unittest.mock import patch

import requests

from yellowstone.request import forum_post_revision

from .helpers import FakeResponse, make_wikidot


class TestForumPostRevision(unittest.TestCase):
    def setUp(self):
        self.wikidot = make_wikidot()

    def test_forum_post(self):
        http_response_1 = FakeResponse.from_json("forum_post_revision_1", "json")
        http_response_2 = FakeResponse.from_json("forum_post_revision_2", "json")
        http_response_3 = FakeResponse.from_json("forum_post_revision_3", "json")

        with patch.object(
            requests,
            "post",
            side_effect=[http_response_1, http_response_2, http_response_3],
        ) as mock:

            def get_revision(revision_id):
                return forum_post_revision.get(
                    site_slug="scptestwiki",
                    category_id=6196661,
                    thread_id=12639175,
                    post_id=6462360,
                    revision_id=revision_id,
                    wikidot=self.wikidot,
                )

            data = get_revision(7841563)
            self.assertEqual(data.title, "test with many revisions")
            self.assertEqual(data.content, "<p>1</p>")

            data = get_revision(7841564)
            self.assertEqual(data.title, "test with many revisions")
            self.assertEqual(data.content, "<p><strong>2</strong></p>")

            data = get_revision(7841565)
            self.assertEqual(data.title, "test with many revisions")
            self.assertEqual(data.content, "<p><em>3</em></p>")

            mock.assert_called()
