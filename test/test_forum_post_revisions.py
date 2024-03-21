import unittest
from unittest.mock import patch

import requests

from yellowstone.request import forum_post_revisions

from .helpers import FakeResponse, make_wikidot


class TestForumPostRevisions(unittest.TestCase):
    def setUp(self):
        self.wikidot = make_wikidot()

    def test_forum_posts(self):
        http_response = FakeResponse.ajax_from_file("forum_post_revisions")
        with patch.object(requests, "post", return_value=http_response) as mock:
            revision_ids = forum_post_revisions.get(
                site_slug="scp-wiki",
                category_id=88827,
                thread_id=561991,
                post_id=1782850,
                wikidot=self.wikidot,
            )
            mock.assert_called_once()

        self.assertEqual(revision_ids, [7841563, 7841564, 7841565, 7841566, 7841567])
