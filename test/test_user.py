import unittest
from unittest.mock import patch

import requests

from yellowstone.request import user
from yellowstone.request.user import UserData

from .helpers import FakeResponse, make_wikidot


class TestUser(unittest.TestCase):
    def setUp(self):
        self.wikidot = make_wikidot()

    def test_user(self):
        """Test that user data can be parsed from Wikidot HTML"""

        http_response = FakeResponse.from_file("user_info_win")
        with patch.object(requests, "post", return_value=http_response):
            model = user.get(4598089, wikidot=self.wikidot)

        self.assertIsInstance(model, UserData)
        self.assertEqual(model.id, 4598089)
        self.assertEqual(model.slug, "aismallard")
        self.assertEqual(model.name, "aismallard")
        self.assertEqual(model.gender, "female")
        self.assertIsNone(model.birthday)
        self.assertIsNone(model.location)
        self.assertIsNone(model.bio)
        self.assertEqual(model.karma, 5)
